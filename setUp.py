import logging
import os
import subprocess
import sys

import colorlog

import shutil
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
    print("请输入要执行的指令：\n1 绑定到远程仓库(如果通过源码包安装请执行)\n2 更新bot代码\n3 启动数据清理大师(doge)\n4 导出群信息，制作一个chatLearning可用的配置文件\n5 全面去除二刺猿相关内容")

    a=input("输入要执行的数字")
    if a=="1":
        os.system("git init")
        os.system("git remote add origin https://github.com/avilliai/Manyana.git")
        print("正在添加文件.....这可能需要较长时间")
        os.system("git add .")
        print("over")
    elif a=="2":
        updaat()
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
        ls1 = os.listdir("data/music/musicCache")
        for i in ls1:
            try:
                os.remove("data/music/musicCache/" + i)
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
    elif a=="4":
        import json
        print("chatLearning： https://mirai.mamoe.net/topic/1018/chatlearning-%E8%AE%A9bot%E5%AD%A6%E4%BC%9A%E4%BD%A0%E7%9A%84%E7%BE%A4%E8%81%8A/8")
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
        ja = json.dumps(p,ensure_ascii=False,indent=1)
        with open("config.clc", "w", encoding="utf_8_sig",newline='\n') as fp:
            fp.write(ja)
        print("完毕，请用config.clc覆盖chatLearning文件夹下同名文件")
    elif a=="5":
        import yaml
        logger = newLogger()
        logger.info("开始清理：nudgeReply.yaml")
        with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
            resy = yaml.load(f.read(), Loader=yaml.FullLoader)
        resy["BeatNudge"]=["干嘛","有事吗"]
        resy["BeatNudge1"]=["干嘛","有事吗"]
        resy["nudgedReply"]=["干嘛","有事吗"]
        with open('config/nudgeReply.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(resy, file, allow_unicode=True)
        logger.info("清理config/nudgeReply.yaml完成")
        logger.info("开始清理：词库")
        os.remove("data/autoReply/lexicon/public.xlsx")

        shutil.copyfile('data/autoReply/lexicon/init.xlsx',
                        'data/autoReply/lexicon/public.xlsx')
        logger.info("清理词库成功")
        logger.warning("请自行删除 miraiBot/plugins/AutoGroup-2.0.3.mirai.jar")
        logger.info("请自行修改 chatGLM模式为chatglm_pro")


    else:
        print("结束")
def updaat(f=False):

    logger.warning("更新可能包含setUp.py自身更新。一般建议运行两次setUp.py")
    logger.warning("更新python库，按1跳过，如果最近没有更新过，不建议跳过，可能错过某些更新。")
    if input("在这里输入:") != "1":
        os.system("pip install edge-tts")
        os.system("pip install psutil")
        os.system("pip install -q -U google-generativeai")
        os.system("pip install ruamel.yaml")
        # os.system("pip install -U zhipuai")
        # os.system("pip install pydantic==1.10.11")
        # os.system("pip install aspose-words")

        # os.system("pip install --upgrade poe-api")
        # os.system("pip install --upgrade requests")
        # os.system("pip install --upgrade urllib3[socks]")
        # os.system("pip install selenium")
    logger.info("拉取bot代码\n--------------------")
    logger.info("选择更新源()：\n1 git源\n2 镜像源(无需代理，但版本一般落后于git源)")
    sfsff = input("选择更新源(输入数字)：")
    if sfsff == "1":
        # os.system("git pull https://github.com/avilliai/Manyana.git")
        # 启动进程
        p = subprocess.Popen(['git', 'pull', 'https://github.com/avilliai/Manyana.git'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        # 获取进程的输出和错误信息
        stdout, stderr = p.communicate()

        # 输出内容和错误信息都是字节串，需要解码为字符串
        stdout = stdout.decode()
        logger.info(stdout)
        stderr = stderr.decode()

        # 标记是否在错误信息中
        in_error_info = False

        # 存放冲突文件名的列表
        conflict_files = []
        if f==True:
            if os.path.exists("./temp"):
                for i in os.listdir("./temp"):
                    logger.info("开始处理"+i)
                    if os.path.exists("config/"+i):
                        conflict_file_dealter("./temp/"+i,"config/"+i)
                    else:
                        continue
            logger.info("处理冲突文件完成")
            shutil.rmtree("./temp")
            logger.info("你可以关闭此窗口了")
            input()
        # 逐行检查错误信息
        for line in stderr.split('\n'):
            # 标记冲突文件名开始位置
            if 'error: Your local changes to the following files would be overwritten by merge:' in line:
                in_error_info = True
                continue  # 结束当前循环，进入下一个循环

            # 标记冲突文件名结束位置
            if 'Please commit your changes or stash them before you merge.' in line:
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
                    shutil.copyfile(file, file.replace("config", "temp"))
                    os.remove(file)
                else:
                    os.mkdir("./temp")
                    shutil.copyfile(file, file.replace("config", "temp"))
                    os.remove(file)
            else:
                logger.warning("无法处理的 " + file)
                logger.warning("请自行决定删除或修改文件名称，在重新拉取后根据旧文件重新填写新文件")
        logger.warning("如果存在冲突文件，请按任意键，程序将自动处理")
        a=input("即将再次执行拉取操作，输入任意键继续，按1退出：")
        if a==1:
            return
        updaat(True)
        # 不要忘了等待进程结束
        p.wait()
    else:
        os.system("git pull https://gitclone.com/github.com/avilliai/Manyana")
    logger.info("结束")
    logger.info("如更新成功请自行查看 更新日志.yaml")
# 创建一个YAML对象来加载和存储YAML数据
try:
    from ruamel.yaml import YAML
except Exception as e:
    logger.error("未安装ruamel.yaml库，无法处理冲突文件，开始安装缺少的依赖")
    os.system("pip install ruamel.yaml")
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
            logger.info("更新key"+str(k)+" value"+str(v))
            new[k] = v

def conflict_file_dealter(file_old='old_aiReply.yaml', file_new='new_aiReply.yaml'):
    # 加载旧的YAML文件
    with open(file_old, 'r',encoding="utf-8") as file:
        old_data = yaml.load(file)

    # 加载新的YAML文件
    with open(file_new, 'r',encoding="utf-8") as file:
        new_data = yaml.load(file)

    # 遍历旧的YAML数据并更新新的YAML数据中的相应值
    merge_dicts(old_data, new_data)

    # 把新的YAML数据保存到新的文件中
    with open(file_new, 'w') as file:
        yaml.dump(new_data, file)



# 添加远程仓库

# 获取远程更新并合并到本地


if __name__ == '__main__':
    main()
    input("按任意键退出.")