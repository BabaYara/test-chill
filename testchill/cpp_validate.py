import os

from . import util

def parse_testproc_python(txt):
    glb = dict()
    exec('import testchill._cpp_validate_env\nfrom testchill._cpp_validate_env import *', glb)
    return eval(txt, glb)

def parse_testprocs(srcfile, wd=os.getcwd()):
    default_attrs = {'lang':'python'}
    for txt, parsed_attrs in util.extract_tag('test', srcfile, wd):
        attrs = dict(default_attrs)
        attrs.update(parse_attrs)
        if attrs['lang'] == 'python':
            yield parse_testproc_python(txt)

def run_from_src(control_src, test_src, test_valid=True, test_time=True, wd=os.getcwd()):
    for test_proc in parse_testprocs(control_src, wd):
       #TODO:
       #build(...,wd)
       yield None
