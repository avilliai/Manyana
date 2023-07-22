import os
r = os.popen ("where python") # 启动脚本
#print (r.read (),type(r.read())) # 读取输出内容
a=r.read().split("\n")
pyPath=a[0][:-10]
print()
r.close () # 关闭文件对象
print("执行拷贝操作")

import os
import shutil

source_path = os.path.abspath(r'site-packages')
target_path = os.path.abspath(pyPath+"Lib/site-packages")

if not os.path.exists(target_path):
    # 如果目标路径不存在原文件夹的话就创建
    os.makedirs(target_path)

if os.path.exists(source_path):
    # 如果目标路径存在原文件夹的话就先删除
    shutil.rmtree(target_path)

shutil.copytree(source_path, target_path)
print('依赖库拷贝完成')
print("拉取bot代码")
os.system("git clone https://github.com/avilliai/Manyana.git")
print("完成，请阅读readMe并填写对应配置文件")

