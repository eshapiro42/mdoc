import os
import json
from mdoc import *

def boilerplate(testnum, vars={}):
    include_graph = {}
    # Generate an mdoc based on the main.txt file in the relevant directory
    generated = MDoc('test_snippet/{0}/main.txt'.format(testnum), variables=vars)
    # Read in the expected result
    with open('test_snippet/{0}/expected.txt'.format(testnum), 'r') as f:
        expected = f.read()
    # Check that they are the same
    assert generated.parsed == expected

def test_snippet_1():
    '''Test that we can include a snippet at all'''
    boilerplate(1)

def test_snippet_2():
    '''Test that we can include snippets which include other files'''
    boilerplate(2)

# def test_snippet_3():
#     '''Test that we can include snippets which include other snippets'''
#     boilerplate(3)
#
# def test_snippet_4():
#     '''Test that we can include multiple snippets'''
#     boilerplate(4)
#
# def test_snippet_5():
#     '''Test that we can statically include snippets'''
#     boilerplate(5)
#
# def test_snippet_6():
#     '''Test that we can include snippets which statically include other files'''
#     boilerplate(6)
#
# def test_snippet_7():
#     '''Test that we can include snippets which statically include other snippets'''
#     boilerplate(7)
#
# def test_snippet_8():
#     '''Test that we can statically include multiple snippets'''
#     boilerplate(8)
#
# def test_snippet_9():
#     '''Test that we can include snippets which use mdoc variables'''
#     with open('test_include/9/vars.json', 'r') as f:
#         vars = json.load(f)
#     boilerplate(9, vars)
#
# def test_snippet_10():
#     '''Test that we can include snippets which use mdoc evals'''
#     boilerplate(10)
#
# def test_snippet_11():
#     '''Test that we can include snippets from comment snips'''
#     boilerplate(11)
