# testchill  

## Description  
TODO: better description
testchill is a Python module that runs a series of tests to aid in the development and maintence of CHiLL.
testchill tests that chill compiles successfully, that scripts can be run without error, and that they generate compilable code.
It can also optionally test optimized code for correctness and provide code coverage.  


## Running testchill  

testchill is a Python module, and can be run like any other Python module:  
`python -m testchill <suite-args>* <sub-command> <sub-command-args>*`  

### Arguments common to all sub commands (with the exception of `repo` and `local`):  
- `-w <working-directory>, --working-dir <working-directory>`

   Sets the working directory where testchill will compile and run test scripts. If not set, the current working  directory will be used.

- `-R <rose-home>, --rose-home <rose-home>`

   Set ROSEHOME environment variable for building omega. If not set, the current ROSEHOME environment variable will be used.

- `-C <chill directory>, --chill-home <chill-home>`

   Set the path to chill. If not set, the current CHILLHOME environment variable will be used.

- `-O <omega directory>, --omega-home <omega-home>`

   Set the path to omega. If not set, the current OMEGAHOME environment variable will be used.

- `-b <binary directory>, --binary-dir <binary directory>`

   Set the directory were all chill binary files will be placed after being compiled. The chill directory will be used by default.

### Subcommands for running individual tests:  
- <h4> `build-chill-testcase ...`

   Build chill. It will fail if the build process returns non zero.  
   Optional arguments are:  
   - `-v {release | dev}`
   
     `release` will build the old release version, and `dev` will build the current development version.
     `dev` is used by default.
   
   - `-u | -c`
   
     `-c` will build chill, and `-u` will build cuda-chill.
     `-c` is used by default.
   
   - `i {script | lua | python}`
   
     `script` will build chill with the original chill script language.  
     `lua` will build chill with lua as the interface language.  
     `python` will build chill with python as the interface language.
   
- <h4> `chill-testcase

   Run a chill tests script

- <h4> batch
- <h4> local
- <h4> repo

To test a local working copy of chill (from the development branch):  
------------------------------------------------------------ 
- Set $OMEGAHOME and compile omega.  
- Run `python -m testchill local <path-to-chill>`  

To test chill from the repository:  
------------------------------
- Run `python -m testchill repo <svn-user-name>`  


