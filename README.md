To test a local working copy of chill (from the development branch):  
--------------------------------------------------------------------  
- Set $OMEGAHOME and compile omega.  
- Run
  ```Bash
  python -m testchill local _path-to-chill_
  ```  
  This creates a temporary directory where it builds chill in each
  configuration and tests it.

