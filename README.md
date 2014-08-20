testchill  
========

Description  
==========
TODO: better description
testchill is a Python module that runs a series of tests to aid in the development and maintence of CHiLL.
testchill tests that chill compiles successfully, that scripts can be run without error, and that they generate compilable code.
It can also optionally test optimized code for correctness and provide code coverage.  


Running testchill  
===============

testchill is a Python module, and can be run like any other Python module:  
`python -m testchill <suite-args>* <sub-command> <sub-command-args>*`  

Arguments common to all sub commands:  
- `-w <working-directory>`
  Sets the working directory where testchill will compile and run test scripts. If not set, the current working directory will be used.  
- `-R <Rose directory>`
  ROSEHOME environment variable for building omega. If not set, the current ROSEHOME environment variable will be used.  
- `-C <chill directory>`
  Sets the path to chill. If not set, the current CHILLHOME environment variable will be used.  
- `-O <omega directory>`
  Sets the path to omega. If not set, the current OMEGAHOME environment variable will be used.  
- `-b <binary directory>`
  A directory were all chill binary files will be placed after being compiled. The chill directory will be used by default.  


Subcommands for running individual tests:  

To test a local working copy of chill (from the development branch):  
------------------------------------------------------------ 
- Set $OMEGAHOME and compile omega.  
- Run `python -m testchill local <path-to-chill>`  

To test chill from the repository:  
------------------------------
- Run `python -m testchill repo <svn-user-name>`  


