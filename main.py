# -*- coding:utf-8 -*-
import asyncio
import datetime
import json

import os
import random
import subprocess
from asyncio import sleep as sleep1
from time import sleep

import httpx
import requests
import yaml
from mirai import Mirai, FriendMessage, WebSocketAdapter, Poke, GroupMessage, Image, Voice, At, Startup
from mirai.models import NudgeEvent, MemberHonorChangeEvent, MemberCardChangeEvent, MemberSpecialTitleChangeEvent

from plugins.RandomStr import random_str
from plugins.newLogger import newLogger
from plugins.translater import translate
from run import aiReply, voiceReply, nudgeReply, wikiHelper, imgSearch, extraParts, wReply, userSign, groupManager, \
    PicRandom, musicShare, LiveMonitor

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
    app_id = result.get("youdao").get("app_id")
    app_key=result.get("youdao").get("app_key")#有道翻译api
    sizhiKey=result.get("siZhiAi")
    proxy=result.get("proxy")
    moderate=result.get("moderate")
    nasa_api=result.get("nasa_api")
    chatglm=result.get("chatGLM")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        resulta = yaml.load(f.read(), Loader=yaml.FullLoader)
    pandora=resulta.get("pandora")

    logger.info("读取到apiKey列表")

    global notice
    notice=0
    @bot.on(GroupMessage)
    async def unlockNotice(event:GroupMessage):
        global notice
        if str(event.message_chain)=="notice" and event.sender.id==master:

            await bot.send(event,"请发送要推送的消息")
            notice = 1
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
        if ('帮助' in str(event.message_chain) or '菜单' in str(event.message_chain)) and At(bot.qq) in event.message_chain:
            logger.info("获取菜单")
            await bot.send(event, Image(path='config/help1.png'))
            await bot.send(event, Image(path='config/help2.png'))
            await bot.send(event, '这是' + botName + '的功能列表\nヾ(≧▽≦*)o')
        if '制图' in str(event.message_chain) and At(bot.qq) in event.message_chain :
            logger.info("菜单")
            await bot.send(event, Image(path='config/picMaker.png'))
            await bot.send(event, '这是' + botName + '的制图功能列表\nヾ(≧▽≦*)o')


    @bot.on(Startup)
    async def clearCache(event:Startup):
        logger.info("执行清理缓存操作")
        ls1 = os.listdir("data/pictures/avatars")
        for i in ls1:
            try:
                os.remove("data/pictures/avatars/" + i)
            except:
                continue
        logger.info("清理头像缓存完成")
        ls1 = os.listdir("data/pictures/cache")
        for i in ls1:
            try:
                os.remove("data/pictures/cache/" + i)
            except:
                continue
        logger.info("清理图片缓存完成")
        ls1 = os.listdir("data/voices")
        for i in ls1:
            try:
                os.remove("data/voices/" + i)
            except:
                continue
        logger.info("清理语音缓存完成")

        file = open('data/music/groups.txt', 'r')
        js = file.read()
        severGroupsa = json.loads(js)
        logger.info('已读取服务群聊:' + str(len(severGroupsa)) + '个')
        with open('data/userData.yaml', 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        global userdict
        userdict = data
        userCount = userdict.keys()
        logger.info('已读取有记录用户:' + str(len(userCount)) + '个')

        # 修改为你bot的名字
        logger.info('botName:' + botName + '     |     master:' + str(master))
        time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await bot.send_friend_message(master,time1 + '\n已读取服务群聊:' + str(len(severGroupsa)) + '个')
        await bot.send_friend_message(master,time1 + '\n已读取有记录用户:' + str(len(userCount)) + '个')
        await bot.send_friend_message(master,time1 + '\n功能已加载完毕，欢迎使用')


    logger.warning("请定期通过setUp.py进行更新")
   # logger.info("如果遇到卡顿请按ctrl+c | 如成功更新了某些文件，请重启main.py以应用更新")

    '''try:
        logger.warning("如果出现 Merge冲突 请重命名本地的对应文件，拉取后将你的数据重新导入")
        logger.warning("merge冲突示例：Your local changes to the following files would be overwritten by merge:")
        os.system("git pull https://github.com/avilliai/Manyana.git")
        logger.info("over")
    except:
        logger.error("取消github更新")'''

    subprocess.Popen(["python.exe", "flask_voice.py"],cwd="vits")
    #asyncio.run(os.system("cd vits && python flask_voice.py"))
    logger.info(" 语音合成sever启动....")
    if pandora:
        try:
            subprocess.Popen(["pandora", "-t", "config/token.txt","-s", "127.0.0.1:23459", "-p", proxy])
        except:
            logger.error("pandora启动失败")
    else:
        logger.warning("未启用pandora，如需启用请修改setting.yaml并完成相关配置")
    def startVer():
        file_object = open("config/mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)


    voiceReply.main(bot, master, app_id, app_key, logger)  # 语音生成
    if proxy != "":
        try:
            # logger.info("开发过程中暂不启动poe-api")
            aiReply.main(bot, master, result.get("poe-api"),chatglm, result.get("proxy"), logger)  # poe-api
        except:
            logger.error("poe-api启动失败")
        imgSearch.main(bot, result.get("sauceno-api"), result.get("proxy"), logger)
    else:
        logger.warning("未设置代理，禁用poe-api与搜图")
    nudgeReply.main(bot, master, app_id, app_key, logger)  # 戳一戳
    extraParts.main(bot, result.get("weatherXinZhi"), app_id, app_key, nasa_api, proxy, logger)  # 额外小功能
    wReply.main(bot, config, sizhiKey, app_id, app_key, logger)
    wikiHelper.main(bot, app_id, app_key, logger)
    userSign.main(bot, result.get("weatherXinZhi"), master, config, logger)
    groupManager.main(bot, config, moderate, logger)
    PicRandom.main(bot, proxy, logger)
    musicShare.main(bot, master, botName, logger)
    LiveMonitor.main(bot, master, botName, logger)

    startVer()
    bot.run()

