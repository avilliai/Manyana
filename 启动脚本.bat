cd venv/Scripts
rem 激活虚拟环境
call activate.bat
cd ../..
start /b /d "./vits/flask_voice.py" python flask_voice.py
python main.py
