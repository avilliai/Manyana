@echo off
set PYTHON_EXE=..\environments\Python39\python.exe
set MAIN_SCRIPT=main.py

rem checking.....
if exist "%PYTHON_EXE%" (
    cd venv\Scripts
    call activate.bat
    cd ..\..
    "%PYTHON_EXE%" "%MAIN_SCRIPT%"
) else (
    echo Python doesn't exists
    python %MAIN_SCRIPT%
)

exit /b
