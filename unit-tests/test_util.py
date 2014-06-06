import os
import subprocess
import tempfile
import unittest

import testchill.util as util

### Most of these are sanity checks. ###

class TestUtil(unittest.TestCase):
    def setUp(self):
        self.tempfiles = []
    
    def maketempfiles(self, n=1):
        files = tuple([tempfile.mkstemp(text=True) for i in range(n)])
        self.tempfiles += list(map(lambda f: f[1], files))
        return files
        
    def test_shell(self):
        sbla = subprocess.check_output(['ls', '-la', 'test-cases/chill'])
        
        if util.python_version_major == 3:
            sbla = sbla.decode()
        
        shla = util.shell('ls', ['-la', 'test-cases/chill'])
        self.assertEqual(sbla, shla)
    
    def test_shell_env(self):
        env = {'STRING_VAR':'string','NUMBER_VAR':3,'DEFINED_VAR':1}
        
        self.assertEqual(util.shell('echo', ['$STRING_VAR'], env=env), env['STRING_VAR'] + '\n')
        self.assertEqual(util.shell('echo', ['$NUMBER_VAR'], env=env), str(env['NUMBER_VAR']) + '\n')
        self.assertEqual(util.shell('echo', ['$DEFINED_VAR'], env=env), str(env['DEFINED_VAR']) + '\n')
    
    def test_shell_tofile(self):
        tfile = self.maketempfiles(1)
        fname = tfile[0][1]
        
        with open(fname, 'w') as f:
            util.shell('ls', ['-la', 'test-cases/chill'], stdout=f)
        with open(fname, 'r') as f:
            self.assertEqual(util.shell('ls', ['-la', 'test-cases/chill']), f.read())
    
    def test_copy(self):
        class C(object):
            pass
        c = C()
        c.x = 'x'
        a = util.copy(c)
        b = util.copy(c)
        a.x = 'y'
        self.assertEqual(c.x,'x')
        self.assertEqual(b.x,'x')
        self.assertEqual(a.x,'y')
    
    def test_callonce(self):
        def foo():
            return 3
        foo_once = util.callonce(foo)
        self.assertEqual(foo_once(), 3)
        self.assertRaises(Exception, foo_once)
    
    def tearDown(self):
        for f in self.tempfiles:
            os.remove(f)
    

