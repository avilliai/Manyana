@echo off

:loop
cd venv\Scripts
call activate.bat
cd ../..
python main.py
REM checking......
goto loop

REM EXIT PROCESS
pause