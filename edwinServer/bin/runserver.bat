setlocal

rem # set python executable 
set PYTHON_BIN=D:\pythonenv\python272_flask\Scripts\python.exe

rem # base path, it is the parent of root package path 
set BASE_PATH=D:\corp_files\trunk\workspace\Edwin

rem # set your python script file. Please be noticed to trim the tailed space of file name 
set MY_PY_SCRIPT=runserver.py


rem #=================================
rem # do not change the following code
rem #=================================
set PYTHONPATH=%BASE_PATH%

set SCRIPT_PATH=%BASE_PATH%\edwinServer\web
set BIN_PATH=%BASE_PATH%\edwinServer\bin
SET LOCK_FILE=%BIN_PATH%\locks\%MY_PY_SCRIPT%.lock
SET MY_PY_FILE=%SCRIPT_PATH%\%MY_PY_SCRIPT%

dir %LOCK_FILE% 
if  not %errorlevel% == 0 ( 
    echo ''  > %LOCK_FILE%	
    %PYTHON_BIN% %MY_PY_FILE%
    del %LOCK_FILE% 
)

endlocal

