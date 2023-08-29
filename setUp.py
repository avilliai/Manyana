import os

from plugins.newLogger import newLogger


def main():
    print("请输入要执行的指令：\n1 绑定到远程仓库(如果通过源码包安装请执行)\n2 更新bot代码\n3 启动数据清理大师(doge)")

    a=input("输入要执行的数字")
    if a=="1":
        os.system("git init")
        os.system("git remote add origin https://github.com/avilliai/Manyana.git")
        print("正在添加文件.....这可能需要较长时间")
        os.system("git add .")
        print("over")
    elif a=="2":
        logger = newLogger()
        logger.warning("更新python库")
        logger.warning("更新可能包含setUp.py自身更新。一般建议运行两次setUp.py")
        os.system("pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/")
        os.system("pip install pandora-chatgpt")
        #os.system("pip install --upgrade poe-api")
        #os.system("pip install --upgrade requests")
        #os.system("pip install --upgrade urllib3[socks]")
        #os.system("pip install selenium")
        logger.info("拉取bot代码\n--------------------")
        logger.warning("如出现 Merge冲突 例如：Your local changes to the following files would be overwritten by merge:\n请重命名本地的对应文件，拉取后将你的数据重新导入\n--------------------")
        os.system("git pull https://github.com/avilliai/Manyana.git")
        logger.info("结束")
        logger.info("如更新成功请自行查看 更新日志.yaml")
    elif a=="3":
        print("执行清理缓存操作")
        ls1 = os.listdir("data/pictures/avatars")
        for i in ls1:
            try:
                os.remove("data/pictures/avatars/" + i)
            except:
                continue
        print("清理头像缓存完成")
        ls1 = os.listdir("data/voices")
        for i in ls1:
            try:
                os.remove("data/voices/" + i)
            except:
                continue
        print("清理音频缓存完成")
        ls1 = os.listdir("data/pictures/cache")
        for i in ls1:
            try:
                os.remove("data/pictures/cache/" + i)
            except:
                continue

        ls1 = os.listdir("data/pictures/wallpaper")
        for i in ls1:
            try:
                os.remove("data/pictures/wallpaper/" + i)
            except:
                continue
        print("清理本地图库缓存完成,缓存的涩图都没喽")
        print("清理缓存完成")
    else:
        print("结束")

# 添加远程仓库

# 获取远程更新并合并到本地


if __name__ == '__main__':
    main()
    input("按任意键退出.")