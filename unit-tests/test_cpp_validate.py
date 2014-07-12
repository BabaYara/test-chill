import os
import pprint
import unittest

import testchill
import testchill.util
import testchill._cpp_validate_env as cpp_validate_env
import testchill.cpp_validate as cpp_validate

class TestCppValidate(unittest.TestCase):
    def setUp(self):
        self.staging_dir_wd = os.getenv("STAGING_DIR_WD")
        self.cpp_validate_dir = os.path.join(os.getcwd(),'unit-tests/cpp_validate_prog/')
        self._parse_testproc_script_test_data = [
                (('mm_one.testproc',),      None),
                (('mm_one_with.testproc',), None)
            ]
        self._parse_testproc_python_test_data = [
            ]
        self._generate_data_test_data = [
                (('mm_one.cc','in'),               None),
                (('mm_one.cc','out'),              None),
                (('mm_one_with.cc','in'),          None),
                (('mm_one_with.cc','out'),         None),
                (('mm_one_defines.cc','in'),       None),
                (('mm_one_defines.cc','out'),      None),
                (('mm_one_with_defines.cc','in'),  None),
                (('mm_one_with_defines.cc','out'), None),
            ]
        self._parse_testproc_iter_test_data = [
                (('mm_one.cc',),
                    [({'lang': 'script', 'name': 'mm_small'},)]),
                (('mm_one_with.cc',),
                    [({'lang': 'script', 'name': 'mm_small'},)]),
                (('mm_one_defines.cc',),
                    [({'lang': 'script', 'name': 'mm_small', 'define': "{'AN':3, 'BM':2, 'AMBN':5}"},)]),
                (('mm_one_with_defines.cc',),
                    [({'lang': 'script', 'name': 'mm_small', 'define': "{'AN':3, 'BM':2, 'AMBN':5}"},)])
            ]
    
    def test__get_script_parser(self):
        cpp_validate._script_parser = None
        self.assertIsNotNone(cpp_validate._get_script_parser())
        self.assertIsNotNone(cpp_validate._get_script_parser())
    
    def _test_parse_src(self, parsefunc, test_data):
        def parse_file(filename):
            path = os.path.join(self.cpp_validate_dir, filename)
            with open(path, 'r') as f:
                src = f.read()
            return parsefunc(src)
        for args, expected in test_data:
            srcfile, = args
            val = parse_file(srcfile)
            #TODO: make some assertions
    
    def test__parse_testproc_script(self):
        self._test_parse_src(
                cpp_validate._parse_testproc_script,
                self._parse_testproc_script_test_data)
    
    @unittest.skip("not yet supported")
    def test__parse_testproc_python(self):
        self._test_parse_src(
                cpp_validate._parse_testproc_python,
                self._parse_testproc_python_test_data)
    
    def test__parse_testproc_iter(self):
        def testfunc(filename):
            path = os.path.join(self.cpp_validate_dir, filename)
            testchill.util.shell('cp', [path, '.'], wd=self.staging_dir_wd)
            return list(cpp_validate._parse_testproc_iter(filename, wd=self.staging_dir_wd))
        for args, expected_list in self._parse_testproc_iter_test_data:
            val_list = testfunc(*args)
            for val, expected in zip(val_list, expected_list):
                _, attr_val = val
                attr_exp, = expected
                self.assertEqual(attr_val, attr_exp)
            #TODO: make some assertions
    
    def test__generate_data(self):
        def testfunc(filename, direction):
            path = os.path.join(self.cpp_validate_dir, filename)
            testchill.util.shell('cp', [path, '.'], wd=self.staging_dir_wd)
            for proc, attrs in cpp_validate._parse_testproc_iter(filename, wd=self.staging_dir_wd):
                defines = attrs['define']
                if defines is not None:
                    defines = eval(defines)
                yield cpp_validate._generate_data(proc, direction, filename, defines, wd=self.staging_dir_wd)
            
        for args, expected in self._generate_data_test_data:
            for filename in testfunc(*args):
                self.assertTrue(os.path.exists(filename))
            
            #TODO: make some assertions
            
        
