import os

from plugins.newLogger import newLogger


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
        logger = newLogger()
        logger.warning("更新可能包含setUp.py自身更新。一般建议运行两次setUp.py")
        logger.warning("更新python库，按1跳过，如果最近没有更新过，不建议跳过，可能错过某些更新。")
        if input("在这里输入:")!="1":

            os.system("pip install numpy==1.23.0")
            #os.system("pip install aspose-words")

            #os.system("pip install --upgrade poe-api")
            #os.system("pip install --upgrade requests")
            #os.system("pip install --upgrade urllib3[socks]")
            #os.system("pip install selenium")
        logger.info("拉取bot代码\n--------------------")
        logger.warning("如出现 Merge冲突 例如：Your local changes to the following files would be overwritten by merge:\n请重命名本地的对应文件，拉取后将你的数据重新导入\n--------------------")
        logger.info("选择更新源()：\n1 git源\n2 镜像源(无需代理，但更新缓慢)")
        sfsff=input("选择更新源(输入数字)：")
        if sfsff=="1":
            os.system("git pull https://github.com/avilliai/Manyana.git")
        else:
            os.system("git pull https://gitclone.com/github.com/avilliai/Manyana")
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
        import shutil
        shutil.copyfile('data/autoReply/lexicon/init.xlsx',
                        'data/autoReply/lexicon/public.xlsx')
        logger.info("清理词库成功")
        logger.warning("请自行删除 miraiBot/plugins/AutoGroup-2.0.3.mirai.jar")
        logger.info("请自行修改 chatGLM模式为chatglm_pro")


    else:
        print("结束")

# 添加远程仓库

# 获取远程更新并合并到本地


if __name__ == '__main__':
    main()
    input("按任意键退出.")