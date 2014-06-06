#TODO: setup and cleanup mechanism

import argparse
import logging
import os
import pickle
import sys
import textwrap

from . import chill
from . import test
from . import util



def make_local(argsns, arg_parser):
    """
    Make the local test case list. A convinience function for testing a local copy of chill.
    @params argsns Command line arguments
    @params arg_parser The ArgumentParser object
    """    
    util.mkdir_p(os.path.join(os.getcwd(), '.staging'), temp=True)
    argsns.wd = os.path.join(os.getcwd(), '.staging/wd')
    argsns.bin_dir = os.path.join(os.getcwd(), '.staging/bin')
    
    util.mkdir_p(argsns.wd)
    util.mkdir_p(argsns.bin_dir)
    util.shell('cp', [os.path.join(argsns.chill_dir, 'examples/cuda-chill/cudaize.lua'), argsns.wd])
    util.shell('cp', [os.path.join(argsns.chill_dir, 'examples/cuda-chill/cudaize.py'), argsns.wd])
    
    chill_version = argsns.chill_version
    for config in chill.ChillConfig.configs_by_version(argsns.omega_dir, chill_version):
        build_testcase = config.make_build_testcase(argsns.chill_dir, argsns.bin_dir)
        yield build_testcase
        batch_file = os.path.join(argsns.chill_tc_dir, config.name() + '.tclist')
        for tc in make_batch_testcaselist(argsns, arg_parser, batch_file):
            yield tc

def make_runchill_testcase(argsns):
    """
    Make a RunChillTestCase from the given argument namespace
    @param argsns Command line arguments
    """
    assert (argsns.chill_dir != None) or (argsns.bin_dir != None)
    
    ### Required parameters ###
    chill_dir = argsns.chill_dir
    bin_dir = argsns.bin_dir
    build_cuda = argsns.build_cuda
    chill_version = argsns.chill_version
    script_lang = argsns.chill_script_lang
    wd = argsns.wd
    chill_script = argsns.chill_script
    chill_src = argsns.chill_src
    
    chill_bin_dir = bin_dir if bin_dir != None else chill_dir
    
    ### Options to pass to the chill test case ###
    options = dict()
    options['compile-src'] = argsns.chill_test_compile_src
    options['run-script'] = argsns.chill_test_run_script
    options['compile-gensrc'] = argsns.chill_test_compile_gensrc
    options['check-run-script-stdout'] = argsns.chill_test_check_run_script
    
    return chill.RunChillTestCase(chill_bin_dir, chill_script, chill_src, build_cuda=build_cuda, chill_version=chill_version, script_lang=script_lang, wd=wd, options=options)

def make_buildchill_testcase(argsns):
    """
    Make a BuilChillTestCase from the given argument namespace
    @param argsns Command line arguments
    """
    assert argsns.chill_dir != None
    assert argsns.omega_dir != None
    
    chill_dir = argsns.chill_dir
    bin_dir = argsns.bin_dir
    build_cuda = argsns.build_cuda
    chill_version = argsns.chill_version
    chill_script_lang = argsns.chill_script_lang
    omega_dir = os.path.abspath(argsns.omega_dir)
    
    return chill.BuildChillTestCase(chill_dir, omega_dir, build_cuda, chill_script_lang, chill_version, bin_dir)

def make_batch_testcaselist(argsns, arg_parser, batch_file=None):
    """
    Make a list of test cases from a file.
    @param batch_file The batch file name
    @param arg_parser The argument parser. Used to parse lines from the batch file.
    """
    if batch_file is None:
        batch_file = argsns.batch_file
    with open(batch_file, 'r') as f:
        for txt_line in f.readlines():
            if len(txt_line.strip()) == 0: continue         # skip empty lines
            if txt_line.strip().startswith('#'): continue   # skip comment lines
            args = util.applyenv(txt_line.strip())          # replace environment variables with thier values
            args = args.split()                             # split by whitespace
            for tc in args_to_tclist(args, arg_parser, argsns):
                yield tc

@util.callonce
def add_local_args(arg_parser):
    """
    Command line arguments for the local command
    @param arg_parser The local ArgumentParser object
    """
    arg_parser.add_argument('chill_dir', metavar='chill-home')
    arg_parser.add_argument('-v', '--chill-branch', dest='chill_version', default='dev', choices=['release','dev'])
    # - Testing should consider all interface languages. Will uncomment if testing takes too long
    # arg_parser.add_argument('-i', '--interface-lang', nargs=1, action='append', dest='chill_script_lang_list', choices=['script','lua','python'])
    arg_parser.add_argument('-t', '--testcase-dir', dest='chill_tc_dir', default=os.path.join(os.getcwd(), 'test-cases/'))
    arg_parser.set_defaults(wd=os.path.join(os.getcwd(), '.staging/wd'))       # - These don't seem to work
    arg_parser.set_defaults(bin_dir=os.path.join(os.getcwd(), '.staging/bin')) # -

def add_chill_common_args(arg_parser):
    """
    Common chill command line arguments.
    @param arg_parser The ArgumentParser object
    """
    arg_parser.add_argument('-v', '--chill-branch', dest='chill_version', default='dev', choices=['release','dev'])
    cuda_group = arg_parser.add_mutually_exclusive_group()
    cuda_group.add_argument('-u', '--target-cuda', action='store_const', const=True, dest='build_cuda', default=False, help='Test cuda-chill. (Default is chill)')
    cuda_group.add_argument('-c', '--target-c', action='store_const', const=False, dest='build_cuda', default=False, help='Test chill. (Default is chill)')
    arg_parser.add_argument('-i', '--interface-lang', dest='chill_script_lang', choices=['script','lua','python'], default=None, help='Chill interface language. If an interface language is not specified, it will be determined by the script file name.')

def add_boolean_option(arg_parser, name, dest, default=True, help_on=None, help_off=None):
    """
    Add a boolean option.
    @param parg_parser The ArgumentParser object
    @param name The name of the parameter
    @param dest The dest parameter passed to the ArgumentParser
    @param default The default value
    @param help_on The help parameter for the true option
    @param help_off The help parameter for the false option
    """
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument('--' + name, action='store_true', dest=dest, default=default, help=help_on)
    group.add_argument('--no-' + name, action='store_false', dest=dest, default=default, help=help_off)

@util.callonce
def add_chill_run_args(arg_parser):
    """
    Command line arguments specific to running a chill test case
    @param arg_parser The ArgumentParser object
    """
    arg_parser.add_argument('chill_script', help='Chill script file.', metavar='chill-script')
    arg_parser.add_argument('chill_src', help='Chill source file.', metavar='chill-src')
    add_boolean_option(arg_parser, 'compile-src', dest='chill_test_compile_src', default=True, help_on='Compile source file.', help_off='Do not compile source file.')
    add_boolean_option(arg_parser, 'run-script', dest='chill_test_run_script', default=True, help_on='Run chill script.', help_off='Do not run chill script.')
    add_boolean_option(arg_parser, 'compile-gensrc', dest='chill_test_compile_gensrc', default=True, help_on='Compile generated source file', help_off='Do not compile generated source file.')
    add_boolean_option(arg_parser, 'check-run-script', dest='chill_test_check_run_script', default=False, help_on='Diff stdout from chill script against a benchmark.')

@util.callonce
def add_local_command(command_group):
    """
    Add local to the subcommand group
    @param command_group the subparser group object
    """
    local_arg_parser = command_group.add_parser('local')
    add_local_args(local_arg_parser)
    local_arg_parser.set_defaults(func=lambda a, ap: make_local(a, ap))

@util.callonce
def add_chill_command(command_group):
    """
    Add chill-testcase to the subcommand group
    @param command_group The subparser group object
    """
    chill_arg_parser = command_group.add_parser('chill-testcase')
    add_chill_run_args(chill_arg_parser)
    add_chill_common_args(chill_arg_parser)
    chill_arg_parser.set_defaults(func=lambda a, ap: [make_runchill_testcase(a)])

@util.callonce
def add_buildchill_command(command_group):
    """
    Add build-chill-testcase to the subcommand group
    @param command_group The subparser group object
    """
    buildchill_arg_parser = command_group.add_parser('build-chill-testcase')
    add_chill_common_args(buildchill_arg_parser)
    buildchill_arg_parser.set_defaults(func=lambda a, ap: [make_buildchill_testcase(a)])

@util.callonce
def add_batch_args(arg_parser):
    """
    Command line arguments for the batch file command
    @param arg_parser The ArgumentParser object
    """
    arg_parser.add_argument('batch_file', help='Batch file', metavar='batch-filename')

@util.callonce
def add_batch_command(command_group):
    """
    Add batch command to the subcommand group
    @param command_group The subparser group object
    """
    batch_arg_parser = command_group.add_parser('batch')
    add_batch_args(batch_arg_parser)
    batch_arg_parser.set_defaults(func=make_batch_testcaselist)

@util.callonce
def add_commands(arg_parser):
    """
    Add the subcommand group
    @param arg_parser The ArgumentParser object
    """
    command_group = arg_parser.add_subparsers(title='commands')
    add_local_command(command_group)
    add_chill_command(command_group)
    add_buildchill_command(command_group)
    add_batch_command(command_group)

@util.callonce
def add_global_args(arg_parser):
    """
    Add arguments that are used for most subcommands
    @param arg_parser The ArgumentParser object
    """
    arg_parser.add_argument('-w', '--working-dir', dest='wd', default=os.getcwd(), help='The working directory. (Defaults to the current directory)', metavar='working-directory')
    arg_parser.add_argument('-R', '--rose-home', dest='rose_dir', default=os.getenv('ROSEHOME'), help='Rose home directory. (Defaults to ROSEHOME)', metavar='rose-home')
    arg_parser.add_argument('-C', '--chill-home', dest='chill_dir', default=os.getenv('CHILLHOME'), help='Chill home directory. (Defaults to CHILLHOME)', metavar='chill-home')
    arg_parser.add_argument('-O', '--omega-home', dest='omega_dir', default=os.getenv('OMEGAHOME'), help='Omega home directory. (Defaults to OMEGAHOME)', metavar='omega-home')
    arg_parser.add_argument('-b', '--binary-dir', dest='bin_dir', default=None, help='Binary directory.', metavar='bin-dir')
    
@util.callonce
def make_argparser():
    """
    Create the argument parser
    """
    arg_parser = argparse.ArgumentParser(
        prog='python -m testchill',
        epilog=textwrap.dedent('''\
            
            To test a local working copy of chill (from the development branch):
            --------------------------------------------------------------------  
            - Set $OMEGAHOME and compile omega.
            - Run `python -m testchill local <path-to-chill>`
            
        '''),
        description='DESCRIPTION',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    add_global_args(arg_parser)
    add_commands(arg_parser)
    
    # ...
    
    return arg_parser

def args_to_tclist(args=sys.argv[1:], arg_parser=make_argparser(), argsns=None):
    """
    Parse one line and return a list of test cases.
    @params args Raw arguments to be passed to the ArgumentParser object (defaults to sys.args[1:])
    @params arg_parser The ArgumentParser object (defaults to an ArgumentParser returned by make_argparser())
    @params argsns The top level argument namespace (defaults to None)
    """
    if not argsns is None:                           # if an argsns is given,
        argsns = util.copy(argsns, exclude=['func']) # make a shallow copy, (excluding func)
    argsns = arg_parser.parse_args(args, namespace=argsns)
    return list(argsns.func(argsns, arg_parser))

@util.callonce
def main():
    results = list(test.run(args_to_tclist()))
    test.pretty_print_results(results)
    util.rmtemp()
    if any(s.failed() or s.errored() for s in results):
        sys.exit(1)

if __name__ == '__main__':
    main()
    
