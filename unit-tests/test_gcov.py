import pprint
import os
import unittest

import testchill.util as util
import testchill.gcov as gcov


class TestGCov(unittest.TestCase):
    def setUp(self):
        self.cprog_dir = os.path.join(os.getcwd(), 'unit-tests/cprog')
        self.cprog_bin = os.path.join(self.cprog_dir, 'sorter')
    
    def build_prog(self):
        self.clean_prog()
        util.shell('make', [], wd=self.cprog_dir)
    
    def clean_prog(self):
        util.shell('make', ['clean'], wd=self.cprog_dir)
    
    def run_prog(self, alg, lst):
        util.shell(self.cprog_bin, [alg] + list(map(str,lst)))
    
    def test_Gcov_parse(self):
        self.build_prog()
        self.run_prog('quicksort', [9, 4, 10, 6, 11, 0, 3, 7, 2, 1, 8, 5])
        g = gcov.Gcov.parse(self.cprog_dir, 'unsorted')
        self.build_prog()
        self.run_prog('quicksort', [5, 4, 3, 2, 1])
        g.merge(gcov.Gcov.parse(self.cprog_dir, 'reverse'))
        pprint.pprint(vars(g.files['QuickSorter.cc']))
    
    def tearDown(self):
        self.clean_prog()
        
