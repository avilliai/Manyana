# -*- coding:utf-8 -*-
import datetime

import os
import random
import shutil
import sys

from asyncio import sleep as sleep1

#下面的两行是launcher启动必要设置，勿动。
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yaml
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage, Shutdown

from plugins.RandomStr import random_str
from plugins.newLogger import newLogger
from plugins.systeminfo import get_system_info
from run import aiReply, voiceReply, nudgeReply, wikiHelper, imgSearch, extraParts, wReply, userSign, groupManager, \
    musicShare, LiveMonitor, aronaapi, groupGames, musicpick, scheduledTasks, appCard, aiDraw, starRail,bangumi

if __name__ == '__main__':
    with open('config.json', 'r', encoding='utf-8') as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)

    config = data
    qq = int(config.get('botQQ'))
    key = str(config.get("vertify_key"))
    port = int(config.get("port"))

    bot = Mirai(qq, adapter=WebSocketAdapter(
        verify_key=key, host='localhost', port=port
    ))
    botName = config.get('botName')
    master = int(config.get('master'))
    # 芝士logger
    logger = newLogger()

    # 读取api列表
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    sizhiKey = result.get("siZhiAi")
    proxy = result.get("proxy")
    berturl = result.get("bert_colab")
    moderate = result.get("moderate")
    nasa_api = result.get("nasa_api")
    chatglm = result.get("chatGLM")

    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        resulta = yaml.load(f.read(), Loader=yaml.FullLoader)
    pandora = resulta.get("chatGLM").get("model")
    voicegg = resulta.get("语音功能设置").get("voicegenerate")
    logger.info("读取到apiKey列表")


    @bot.on(GroupMessage)
    async def systemiiiiii(event: GroupMessage):
        if str(event.message_chain) == ".system" and event.sender.id == master:
            infof = get_system_info()
            await bot.send(event, infof)


    @bot.on(FriendMessage)
    async def systemiiiiii1(event: FriendMessage):
        if str(event.message_chain) == ".system" and event.sender.id == master:
            infof = get_system_info()
            await bot.send(event, infof)


    global notice
    notice = 0


    @bot.on(GroupMessage)
    async def unlockNotice(event: GroupMessage):
        global notice
        if str(event.message_chain) == "notice" and event.sender.id == master:
            await bot.send(event, "请发送要推送的消息")
            notice = 1
        if str(event.message_chain).startswith("/sub") or str(event.message_chain).startswith("/unsub"):
            await bot.send(event, "该指令可能已经失效\n请发送@" + str(botName) + "帮助\n以查看菜单3/B站动态推送v2")


    @bot.on(GroupMessage)
    async def sendNotice(event: GroupMessage):
        global notice
        if notice == 1 and event.sender.id == master:
            notice = 0
            asf = await bot.group_list()
            await bot.send(event, "收到，正在推送......")
            # print(asf.data)
            for i in asf.data:
                # print(i.id, i.name)
                await sleep1(random.randint(2, 10))
                logger.info("向群：" + i.name + " 推送公告")
                try:
                    if event.message_chain.count(Image):
                        await bot.send_group_message(int(i.id), event.message_chain)
                    else:
                        try:
                            await bot.send_group_message(int(i.id), (
                                    event.message_chain + "\n==============\n随机码：" + random_str()))
                        except:
                            await bot.send_group_message(int(i.id), event.message_chain)
                except:
                    logger.error("无效的群：" + str(i))
                    continue


    # 菜单
    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        if ('帮助' in str(event.message_chain) or '菜单' in str(event.message_chain) or "功能" in str(
                event.message_chain)) and At(bot.qq) in event.message_chain:
            logger.info("获取菜单")
            s = [Image(path='data/fonts/help1.png'), Image(path='data/fonts/help2.png'),
                 Image(path='data/fonts/help3.png')]
            for i in s:
                await bot.send(event, i)
            await bot.send(event, '这是' + botName + '的功能列表\nヾ(≧▽≦*)o\n发送 pet 以查看制图功能列表')
        if '制图' in str(event.message_chain) and At(bot.qq) in event.message_chain:
            logger.info("制图菜单")
            await bot.send(event, '发送 pet 以查看制图功能列表')


    @bot.on(Startup)
    async def clearCache(event: Startup):

        logger.info("执行清理缓存操作")
        aimdir=["data/pictures/avatars","data/pictures/cache","data/pictures/new_sign_Image","data/voices"]
        for ib in aimdir:
            ls1 = os.listdir(ib)
            for i in ls1:
                try:
                    if i.endswith(".py"):
                        continue
                    if i.endswith("zYz.png"):
                        continue
                    os.remove(f"{ib}/" + i)
                except:
                    continue
        logger.info("清理缓存完成")
        logger.info("请定期执行launcher.exe的更新功能以获取最新版Manyana")

        asf = await bot.group_list()
        #print(asf.data)
        logger.info('已读取服务群聊:' + str(len(asf.data)) + '个')

        with open('data/userData.yaml', 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        global userdict
        userdict = data
        try:
            userCount = userdict.keys()
            logger.info('已读取有记录用户:' + str(len(userCount)) + '个')
            if os.path.exists("./temp"):
                shutil.copyfile('data/userData.yaml', 'temp/userData_back.yaml')
                shutil.copyfile('data/chatGLMData.yaml', 'temp/chatGLMData_back.yaml')
            else:
                os.mkdir("./temp")
                shutil.copyfile('data/userData.yaml', 'temp/userData_back.yaml')
                shutil.copyfile('data/chatGLMData.yaml', 'temp/chatGLMData_back.yaml')
            logger.info("已备份用户数据文件至temp文件夹下")
        except Exception as e:
            logger.error(e)
            logger.error("用户数据文件出错，自动使用备用文件替换")
            shutil.copyfile('temp/userData_back.yaml', 'data/userData.yaml')
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            userdict = data

        # 修改为你bot的名字
        logger.info('botName:' + botName + '     |     master:' + str(master))
        time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await bot.send_friend_message(master, time1 + '\n已读取服务群聊:' + str(len(asf.data)) + '个')
        await bot.send_friend_message(master, time1 + '\n已读取有记录用户:' + str(len(userCount)) + '个')
        await bot.send_friend_message(master, time1 + '\n功能已加载完毕，欢迎使用')
        await bot.send_friend_message(master, Image(path="data/fonts/master.png"))

    logger.info("当前语音合成模式：" + voicegg)


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


    # current_dir = os.path.dirname(os.path.abspath(__file__))
    voiceReply.main(bot, master, logger)  # 语音生成

    aiReply.main(bot, master, logger)  # poe-api
    imgSearch.main(bot, result.get("sauceno-api"), result.get("proxy"), logger)

    nudgeReply.main(bot, master, logger, berturl, proxy)  # 戳一戳
    extraParts.main(bot, logger)  # 额外小功能
    wReply.main(bot, config, sizhiKey, logger)
    wikiHelper.main(bot, logger)
    userSign.main(bot, result.get("weatherXinZhi"), master, config, logger)
    groupManager.main(bot, config, moderate, logger)
    musicShare.main(bot, master, botName, logger)
    LiveMonitor.main(bot, master, botName, logger)
    aronaapi.main(bot, logger)
    scheduledTasks.main(bot, proxy, nasa_api, logger)
    groupGames.main(bot, logger)
    musicpick.main(bot, logger)
    appCard.main(bot, logger)
    aiDraw.main(bot, logger)
    starRail.main(bot, logger)
    bangumi.main(bot,logger)
    #gemini_ai.main(bot,logger,master)
    startVer()
    bot.run(asgi_server=None)
