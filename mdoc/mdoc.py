from __future__ import print_function
from pathlib import Path
import argparse
import json
import re
import textwrap

class MDoc(object):

    def __init__(self, input_path=None, input_str=None, variables={}, showvariables=False, static=False):
        self.showvariables = showvariables
        self.variables = variables
        if input_path is not None:
            # Convert the path to a Path object. If it already is, this does nothing
            self.input_path = Path(input_path)
            # Read the input file into self.input
            self.read()
        elif input_str is not None:
            self.input = input_str
            self.input_path = None
        else:
            raise ValueError('MDoc constructors must specify either an input path or an input string')
        self.parsed = self.input
        # Delete any blank lines at the end
        while self.parsed[-1] == '\n':
            self.parsed = self.parsed[:-1]
        if not static:
            # Parse the input into self.parsed
            self.parse(showvariables)

    # {mdoc tag read}
    def read(self):
        with self.input_path.open() as f:
            self.input = f.read()
    # {mdoc untag read}

    def parse(self, showvariables=False):
        if not showvariables:
            self.parse_variables()
        else:
            self.find_variables()
        self.parse_tag_includes()
        self.parse_includes()
        self.parse_evals()

    def parse_variables(self):
        variable_regex = re.compile('{mdoc (?!include)(?!eval)(.*?)}')
        self.parsed = re.sub(variable_regex, self.sub_variable, self.parsed)

    def parse_includes(self):
        include_regex = re.compile('{mdoc include (?!tag)(.*?)(static)?}')
        self.parsed = re.sub(include_regex, self.sub_include, self.parsed)

    def parse_tag_includes(self):
        tag_include_regex = re.compile('{mdoc include tag (.*?) from (.*?)(static)?}')
        self.parsed = re.sub(tag_include_regex, self.sub_tag_include, self.parsed)

    def parse_evals(self):
        eval_regex = re.compile('{mdoc eval (.*?)}')
        self.parsed = re.sub(eval_regex, self.sub_eval, self.parsed)

    def sub_variable(self, match):
        variable_str = match.group(1).strip()
        if not variable_str in self.variables:
            raise LookupError('The variable {0} was not defined but was requested by {1}'.format(variable_str, self.input_path))
        return self.variables[variable_str]

    def sub_include(self, match):
        include_path = match.group(1).strip()
        if match.group(2) is not None:
            try:
                with Path(include_path).open() as f:
                    include_str = f.read()
            except IOError:
                raise LookupError('The include file {0} was not found but was requested by {1}'.format(include_path, self.input_path))
            ret = include_str
        else:
            try:
                include_mdoc = MDoc(input_path=include_path, variables=self.variables, showvariables=self.showvariables)
            except IOError:
                raise LookupError('The include file {0} was not found but was requested by {1}'.format(include_path, self.input_path))
            ret = include_mdoc.parsed
        return ret

    def sub_tag_include(self, match):
        tag_str = match.group(1).strip()
        include_path = Path(match.group(2).strip())
        tag_regex = re.compile('{{mdoc tag {}}}'.format(tag_str))
        untag_regex = re.compile('{{mdoc untag {}}}'.format(tag_str))
        # Read in the file
        with Path(include_path).open() as f:
            f_str = f.read()
        # Look for the tag and untag and get their indices
        tag_match = re.search(tag_regex, f_str)
        untag_match = re.search(untag_regex, f_str)
        if tag_match is None:
            raise LookupError('The tag {0} was not found in {1} but was requested by {2}'.format(tag_str, include_path, self.input_path))
        if untag_match is None:
            raise LookupError('The tag {0} was never closed in {1}'.format(tag_str, include_path))
        tag_idx = tag_match.end() + 1
        untag_idx = untag_match.start()
        # Slice the file at these indices
        tag_contents = f_str[tag_idx:untag_idx]
        # Look for the last new line and chop off everything after it
        last_newline_idx = tag_contents.rfind('\n')
        tag_contents = tag_contents[:last_newline_idx]
        # Remove any shared leading indents
        tag_contents = textwrap.dedent(tag_contents)
        if match.group(3) is not None:
            ret = tag_contents
        else:
            tag_mdoc = MDoc(input_str=tag_contents, variables=self.variables, showvariables=self.showvariables)
            tag_mdoc.input_path = include_path
            ret = tag_mdoc.parsed
        return ret

    def sub_eval(self, match):
        eval_str = match.group(1).strip()
        return str(eval(eval_str))

    def find_variables(self):
        variable_regex = re.compile('{mdoc (?!include)(?!eval)(.*?)}')
        var_list = re.findall(variable_regex, self.parsed)
        for var in var_list:
            self.variables[var] = ''
        self.parsed = json.dumps(self.variables, indent=2)

def get_files():
    parser = argparse.ArgumentParser()
    # Command line arguments
    parser.add_argument('--input', '-i', required=True, help='Input file')
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument('--output', '-o', help='Output file')
    output_group.add_argument('--dryrun', '-d', action='store_true', help='Print output to the screen only')
    output_group.add_argument('--showvariables', '-s', action='store_true', help='Print out only which variables are referenced')
    parser.add_argument('--variables', '-v', help='JSON file containing variable definitions')
    args = parser.parse_args()
    # Get input file name
    input_file = Path(args.input)
    # Get output file name
    if args.output:
        output_file = Path(args.output)
    elif args.dryrun:
        output_file = -1
    elif args.showvariables:
        output_file = -2
    if args.variables:
        with open(args.variables, 'r') as f:
            variables = json.load(f)
    else:
        variables = {}
    return input_file, output_file, variables

def console():
    input_file, output_file, variables = get_files()
    if output_file == -2:
        showvariables = True
    else:
        showvariables = False
    mdoc = MDoc(input_path=input_file, variables=variables, showvariables=showvariables)
    if output_file is -1 or output_file == -2:
        print(mdoc.parsed)
    else:
        with open(output_file, 'w') as f:
            f.write(mdoc.parsed)
