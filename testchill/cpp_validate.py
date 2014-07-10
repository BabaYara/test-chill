import os
import pickle

from . import util

_script_parser = None
def _get_script_parser():
    global _script_parser
    if _script_parser is None:
        with open('testchill/cpp_validate/parser.pickle','rb') as f:
            _script_parser = pickle.load(f)
    return _script_parser

def _parse_testproc_python(txt):
    glbls = dict()
    exec('import testchill._cpp_validate_env\nfrom testchill._cpp_validate_env import *', None, glbls)
    return eval(txt, glbls)

def _parse_testproc_script(txt):
    parser = _get_script_parser()
    return parser.parse(util.textstream(txt))

def _parse_testprocs(srcfile, wd=os.getcwd()):
    default_attrs = {'lang':'script'}
    for txt, parsed_attrs in util.extract_tag('test', srcfile, wd):
        attrs = dict(default_attrs)
        attrs.update(parse_attrs)
        if attrs['lang'] == 'python':
            yield parse_testproc_python(txt)
        if attrs['lang'] == 'script':
            yield parse_testproc_script(txt)

def run_from_src(control_src, test_src, test_valid=True, test_time=True, wd=os.getcwd()):
    for test_proc in parse_testprocs(control_src, wd):
       #TODO:
       #build(...,wd)
       yield None
