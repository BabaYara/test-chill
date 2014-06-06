#TODO: move omega_dir, bin_dir, chill_dir, ... to ChillConfig
#TODO: highlight test implementation hooks

import os
import os.path

from . import test
from . import util


class ChillConfig(object):
    _config_map = dict(('-'.join(map(str,k)),v) for k,v in [
            (('dev',False,'script'),     ('chill',              'depend-chill',      'chill',      '')),
            (('dev',False,'lua'),        ('chill-lua',          'depend-chill',      'chill',      'SCRIPT_LANG=lua')),
            (('dev',False,'python'),     ('chill-python',       'depend-chill',      'chill',      'SCRIPT_LANG=python')),
            (('dev',True,'lua'),         ('cuda-chill',         'depend-cuda-chill', 'cuda-chill', '')),
            (('dev',True,'python'),      ('cuda-chill-python',  'depend-cuda-chill', 'cuda-chill', 'SCRIPT_LANG=python')),
            (('release',False,'script'), ('chill-release',      'depend',            'chill',      '')),
            (('release',True,'lua'),     ('cuda-chill-release', 'depend-cuda-chill', 'cuda-chill', ''))
        ])
    
    def __init__(self, omega_dir=None, build_cuda=False, script_lang=None, version='dev'):
        self.version = version
        self.build_cuda = build_cuda
        self.script_lang = script_lang if script_lang != None else self.default_script_lang()
        self.omega_dir = omega_dir
    
    def _get(self, index):
        return ChillConfig._config_map[self.version + '-' + str(self.build_cuda) + '-' + self.script_lang][index]
    
    def default_script_lang(self):
        if self.build_cuda:
            return 'lua'
        else:
            return 'script'
    
    def name(self):
        return self._get(0)
    
    def make_depend_target(self):
        return self._get(1)
    
    def make_target(self):
        return self._get(2)
    
    def make_args(self):
        return self._get(3)
    
    def env(self):
        chill_env = {'OMEGAHOME':self.omega_dir}
        if self.version == 'release' and self.build_cuda:
            chill_env['CUDACHILL']='true'
        return chill_env
    
    def make_build_testcase(self, chill_dir, bin_dir=None):
        return BuildChillTestCase(chill_dir, self.omega_dir, self.build_cuda, self.script_lang, self.version, bin_dir)
    
    @staticmethod
    def ext_to_script_lang(ext):
        return {'script':'script', 'lua':'lua', 'py':'python'}[ext]
    
    @staticmethod
    def configs_by_version(omega_dir, version):
        if version == 'dev':
            yield ChillConfig(omega_dir, False, 'script', version)
            yield ChillConfig(omega_dir, False, 'lua', version)
            yield ChillConfig(omega_dir, False, 'python', version)
            yield ChillConfig(omega_dir, True, 'lua', version)
            yield ChillConfig(omega_dir, True, 'python', version)
        else:
            yield ChillConfig(omega_dir, False, 'script', version)
            yield ChillConfig(omega_dir, True, 'lua', version)


# -                               - #
# -  Test case for building chill - #
# -                               - #
class BuildChillTestCase(test.TestCase):
    """
    Test case for building chill.
    """
    def __init__(self, chill_dir, omega_dir, build_cuda=False, script_lang=None, version='dev', bin_dir=None):
        """
        @param chill_dir The chill home directory.
        @param omega_dir The omeag home directory (OMEGAHOME).
        @param build_cuda True if building any varient of cuda-chill
        @param script_lang The interface scripting language. Defaults to script for chill and lua for cuda-chill if not specified.
        @param version The branch version (release or dev)
        @param bin_dir If the binary file is successfully compiled, this is where it will be moved to.
        """
        super(BuildChillTestCase,self).__init__(ChillConfig(omega_dir, build_cuda, script_lang, version).name())
        self.chill_dir = chill_dir
        self.config = ChillConfig(omega_dir, build_cuda, script_lang, version)
        self.bin_dir = bin_dir
    
    def setUp(self):
        util.shell('make clean', wd=self.chill_dir)
        util.shell('make veryclean', wd=self.chill_dir)
    
    def run(self):
        env = self.config.env()
        buildargs = self.config.make_args()
        depend_target = self.config.make_depend_target()
        target = self.config.make_target()
        util.shell('make', [depend_target] + [buildargs], env=env, wd=self.chill_dir)
        util.shell('make', [target] + [buildargs], env=env, wd=self.chill_dir)
        self.maybe_movebin()
    
    def tearDown(self):
        '''
        There is currently nothing to do here.
        '''
        pass
    
    def maybe_movebin(self):
        if self.bin_dir:
            util.shell('mv', [os.path.join(self.chill_dir, self.config.make_target()), os.path.join(self.bin_dir, self.config.name())])


# -                              - #
# -  Test case for running chill - #
# -                              - #
class RunChillTestCase(test.SequencialTestCase):
    """
    Test case for running and testing chill.
    """
    
    default_options={
            'compile-src':True,              # Compile original source file
            'run-script':True,               # Run chill script
            'compile-gensrc':True,           # Compile generated source file
            'check-run-script-stdout':False, # Diff stdout from run_script() against an expected value (from a .stdout file)
            
            'fail-compile-src':False,        # Expect compile_src to fail (TODO: not implemented)
            'fail-run-script':False,         # Expect run_script to fail  (TODO: not implemented)
        }
    
    def __init__(self, chill_bin_dir, chill_script, chill_src, build_cuda=False, chill_version='dev', script_lang=None, wd=None, options={}):
        """
        @param chill_bin_dir Where to look for the chill binary.
        @param chill_script The path to the chill script.
        @param chill_src The path to the source file that the script uses.
        @param build_cuda True for cuda-chill
        @param chill_version One of release or dev (development)
        @param script_lang One of script, lua, or python. If not specified, the extension of the script file will be used.
        @param wd The working directory. Where the script will be executed, compiled, and tested.
        @param options Additional testing options.
        """
        if script_lang == None:
            script_lang = ChillConfig.ext_to_script_lang(chill_script.split('.')[-1])
        
        self.config = ChillConfig(None, build_cuda, script_lang, chill_version)
        self.chill_bin_dir = os.path.abspath(chill_bin_dir)
        self.chill_src_path = os.path.abspath(chill_src)
        self.chill_script_path = os.path.abspath(chill_script)
        self.wd = wd if (wd != None) else os.getcwd()
         
        super(RunChillTestCase,self).__init__(self.config.name() + ':' + os.path.basename(chill_script))
        
        self.chill_bin = os.path.join(self.chill_bin_dir, self.config.name())
        self.chill_src = os.path.basename(self.chill_src_path)
        self.chill_script = os.path.basename(self.chill_script_path)
        self.chill_gensrc = self._get_gensrc(self.chill_src)
        self._set_options(options)

    def _set_options(self, options):
        self.options = dict(RunChillTestCase.default_options)
        self.options.update(options)
        
        self.out = dict()
        self.expected = dict()
        
        if self.options.get('compile-src'):
            self.add_subtest('compile-src', self.compile_src)
        if self.options.get('run-script'):
            self.add_subtest('run-script', self.run_script)
        if self.options.get('compile-gensrc'):
            self.add_subtest('compile-generated-src', self.compile_gensrc)
        if self.options.get('check-run-script-stdout'):
            self.add_subtest('check-run-script-stdout', self.check_run_script_stdout)
            with open('.'.join(self.chill_script_path.split('.')[0:-1] + ['stdout']), 'r') as f:
                self.expected['run_script.stdout'] = f.read()
    
    def _get_gensrc(self, src):
        """
        The name of the generated source file.
        """
        if not self.config.build_cuda:
            return 'rose_' + src
        else:
            return 'rose_' + '.'.join(src.split('.')[0:-1]) + '.cu'
    
    def setUp(self):
        """
        Called before any tests are performed. Moves source and script files into the working directory.
        """
        util.shell('cp', [self.chill_src_path, self.chill_src], wd=self.wd)
        util.shell('cp', [self.chill_script_path, self.chill_script], wd=self.wd)
        #TODO: check for chill binary
    
    def tearDown(self):
        """
        Called when the test is complete
        """
        util.shell('rm', ['-f', self.chill_src], wd=self.wd)
        util.shell('rm', ['-f', self.chill_script], wd=self.wd)
        util.shell('rm', ['-f', self.chill_gensrc], wd=self.wd)
    
    def compile_src(self, tc):
        """
        Attempts to compile the source file before any transformation is performed. Fails if gcc fails.
        """
        self.out['compile_src.stdout'] = util.shell('gcc', ['-c', self.chill_src], wd=self.wd)
    
    def run_script(self, tc):
        """
        Attempts to run the script file. Fails if chill exits with a non-zero result.
        """
        self.out['run_script.stdout'] = util.shell(self.chill_bin, [self.chill_script], wd=self.wd)
    
    def compile_gensrc(self, tc):
        """
        Attempts to compile the generated source file. Fails if gcc fails.
        """
        self.out['compile_gensrc.stdout'] = util.shell('gcc', ['-c', self.chill_gensrc], wd=self.wd)
    
    def check_run_script_stdout(self, tc):
        """
        Diff stdout from run_script against an expected stdout
        """
        isdiff, diff = util.isdiff(self.out['run_script.stdout'], self.expected['run_script.stdout'])
        if isdiff:
            return test.TestResult.make_fail(test.FailedTestResult, tc, reason='Diff:\n' + diff)
    
