# -*- coding:utf-8 -*-
import asyncio
import datetime
import json

import os
import subprocess
from random import random

import yaml
from mirai import Mirai, FriendMessage, WebSocketAdapter, Poke, GroupMessage
from mirai.models import NudgeEvent

from plugins.newLogger import newLogger
from run import poeAi, voiceReply, nudgeReply, blueArchiveHelper

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
    logger.info("读取到apiKey列表")


    @bot.on(GroupMessage)
    async def test112(event:GroupMessage):
        if str(event.message_chain)=="zxc":
            await bot.send_group_message(event.group.id,Poke(name="ChuoYiChuo"))





    subprocess.Popen(["venv/Scripts/python.exe", "flask_voice.py"],cwd="vits")
    #asyncio.run(os.system("cd vits && python flask_voice.py"))
    logger.info(" 语音合成sever启动....")

    def startVer():
        file_object = open("config/mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)

    voiceReply.main(bot,app_id,app_key,logger)#语音生成
    try:
        #logger.info("开发过程中暂不启动poe-api")
        poeAi.main(bot,master,result.get("poe-api"),result.get("proxy"),logger)#poe-api
    except:
        logger.error("poe-api启动失败")
    nudgeReply.main(bot,logger)

    blueArchiveHelper.main(bot,app_id,app_key,logger)
    startVer()

    bot.run()