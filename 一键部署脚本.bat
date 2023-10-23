@echo off
pip install virtualenv
virtualenv -p python3.9 venv
rem 进入虚拟环境的目录
cd venv/Scripts
rem 激活虚拟环境
call activate.bat
rem 安装依赖包
where python
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pause
cd ../..
pip install -r requirements.txt
rem 暂停显示结果
pause
