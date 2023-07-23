import os


def main():
    print("请输入要执行的指令：\n1 绑定到远程仓库(如果通过源码包安装请执行)\n2 更新bot代码")
    a=input("输入要执行的数字")
    if a=="1":
        os.system("git init")
        os.system("git remote add origin https://github.com/avilliai/Manyana.git")
        print("over")
    elif a=="2":
        print("拉取bot代码")
        os.system("git pull https://github.com/avilliai/Manyana.git")
        print("已更新")
    else:
        print("结束")

# 添加远程仓库

# 获取远程更新并合并到本地


if __name__ == '__main__':
    main()