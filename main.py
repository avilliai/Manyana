# -*- coding:utf-8 -*-
import datetime
import json

import os
import random
import shutil
import subprocess
import sys
from asyncio import sleep as sleep1
from time import sleep

import yaml
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage, Shutdown

from plugins.RandomStr import random_str
from plugins.newLogger import newLogger
from plugins.systeminfo import get_system_info
from run import aiReply, voiceReply, nudgeReply, wikiHelper, imgSearch, extraParts, wReply, userSign, groupManager, \
    PicRandom, musicShare, LiveMonitor, bertVits2, aronaapi, groupGames, musicpick, scheduledTasks, sovits2, appCard, \
    aiDraw

if __name__ == '__main__':
    with open('config.json','r',encoding='utf-8') as fp:
        data=fp.read()
    config=json.loads(data)
    qq=int(config.get('botQQ'))
    key=config.get("vertify_key")
    port= int(config.get("port"))
    bot = Mirai(qq, adapter=WebSocketAdapter(
        verify_key=key, host='localhost', port=port
    ))
    botName = config.get('botName')
    master=int(config.get('master'))


    #芝士logger
    logger=newLogger()

    #读取api列表
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    sizhiKey=result.get("siZhiAi")
    proxy=result.get("proxy")
    berturl=result.get("bert_colab")
    moderate=result.get("moderate")
    nasa_api=result.get("nasa_api")
    chatglm=result.get("chatGLM")

    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        resulta = yaml.load(f.read(), Loader=yaml.FullLoader)
    pandora = resulta.get("chatGLM").get("model")
    voicegg = resulta.get("voicegenerate")
    logger.info("读取到apiKey列表")



    @bot.on(GroupMessage)
    async def systemiiiiii(event: GroupMessage):
        if str(event.message_chain) == ".system" and event.sender.id == master:
            infof=get_system_info()
            await bot.send(event,infof)
    @bot.on(FriendMessage)
    async def systemiiiiii1(event: FriendMessage):
        if str(event.message_chain) == ".system" and event.sender.id == master:
            infof=get_system_info()
            await bot.send(event,infof)
    global notice
    notice=0
    @bot.on(GroupMessage)
    async def unlockNotice(event:GroupMessage):
        global notice
        if str(event.message_chain)=="notice" and event.sender.id==master:

            await bot.send(event,"请发送要推送的消息")
            notice = 1
        if str(event.message_chain).startswith("/sub") or str(event.message_chain).startswith("/unsub"):

            await bot.send(event,"该指令可能已经失效\n请发送@"+str(botName)+"帮助\n以查看菜单3/B站动态推送v2")
    @bot.on(GroupMessage)
    async def sendNotice(event:GroupMessage):
        global notice
        if notice==1 and event.sender.id==master:
            notice=0
            file = open('data/music/groups.txt', 'r')
            js = file.read()
            severGroupsa = json.loads(js)
            dat = []
            for i in severGroupsa:
                await sleep1(random.randint(2,10))
                logger.info("向群："+i +" 推送公告")
                try:
                    if event.message_chain.count(Image):
                        await bot.send_group_message(int(i),(event.message_chain+"\n随机码："+random_str()))
                    else:
                        try:
                            await bot.send_group_message(int(i), (event.message_chain +"\n随机码：" + random_str()))
                        except:
                            await bot.send_group_message(int(i), event.message_chain)
                except:
                    logger.error("不存在的群："+str(i))
                    dat.append(str(i))
                    continue
            logger.warning("清除无效群")
            for i in dat:
                severGroupsa.pop(i)
            newData = json.dumps(severGroupsa)
            with open('data/music/groups.txt', 'w') as fp:
                fp.write(newData)







    # 菜单
    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        if ('帮助' in str(event.message_chain) or '菜单' in str(event.message_chain) or "help" in str(event.message_chain)) and At(bot.qq) in event.message_chain:
            logger.info("获取菜单")
            await bot.send(event, [Image(path='data/fonts/help1.png'),Image(path='data/fonts/help2.png'),Image(path='data/fonts/help3.png'),Image(path='data/fonts/help4.png')])
            await bot.send(event, '这是' + botName + '的功能列表\nヾ(≧▽≦*)o\n发送 pet 以查看制图功能列表')
        if '制图' in str(event.message_chain) and At(bot.qq) in event.message_chain :
            logger.info("制图菜单")
            await bot.send(event, '发送 pet 以查看制图功能列表')



    @bot.on(Startup)
    async def clearCache(event:Startup):
        logger.info("执行清理缓存操作")
        ls1 = os.listdir("data/pictures/avatars")
        for i in ls1:
            try:
                if i.endswith(".py"):
                    continue
                os.remove("data/pictures/avatars/" + i)
            except:
                continue
        logger.info("清理头像缓存完成")
        ls1 = os.listdir("data/pictures/cache")
        for i in ls1:
            try:
                if i.endswith(".py"):
                    continue
                os.remove("data/pictures/cache/" + i)
            except:
                continue
        logger.info("清理图片缓存完成")
        ls1 = os.listdir("data/voices")
        for i in ls1:
            try:
                if i.endswith(".py"):
                    continue
                os.remove("data/voices/" + i)
            except:
                continue
        logger.info("清理语音缓存完成")
        logger.info("请定期执行launcher.exe或者Manyana/更新脚本.bat 的更新功能以获取最新版Manyana")

        file = open('data/music/groups.txt', 'r')
        js = file.read()
        severGroupsa = json.loads(js)
        logger.info('已读取服务群聊:' + str(len(severGroupsa)) + '个')


        with open('data/userData.yaml', 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        global userdict
        userdict = data
        try:
            userCount = userdict.keys()
            logger.info('已读取有记录用户:' + str(len(userCount)) + '个')
            if os.path.exists("./temp"):
                shutil.copyfile('data/userData.yaml', 'temp/userData_back.yaml')

            else:
                os.mkdir("./temp")
                shutil.copyfile('data/userData.yaml', 'temp/userData_back.yaml')
            logger.info("已备份用户数据文件至temp文件夹下")
        except Exception as e:
            logger.error(e)
            logger.error("用户数据文件出错，自动使用备用文件替换")
            shutil.copyfile('temp/userData_back.yaml','data/userData.yaml')
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            global userdict
            userdict = data

        # 修改为你bot的名字
        logger.info('botName:' + botName + '     |     master:' + str(master))
        time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await bot.send_friend_message(master,time1 + '\n已读取服务群聊:' + str(len(severGroupsa)) + '个')
        await bot.send_friend_message(master,time1 + '\n已读取有记录用户:' + str(len(userCount)) + '个')
        await bot.send_friend_message(master,time1 + '\n功能已加载完毕，欢迎使用')
        infof = get_system_info()
        await bot.send_friend_message(master,"当前系统信息如下，可使用.system指令查看当前系统信息")
        await bot.send_friend_message(master, infof)


   # logger.info("如果遇到卡顿请按ctrl+c | 如成功更新了某些文件，请重启main.py以应用更新")

    '''try:
        logger.warning("如果出现 Merge冲突 请重命名本地的对应文件，拉取后将你的数据重新导入")
        logger.warning("merge冲突示例：Your local changes to the following files would be overwritten by merge:")
        os.system("git pull https://github.com/avilliai/Manyana.git")
        logger.info("over")
    except:
        logger.error("取消github更新")'''

    logger.info("当前语音合成模式："+voicegg)
    if pandora=="pandora":
        try:
            subprocess.Popen(["pandora", "-t", "config/token.txt","-s", "127.0.0.1:23459", "-p", proxy])
        except:
            pass
    else:
        pass
    def startVer():
        file_object = open("data/fonts/mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)
    @bot.on(Shutdown)
    async def efff(event: Shutdown):
        raise SystemExit()

    #current_dir = os.path.dirname(os.path.abspath(__file__))
    voiceReply.main(bot, master,logger)  # 语音生成
    if proxy != "":
        try:
            # logger.info("开发过程中暂不启动poe-api")
            aiReply.main(bot, master, logger)  # poe-api
        except Exception as e:
            logger.error(e)
        imgSearch.main(bot, result.get("sauceno-api"), result.get("proxy"), logger)
    else:
        logger.warning("未设置代理，禁用poe-api与搜图")
    nudgeReply.main(bot, master,  logger,berturl,proxy)  # 戳一戳
    extraParts.main(bot, result.get("weatherXinZhi"), nasa_api, proxy, logger)  # 额外小功能
    wReply.main(bot, config, sizhiKey,  logger)
    wikiHelper.main(bot, logger)
    userSign.main(bot, result.get("weatherXinZhi"), master, config, logger)
    groupManager.main(bot, config, moderate, logger)
    PicRandom.main(bot, proxy, logger)
    musicShare.main(bot, master, botName, logger)
    LiveMonitor.main(bot, master, botName, logger)
    bertVits2.main(bot,  logger,berturl,proxy)
    aronaapi.main(bot,logger)
    scheduledTasks.main(bot,proxy,nasa_api,logger)
    groupGames.main(bot,logger)
    musicpick.main(bot,logger)
    sovits2.main(bot,logger)
    appCard.main(bot,logger)
    aiDraw.main(bot,logger)
    #gemini_ai.main(bot,logger,master)
    startVer()
    bot.run()

