pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install --user --upgrade pip
pip install virtualenv
virtualenv -p python3.9 venv
cd venv/Scripts
call activate.bat
where python
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
cd ../..
pip install -r requirements.txt
pause
