import collections
import os
import pickle
import re

from . import util

_script_parser = None
def _get_script_parser():
    """
    Retrieve the test code generator language parser.
    """
    global _script_parser
    if _script_parser is None:
        with open('testchill/cpp_validate/parser.pickle','rb') as f:
            _script_parser = pickle.load(f)
    return _script_parser

def _parse_testproc_python(txt, glbls=None):
    """
    Parse text as a python testchill._cpp_validate_env.Procedure object"
    @param txt Python code to be parsed.
    @param glbls A python global dict.
    """
    if glbls is None:
        glbls = dict()
    exec('import testchill._cpp_validate_env\nfrom testchill._cpp_validate_env import *', None, glbls)
    return eval(txt, glbls)

def _parse_testproc_script(txt, glbls=None):
    """
    Parse text as test code generator language.
    @param txt Code to be parsed.
    @param glbls A python global dict.
    """
    parser = _get_script_parser()
    proc = list(parser.parse(util.textstream(txt)))[0]
    if glbls is None:
        from . import _cpp_validate_env
        glbls = dict()
        return _cpp_validate_env.addbindings(proc, glbls)
    else:
        return proc

def _parse_testproc_iter(srcfile, wd=os.getcwd()):
    """
    Parse all test procedures from a file.
    @param srcfile File path to parse.
    @param wd Working directory.
    """
    default_attrs = {'lang':'script', 'define':'dict()'}
    for txt, parsed_attrs in util.extract_tag('test', srcfile, wd):
        attrs = collections.defaultdict(lambda: None)
        attrs.update(default_attrs)
        attrs.update(parsed_attrs)
        if attrs['lang'] == 'python':
            yield _parse_testproc_python(txt), attrs
        if attrs['lang'] == 'script':
            yield _parse_testproc_script(txt), attrs

def _compile_gpp(src, dest):
    """
    Compile a signle C++ source file into an executable object.
    @param src Source file path.
    @param dest Object file path.
    """
    util.shell('g++', ['-o', dest, src, '-lrt'])

def _test_time(control_time, test_time):
    """
    Determine if test ran faster than control.
    @param control_time Time taken by control.
    @param test_time Time taken by test.
    """
    return control_time > test_time

def _test_validate(control_dataout_path, test_dataout_path):
    """
    Determine if control and test computed the same values.
    @param control_dataout_path Path to the file writen by control.
    @param test_dataout_path Path to the file writen by test.
    """
    with open(control_dataout_path, 'rb') as controlfile:
        with open(test_dataout_path, 'rb') as testfile:
            return controlfile.read() == testfile.read()

def _run_test_validate_time(control_obj_path, test_obj_path, datain_path):
    control_dataout_path = util.mktemp()
    test_dataout_path = util.mktemp()
    control_time, = eval(util.shell(os.path.abspath(control_obj_path), [datain_path, control_dataout_path]))
    test_time, = eval(util.shell(os.path.abspath(test_obj_path), [datain_path, test_dataout_path]))
    return _test_validate(control_dataout_path, test_dataout_path), _test_time(control_time, test_time)

def _compile_run_test_validate_time(control_src_path, test_src_path, datain_path):
    control_obj_path = '.'.join(control_src_path.split('.')[:-1])
    test_obj_path = '.'.join(test_src_path.split('.')[:-1])
    _compile_gpp(control_src_path, control_obj_path)
    _compile_gpp(test_src_path, test_obj_path)
    test_validate, test_time = _run_test_validate_time(control_obj_path, test_obj_path, datain_path)
    util.shell('rm', [control_obj_path])
    util.shell('rm', [test_obj_path])
    return test_validate, test_time

def _generate_initial_data(test_proc, srcfile, defines, wd=os.getcwd()):
    filename = os.path.join(wd, os.path.basename(srcfile)) + '.data'
    with open(filename, 'wb') as f:
        for p_name, p_type, p_dims, p_data in test_proc.generatedata('in', defines):
            f.write(p_data)
        for p_name, p_type, p_dims, p_data in test_proc.generatedata('out', defines):
            f.write(p_data)
    return filename

def _format_insertion_dict(test_proc, src_path, defines):
    with open(src_path, 'r') as src_file:
        return {
                'defines'      : '\n'.join(['#define {} {}'.format(k,v) for k,v in defines]),
                'test-proc'    : src_file.read(),
                'declarations' : '\n'.join(test_proc.generatedecls()),
                'read-in'      : '\n'.join(test_proc.generatereads(test_proc, 'in', 'datafile_initialize')),
                'read-out'     : '\n'.join(test_proc.generatereads(test_proc, 'out', 'datafile_initialize')),
                'run'          : test_proc.invoke_str(),
                'write-out'    : '\n'.join(test_proc.generatewrites(test_proc, 'datafile_out')),
            }

def _write_generated_code(test_proc, src_path, defines, dest_filename, wd):
    insertion_dict = _format_insertion_dict(test_proc, src_path, defines)
    dest_file_path = os.path.join(wd, dst_filename)
    with open('testchill/cpp_validate/src/validate.cpp', 'r') as template_file:
        with open(dest_file_path, 'w') as destfile:
            template_text = template_file.read()
            desttext = template_text
            for match in re.finditer(r'(?P<indent>[ \t]*)//# (?P<name>[^\s]+)', template_text):
                destlines = insertion_dict[match.group('name')].splitlines()
                indent = match.group('indent')
                match_text = match.group()
                repl_text = '\n'.join([indent + line for line in destlines])
                desttext = desttext.replace(match_text, repl_text)
            destfile.write(desttext)
    return dest_file_path

def run_from_src(control_src, test_src, wd=os.getcwd()):
    control_src_path = os.path.join(wd, control_src)
    test_src_path = os.path.join(wd, test_src)
    for test_proc, attrs in _parse_testproc_iter(control_src, wd):
        defines = eval(attrs['define'])
        datafile_in  = _generate_data(test_proc, 'in', control_src, defines, wd=wd)
        control_datafile_out = _generate_data(test_proc, 'out', control_src, defines, wd=wd)
        test_datafile_out = _generate_data(test_proc, 'out', test_src, defines, wd=wd)
        control_src_path = _write_generated_code(test_proc, control_src, defines, 'control.cc', wd)
        test_src_path = _write_generated_code(test_proc, test_src, defines, 'test.cc', wd)
        yield attrs['name'], _compile_run_test_validate_time(control_src_path, test_src_path, datafile_in, control_datafile_out, test_datafile_out)
