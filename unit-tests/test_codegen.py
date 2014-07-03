import unittest

import testchill.codegen

class TestTestCodeGenerator(unittest.TestCase):
    def test__commented_lines(self):
        def run(txt, ext):
            return list(testchill.codegen.TestCodeGenerator._commented_lines(txt, ext))
        test_set = [
                (('no comment here','cc'), []),
                (('one comment //xxx\n','cc'), ['xxx']),
                (('ss/*x\ny\n*/z','cc'),['x','y']),
                (('ss###x#\n','py'),['x#']),
                (('ss"""x"""\n','py'),['x'])
            ]
        for args, res in test_set:
            self.assertEqual(run(*args), res)
    
    def test__parse(self):
        def run(txt, ext):
            return testchill.codegen.TestCodeGenerator._parse(txt, ext)
        test_set = [
                (('/*<test>\nNone\n</test>*/\n','cc'), None)
            ]
        for args, res in test_set:
            self.assertEqual(run(*args), res)
        
