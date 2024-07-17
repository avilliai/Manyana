# -*- coding:utf-8 -*-
import logging
import os
import shutil
import subprocess
import colorlog
import sys

#下面的两行是launcher启动必要设置，勿动。
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
current_dir = os.getcwd()

# 获取上一级目录
parent_dir = os.path.dirname(current_dir)

# 检测上一级目录下的environments/MinGit/cmd/git.exe是否存在
custom_git_path = os.path.join(parent_dir, "environments", "MinGit", "cmd", "git.exe")
if os.path.exists(custom_git_path):
    git_path = custom_git_path
else:
    git_path = "git"

custom_python_path = os.path.join(parent_dir, "environments", "Python39", "python.exe")
if os.path.exists(custom_python_path):
    python_path = custom_python_path
else:
    python_path = "python"
custom_pip_path = os.path.join(parent_dir, "environments", "Python39", "Scripts","pip.exe")
venv_pip=os.path.join("venv", "Scripts","pip.exe")
if os.path.exists(custom_pip_path):
    pip_path = custom_pip_path
elif os.path.exists(venv_pip):
    pip_path=venv_pip
else:
    pip_path = "pip"
def newLogger():
    # 创建一个logger对象
    logger = logging.getLogger("villia")
    # 设置日志级别为DEBUG，这样可以输出所有级别的日志
    logger.setLevel(logging.DEBUG)
    # 创建一个StreamHandler对象，用于输出日志到控制台
    console_handler = logging.StreamHandler()
    # 设置控制台输出的日志格式和颜色
    logger.propagate = False
    console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_colors = {
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
    console_handler.setFormatter(console_formatter)
    # 将控制台处理器添加到logger对象中
    logger.addHandler(console_handler)
    return logger

logger = newLogger()
def main():
    print(
        """请输入要执行的指令：
        1 绑定到远程仓库(如果通过源码包安装请执行)
        2 更新bot代码
        3 清理无用数据(如缓存图片)
        4 导出群信息，制作一个chatLearning可用的配置文件
        5 其他素材下载(可选)
        6 安装vits功能对应依赖""")
    a = input("输入要执行的数字")
    if a == "1":
        os.system(f"{git_path} init")
        os.system(f"{git_path} remote add origin https://github.com/avilliai/Manyana.git")
        print("正在添加文件.....这可能需要较长时间")
        os.system(f"{git_path} add .")
        print("over")
    elif a == "2":
        updaat()
    elif a == "3":
        print("执行清理缓存操作")
        aimdir=["data/pictures/avatars","data/voices","data/music/musicCache","data/pictures/cache","data/pictures/wallpaper","data/blueArchive/arona","data/blueArchive/cache","data/Elo","data/arknights","data/backrooms"]
        for ib in aimdir:
            ls1 = os.listdir(ib)
            for i in ls1:
                try:
                    os.remove(f"{ib}/" + i)
                except:
                    continue
        print("清理缓存完成")
    elif a == "4":
        import json
        print(
            "chatLearning： https://mirai.mamoe.net/topic/1018/chatlearning-%E8%AE%A9bot%E5%AD%A6%E4%BC%9A%E4%BD%A0%E7%9A%84%E7%BE%A4%E8%81%8A/8")
        if os.path.exists("config.clc"):
            with open("config.clc", "r", encoding="utf_8_sig") as ass:
                p = json.loads(ass.read())
        else:
            p = {
                "unmergegrouplist": [],
                "learninggrouplist": [
                    628763673,
                    699455559
                ],
                "replygrouplist": [
                    628763673,
                    699455559
                ],
                "interval": 900,
                "sendmode": 0,
                "mergetime": 900,
                "learning": 0,
                "merge": 0,
                "reply": 0,
                "replychance": 50,
                "admin": 0,
                "Administrator": [
                    123456
                ],
                "blackfreq": 5,
                "voicereply": 0,
                "voicereplychance": 20,
                "synthesizer": "",
                "version": "3.0.3",
                "tag": {},
                "singlereplychance": {},
                "singlevoicereplychance": {},
                "typefreq": {},
                "tempmessagenum": 32,
                "fastdelete": 0,
                "replywait": [
                    0,
                    0
                ],
                "voicecharerror": "存在违规字符，转换失败",
                "voicecderror": "转换冷却中",
                "voicelengtherror": "长度超过限制",
                "deletesuccess": "已从词库内删除！",
                "deletetemperror": "删除失败，该消息已不在缓存内",
                "deletefinderror": "删除失败，词库中已无法找到该答案",
                "replycd": 3,
                "stopsign": 0,
                "voicecommand": "快说 ",
                "cosmatch": 0,
                "cosmatching": 0.5,
                "botname": [
                    "我"
                ],
                "replylength": 100,
                "atreply": 1
            }
        file1 = open('data/music/groups.txt', 'r')
        js1 = file1.read()
        js1 = json.loads(js1)
        file1.close()
        da = js1.keys()
        print(list(da), type(list(da)))
        p["replygrouplist"] = list(da)
        p["learninggrouplist"] = list(da)
        ja = json.dumps(p, ensure_ascii=False, indent=1)
        with open("config.clc", "w", encoding="utf_8_sig", newline='\n') as fp:
            fp.write(ja)
        print("完毕，请用config.clc覆盖chatLearning文件夹下同名文件")
    elif a=="5":
        logger.info("图片素材下载/更新\n输入要执行的指令：\n1 下载/更新星穹铁道资源")
        orderP = input("在这里输入指令：")
        if orderP == "1":
            if os.path.exists("./data/star-rail-atlas"):
                os.chdir("./data")
                logger.info("文件夹已存在，进入更新模式")
                os.system(f"{git_path} pull https://gitee.com/Nwflower/star-rail-atlas.git")
            else:
                os.chdir("./data")
                logger.info("文件夹不存在，拉取素材")
                os.system(f"{git_path} clone https://gitee.com/Nwflower/star-rail-atlas.git")
    elif a == "6":
        logger.info("开始安装vits语音模块相关依赖")
        os.system(f"{custom_pip_path} install -r vits/vitsRequirements.txt")
    else:
        print("结束")
def updaat(f=False, jump=False, source=None):
    if not jump:
        logger.warning("更新python库，按1跳过，如果更新后启动失败，请回来执行此步骤。")
        if input("在这里输入:") != "1":
            logger.warning("即将开始更新依赖库，请确保已关闭代理，否则无法安装依赖库")
            input("按任意键继续：")
            os.system(f"{custom_pip_path} install bingart")
            os.system(f"{custom_pip_path} install emoji")
    if source is None:
        logger.info("拉取bot代码\n--------------------")
        logger.info(
            "选择更新源(git源 镜像源相互兼容)：\n1 git源\n2 镜像源1\n3 镜像源2 \n4 中国计算机协会源(搭建用的默认gitlink源就选这个，不兼容上述源)")
        source = input("选择更新源(输入数字 )：")
    else:
        source = str(source)
    if source == "1":
        # os.system("git pull https://github.com/avilliai/Manyana.git")
        # 启动进程
        p = subprocess.Popen([f'{git_path}', 'pull', 'https://github.com/avilliai/Manyana.git'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    elif source == "2":
        p = subprocess.Popen([f'{git_path}', 'pull', 'https://github.moeyy.xyz/https://github.com/avilliai/Manyana'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    elif source == "3":
        p = subprocess.Popen([f'{git_path}', 'pull', 'https://mirror.ghproxy.com/https://github.com/avilliai/Manyana'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif source == "4":
        p = subprocess.Popen([f'{git_path}', 'pull', 'https://www.gitlink.org.cn/lux-QAQ/Manyana'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logger.error("无效输入，重新执行")
        updaat()
    # 获取进程的输出和错误信息
    stdout, stderr = p.communicate()
    stdout = stdout.decode('utf-8', errors='ignore')
    stderr = stderr.decode('utf-8', errors='ignore')
    logger.info(stdout)
    logger.warning(stderr)

    # 标记是否在错误信息中
    in_error_info = False

    # 存放冲突文件名的列表
    conflict_files = []
    if f:
        if os.path.exists("./temp"):
            if len(os.listdir("./config")) != 14:
                logger.error(
                    "文件数目异常，请参考远程仓库config文件夹https://github.com/avilliai/Manyana/tree/main/config补全缺失文件。")
                input("如已补全请按任意键继续：")
            for i in os.listdir("./temp"):
                logger.info("开始处理" + i)
                if os.path.exists("config/" + i):
                    conflict_file_dealter("./temp/" + i, "config/" + i)
                    if os.path.exists("./temp/conflict " + i):
                        os.remove("./temp/conflict " + i)
                    os.rename("./temp/" + i, "./temp/conflict " + i)
                else:
                    continue
            # shutil.rmtree("./temp")
        logger.info("处理冲突文件完成")
        logger.info("旧的冲突文件被保存到了temp文件夹，以防万一你需要它们。")
        logger.info("你可以关闭此窗口了")
        logger.warning("如果出现启动闪退，重新执行更新脚本，不要跳过 更新python库 环节，执行结束后即可正常启动")
        input()
    # 逐行检查错误信息
    for line in stderr.split('\n'):
        # 标记冲突文件名开始位置
        if 'error: Your local changes to the following files would be overwritten by merge:' in line:
            in_error_info = True
            continue  # 结束当前循环，进入下一个循环
        elif 'error: 您对下列文件的本地修改将被合并操作覆盖：' in line:
            in_error_info = True
            continue
        # 标记冲突文件名结束位置
        if 'Please commit your changes or stash them before you merge.' in line:
            in_error_info = False
        elif '请在合并前提交或贮藏您的修改。' in line:
            in_error_info = False
        # 将冲突文件名添加到列表
        if in_error_info:
            conflict_files.append(line.strip())

    # 显示冲突的文件列表
    for file in conflict_files:
        print('冲突文件:', file)
        logger.warning("开始处理冲突文件")
        if file.endswith(".py"):
            os.remove(file)
            logger.warning("移除了" + file)
        elif file.endswith(".yaml"):
            logger.info("冲突的配置文件" + file)

            logger.warning("开始处理冲突文件.....读取中")

            if os.path.exists("./temp"):
                try:
                    shutil.copyfile(file, file.replace("config/", "temp/").replace("data/", "temp/"))
                    os.remove(file)
                except:
                    continue
            else:
                os.mkdir("./temp")
                shutil.copyfile(file, file.replace("config", "temp"))
                os.remove(file)
        else:
            os.remove(file)
            logger.warning("移除了 " + file)
            # logger.warning("请自行决定删除或修改文件名称，在重新拉取后根据旧文件重新填写新文件")
    logger.warning("开始处理冲突文件")
    logger.info("即将再次执行拉取操作")
    updaat(True, True, str(source))
    # 不要忘了等待进程结束
    p.wait()

    logger.info("结束")
    logger.info("如更新成功请自行查看 更新日志.yaml")


# 创建一个YAML对象来加载和存储YAML数据
try:
    from ruamel.yaml import YAML
except Exception as e:
    logger.error("未安装ruamel.yaml库，无法处理冲突文件，开始安装缺少的依赖")
    os.system(f"{custom_pip_path} install ruamel.yaml")
    from ruamel.yaml import YAML
# 创建一个YAML对象来加载和存储YAML数据
yaml = YAML()


def merge_dicts(old, new):
    for k, v in old.items():
        # 如果值是一个字典，并且键在新的yaml文件中，那么我们就递归地更新键值对
        if isinstance(v, dict) and k in new and isinstance(new[k], dict):
            merge_dicts(v, new[k])
        # 如果键在新的yaml文件中，我们就更新它的值
        elif k in new:
            logger.info("更新key" + str(k) + " value" + str(v))
            new[k] = v


def conflict_file_dealter(file_old='old_aiReply.yaml', file_new='new_aiReply.yaml'):
    # 加载旧的YAML文件
    with open(file_old, 'r', encoding="utf-8") as file:
        old_data = yaml.load(file)

    # 加载新的YAML文件
    with open(file_new, 'r', encoding="utf-8") as file:
        new_data = yaml.load(file)

    # 遍历旧的YAML数据并更新新的YAML数据中的相应值
    merge_dicts(old_data, new_data)

    # 把新的YAML数据保存到新的文件中
    with open(file_new, 'w', encoding="utf-8") as file:
        yaml.dump(new_data, file)


# 添加远程仓库

# 获取远程更新并合并到本地


if __name__ == '__main__':
    main()
    input("按任意键退出.")
