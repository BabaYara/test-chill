import ast
import unittest

import testchill._extract

class TestExtraction(unittest.TestCase):
    def setUp(self):
        self.test_extract_data = [
            ]
        self.test__commented_data = [
                (('no comment here','cc'), []),
                (('one comment //xxx\n','cc'), ['xxx']),
                (('two comments //xxx\nunrelated//yyy\n', 'cc'), ['xxx','yyy']),
                (('two comments //xxx\nunrelated//yyy', 'cc'), ['xxx','yyy']),
                (('ss/*x\ny\n*/z','cc'),['x\ny\n']),
                (('ss/*x\ny\n*/z//q\nc','cc'),['x\ny\n','q']),
                (('ss###x#\n','py'),['x#']),
                (('ss"""x"""\n','py'),['x'])
            ]
    
    def test__commented(self):
        def run(txt, ext):
            return list(testchill._extract._TagExtractor._commented(txt, ext))
        for args, res in self.test__commented_data:
            self.assertEqual(run(*args), res)
        print(__file__)
    
    def test_extract(self):
        #def run(txt, filename, ext):
        #    return _TagExtractor.extract_tag(txt, filename, ext)
        for args, res in self.test_extract_data:
            self.assertEqual(run(*args), res)
    
        
