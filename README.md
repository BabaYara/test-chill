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



To test a local working copy of chill (from the development branch):  
------------------------------------------------------------ 
- Set $OMEGAHOME and compile omega.  
- Run `python -m testchill local <path-to-chill>`  

To test chill from the repository:  
------------------------------
- Run `python -m testchill repo <svn-user-name>`  


