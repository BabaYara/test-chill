import collections
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

def _parse_testproc_python(txt, glbls=None):
    if glbls is None:
        glbls = dict()
    exec('import testchill._cpp_validate_env\nfrom testchill._cpp_validate_env import *', None, glbls)
    return eval(txt, glbls)

def _parse_testproc_script(txt, glbls=None):
    parser = _get_script_parser()
    proc = list(parser.parse(util.textstream(txt)))[0]
    if glbls is None:
        from . import _cpp_validate_env
        glbls = dict()
        return _cpp_validate_env.addbindings(proc, glbls)
    else:
        return proc

def _parse_testproc_iter(srcfile, wd=os.getcwd()):
    default_attrs = {'lang':'script'}
    for txt, parsed_attrs in util.extract_tag('test', srcfile, wd):
        attrs = collections.defaultdict(lambda: None)
        attrs.update(default_attrs)
        attrs.update(parsed_attrs)
        if attrs['lang'] == 'python':
            yield _parse_testproc_python(txt), attrs
        if attrs['lang'] == 'script':
            yield _parse_testproc_script(txt), attrs

def _generate_data(test_proc, direction, srcfile, defines, wd=os.getcwd()):
    filename = os.path.join(wd, os.path.basename(srcfile)) + '.{}.data'.format(direction)
    with open(filename, 'wb') as f:
        for p_name, p_type, p_dims, p_data in test_proc.generatedata(direction, defines):
            f.write(p_data)
    return filename

def run_from_src(control_src, test_src, test_valid=True, test_time=True, wd=os.getcwd()):
    for test_proc, attrs in _parse_testproc_iter(control_src, wd):
        datafile_in  = _generate_data(test_proc, 'in', control_src, wd)
        datafile_out = _generate_data(test_proc, 'out', control_src, wd)
        #...
        yield None, attrs['name']
