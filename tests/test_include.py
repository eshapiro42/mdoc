import os
import json
from mdoc import *

def boilerplate(testnum, vars={}):
    include_graph = {}
    # Generate an mdoc based on the main.txt file in the relevant directory
    generated = MDoc('test_include/{0}/main.txt'.format(testnum), variables=vars)
    # Read in the expected result
    with open('test_include/{0}/expected.txt'.format(testnum), 'r') as f:
        expected = f.read()
    # Check that they are the same
    assert generated.parsed == expected

def test_include_1():
    '''Test that we can include a file at all'''
    boilerplate(1)

def test_include_2():
    '''Test that we can include files which include other files'''
    boilerplate(2)

def test_include_3():
    '''Test that we can include multiple files'''
    boilerplate(3)

def test_include_4():
    '''Test that we can statically include files'''
    boilerplate(4)

def test_include_5():
    '''Test that we can include files which statically include other files'''
    boilerplate(5)

def test_include_6():
    '''Test that we can statically include multiple files'''
    boilerplate(6)

def test_include_7():
    '''Test that we can include files which use mdoc variables'''
    with open('test_include/7/vars.json', 'r') as f:
        vars = json.load(f)
    boilerplate(7, vars)

def test_include_8():
    '''Test that we can include files which use mdoc evals'''
    boilerplate(8)

def test_include_9():
    '''Test that a file trying to include itself will raise an exception'''
    try:
        MDoc('test_include/9/main.txt')
    except MDocError:
        raised = True
    else:
        raised = False
    assert raised

def test_include_10():
    '''Test that if A includes B and B includes A, an exception is raised'''
    try:
        MDoc('test_include/10/main.txt')
    except MDocError:
        raised = True
    else:
        raised = False
    assert raised
