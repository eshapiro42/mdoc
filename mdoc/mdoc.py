from __future__ import print_function
from pathlib import Path
import argparse
import json
import re
import textwrap

class MDocError(Exception):
    pass

class MDoc(object):

    def __init__(self, input_path=None, input_str=None, variables={}, showvariables=False, static=False, path=None):
        self.showvariables = showvariables
        self.variables = variables
        if input_path is not None:
            # Convert the path to a Path object. If it already is, this does nothing
            self.input_path = Path(input_path)
            # Read the input file into self.input
            self.read()
        elif input_str is not None:
            self.input = input_str
            self.input_path = path
        else:
            raise MDocError('MDoc constructors must specify either an input path or an input string')
        self.parsed = self.input
        # Delete any blank lines at the end
        try:
            while self.parsed[-1] == '\n':
                self.parsed = self.parsed[:-1]
        except IndexError:
            pass
        if not static:
            # Parse the input into self.parsed
            self.parse(showvariables)

    # {mdoc snip read}
    def read(self):
        with self.input_path.open() as f:
            self.input = f.read()
    # {mdoc unsnip read}

    def parse(self, showvariables=False):
        if not showvariables:
            self.parse_variables()
        else:
            self.find_variables()
        self.parse_evals()
        # Snippets and includes must be parsed last in order for static to work
        self.parse_snippets()
        self.parse_includes()

    def parse_variables(self):
        variable_regex = re.compile('{mdoc (?!include)(?!snippet)(?!snip)(?!unsnip)(?!eval)(.*?)}')
        self.parsed = re.sub(variable_regex, self.sub_variable, self.parsed)

    def parse_includes(self):
        include_regex = re.compile('{mdoc include (.*?)(static)?}')
        self.parsed = re.sub(include_regex, self.sub_include, self.parsed)

    def parse_snippets(self):
        snippet_regex = re.compile('{mdoc snippet (.*?) from (.*?)(static)?}')
        self.parsed = re.sub(snippet_regex, self.sub_snippet, self.parsed)

    def parse_evals(self):
        eval_regex = re.compile('{mdoc eval (.*?)}')
        self.parsed = re.sub(eval_regex, self.sub_eval, self.parsed)

    def sub_variable(self, match):
        variable_str = match.group(1).strip()
        if not variable_str in self.variables:
            raise MDocError('The variable {0} was not defined but was requested by {1}'.format(variable_str, self.input_path))
        return self.variables[variable_str]

    def sub_include(self, match):
        include_path = Path(match.group(1).strip())
        if not include_path.is_absolute():
            include_path = self.input_path.parent.joinpath(include_path)
        if match.group(2) is not None: # Static include
            try:
                with include_path.open() as f:
                    include_str = f.read()
            except IOError:
                raise MDocError('The include file {0} was not found but was requested by {1}'.format(include_path, self.input_path))
            ret = include_str
        else: # Non-static include
            try:
                include_mdoc = MDoc(input_path=include_path, variables=self.variables, showvariables=self.showvariables)
            except IOError:
                raise MDocError('The include file {0} was not found but was requested by {1}'.format(include_path, self.input_path))
            except RuntimeError:
                raise MDocError('The include file {0} tried to include a file which led to infinite recursion'.format(include_path))
            ret = include_mdoc.parsed
        return ret

    def sub_snippet(self, match):
        snippet_name = match.group(1).strip()
        include_path = Path(match.group(2).strip())
        if not include_path.is_absolute():
            include_path = self.input_path.parent.joinpath(include_path)
        snip_regex = re.compile('{{mdoc snip {}}}'.format(snippet_name))
        unsnip_regex = re.compile('{{mdoc unsnip {}}}'.format(snippet_name))
        # Read in the file
        with Path(include_path).open() as f:
            f_str = f.read()
        # Look for the snip and unsnip tags and get their indices
        snip_match = re.search(snip_regex, f_str)
        unsnip_match = re.search(unsnip_regex, f_str)
        if snip_match is None:
            raise MDocError('The snippet {0} was not found in {1} but was requested by {2}'.format(snippet_name, include_path, self.input_path))
        if unsnip_match is None:
            raise MDocError('The snippet {0} was never closed in {1}'.format(snippet_name, include_path))
        snip_idx = snip_match.end() + 1
        unsnip_idx = unsnip_match.start()
        # Slice the file at these indices
        snippet_contents = f_str[snip_idx:unsnip_idx]
        # Look for the last new line and chop off everything after it
        last_newline_idx = snippet_contents.rfind('\n')
        snippet_contents = snippet_contents[:last_newline_idx]
        # Remove any shared leading indents
        snippet_contents = textwrap.dedent(snippet_contents)
        if match.group(3) is not None: # Static include
            ret = snippet_contents
        else: # Non-static include
            try:
                snippet_mdoc = MDoc(input_str=snippet_contents, variables=self.variables, showvariables=self.showvariables, path=include_path)
            except RuntimeError:
                raise MDocError('The include file {0} tried to include a file which led to infinite recursion'.format(include_path))
            ret = snippet_mdoc.parsed
        return ret

    def sub_eval(self, match):
        eval_str = match.group(1).strip()
        return str(eval(eval_str))

    def find_variables(self):
        variable_regex = re.compile('{mdoc (?!include)(?!snippet)(?!snip)(?!unsnip)(?!eval)(.*?)}')
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
        output_file.touch()
        with output_file.open(mode='w') as f:
            f.write(mdoc.parsed)
