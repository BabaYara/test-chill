usage: python -m testchill [-h] [-w working-directory] [-R rose-home]  
                           [-C chill-home] [-O omega-home] [-b bin-dir]  
                           {local,chill-testcase,build-chill-testcase,batch}  
                           ...  
  
To test a local working copy of chill (from the development branch):  
--------------------------------------------------------------------  
- Set $OMEGAHOME and compile omega.  
- Run
  ```sh
  python -m testchill local <path-to-chill>
  ```  
  This creates a temporary directory where it builds chill in each
  configuration and tests it.


optional arguments:  
  -h, --help            show this help message and exit  
  -w working-directory, --working-dir working-directory  
                        The working directory. (Defaults to the current  
                        directory)  
  -R rose-home, --rose-home rose-home  
                        Rose home directory. (Defaults to ROSEHOME)  
  -C chill-home, --chill-home chill-home  
                        Chill home directory. (Defaults to CHILLHOME)  
  -O omega-home, --omega-home omega-home  
                        Omega home directory. (Defaults to OMEGAHOME)  
  -b bin-dir, --binary-dir bin-dir  
                        Binary directory.  
  
commands:  
  {local,chill-testcase,build-chill-testcase,batch}  
  
EPILOG  
