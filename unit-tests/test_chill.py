import logging
import os
import unittest

import testchill.chill
import testchill.test
import testchill.util


_runbuild=True

def runtest(tclist):
    for tc in tclist:
        tc.setUp()
        tc.run()
        tc.tearDown()

def runchilltest(tclist):
    for tc in tclist:
        tc.setUp()
        tc.compile_src(tc)
        tc.run_script(tc)
        tc.compile_gensrc(tc)
        tc.tearDown()

class TestChillTestCases(unittest.TestCase):
    def setUp(self):
        self.chill_dev_dir = os.getenv('CHILL_DEV_SRC')
        self.chill_rel_dir = os.getenv('CHILL_RELEASE_SRC')
        self.omega_dev_dir = os.getenv('OMEGA_DEV_SRC')
        self.omega_rel_dir = os.getenv('OMEGA_RELEASE_SRC')
        self.bin_dir = os.getenv('STAGING_DIR_BIN')
        self.wd = os.getenv('STAGING_DIR_WD')
    
    def tearDown(self):
        pass
    
    def test_chill_dev(self):
        tc = testchill.chill.BuildChillTestCase(self.chill_dev_dir, self.omega_dev_dir, bin_dir=self.bin_dir)
        self.assertEqual(tc.config.name(), 'chill')
        self.assertEqual(tc.config.env()['OMEGAHOME'], self.omega_dev_dir)
        self.assertEqual(tc.config.make_depend_target(), 'depend-chill')
        self.assertEqual(tc.config.make_target(), 'chill')
        self.assertEqual(tc.name, 'chill')
        logging.info('Building ' + tc.name)
        if _runbuild:
            runtest([tc])
    
    def test_chill_dev_lua(self):
        tc = testchill.chill.BuildChillTestCase(self.chill_dev_dir, self.omega_dev_dir, bin_dir=self.bin_dir, script_lang='lua')
        self.assertEqual(tc.config.name(), 'chill-lua')
        self.assertEqual(tc.config.env()['OMEGAHOME'], self.omega_dev_dir)
        self.assertEqual(tc.config.make_depend_target(), 'depend-chill')
        self.assertEqual(tc.config.make_target(), 'chill')
        self.assertEqual(tc.config.make_args(), 'SCRIPT_LANG=lua')
        self.assertEqual(tc.name, 'chill-lua')
        logging.info('Building ' + tc.name)
        if _runbuild:
            runtest([tc])
    
    def test_chill_dev_python(self):
        tc = testchill.chill.BuildChillTestCase(self.chill_dev_dir, self.omega_dev_dir, bin_dir=self.bin_dir, script_lang='python')
        self.assertEqual(tc.config.name(), 'chill-python')
        self.assertEqual(tc.config.env()['OMEGAHOME'], self.omega_dev_dir)
        self.assertEqual(tc.config.make_depend_target(), 'depend-chill')
        self.assertEqual(tc.config.make_target(), 'chill')
        self.assertEqual(tc.config.make_args(), 'SCRIPT_LANG=python')
        self.assertEqual(tc.name, 'chill-python')
        logging.info('Building ' + tc.name)
        if _runbuild:
            runtest([tc])
    
    def test_cudachill_dev(self):
        tc = testchill.chill.BuildChillTestCase(self.chill_dev_dir, self.omega_dev_dir, bin_dir=self.bin_dir, build_cuda=True)
        self.assertEqual(tc.config.name(), 'cuda-chill')
        self.assertEqual(tc.config.env()['OMEGAHOME'], self.omega_dev_dir)
        self.assertEqual(tc.config.make_depend_target(), 'depend-cuda-chill')
        self.assertEqual(tc.config.make_target(), 'cuda-chill')
        self.assertEqual(tc.name, 'cuda-chill')
        logging.info('Building ' + tc.name)
        if _runbuild:
            runtest([tc])
    
    def test_cudachill_dev(self):
        tc = testchill.chill.BuildChillTestCase(self.chill_dev_dir, self.omega_dev_dir, bin_dir=self.bin_dir, build_cuda=True, script_lang='python')
        self.assertEqual(tc.config.name(), 'cuda-chill-python')
        self.assertEqual(tc.config.env()['OMEGAHOME'], self.omega_dev_dir)
        self.assertEqual(tc.config.make_depend_target(), 'depend-cuda-chill')
        self.assertEqual(tc.config.make_target(), 'cuda-chill')
        self.assertEqual(tc.name, 'cuda-chill-python')
        logging.info('Building ' + tc.name)
        if _runbuild:
            runtest([tc])

    def test_chill_release(self):
        tc = testchill.chill.BuildChillTestCase(self.chill_rel_dir, self.omega_rel_dir, bin_dir=self.bin_dir, version='release')
        self.assertEqual(tc.config.name(), 'chill-release')
        self.assertEqual(tc.config.env()['OMEGAHOME'], self.omega_rel_dir)
        self.assertEqual(tc.config.make_depend_target(), 'depend')
        self.assertEqual(tc.config.make_target(), 'chill')
        self.assertEqual(tc.name, 'chill-release')
        logging.info('Building ' + tc.name)
        if _runbuild:
            runtest([tc])
    
    def test_cudachill_release(self):
        tc = testchill.chill.BuildChillTestCase(self.chill_rel_dir, self.omega_rel_dir, build_cuda=True, version='release')
        self.assertEqual(tc.config.name(), 'cuda-chill-release')
        self.assertEqual(tc.config.env()['OMEGAHOME'], self.omega_rel_dir)
        self.assertEqual(tc.config.env()['CUDACHILL'], 'true')
        self.assertEqual(tc.config.make_depend_target(), 'depend-cuda-chill')
        self.assertEqual(tc.config.make_target(), 'cuda-chill')
        self.assertEqual(tc.name, 'cuda-chill-release')
        logging.info('Building ' + tc.name)
        if _runbuild:
            runtest([tc])
    
    def test_run_chill(self):
        tc = testchill.chill.RunChillTestCase(self.bin_dir, 'test-cases/chill/test_scale.script', 'test-cases/chill/mm.c', wd=self.wd)
        self.assertEqual(tc.chill_src, 'mm.c')
        self.assertEqual(tc.chill_script, 'test_scale.script')
        self.assertEqual(tc.chill_src_path, os.path.join(os.getcwd(), 'test-cases/chill/mm.c'))
        self.assertEqual(tc.chill_script_path, os.path.join(os.getcwd(), 'test-cases/chill/test_scale.script'))
        self.assertEqual(tc.chill_gensrc, 'rose_mm.c')
        self.assertEqual(tc.name, 'chill:test_scale.script')
        runchilltest([tc])

