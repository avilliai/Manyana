# -*- coding: utf-8 -*-
import asyncio
import json
import os
import random
import re
import uuid
from asyncio import sleep
import google.generativeai as genai

import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
import threading
from asyncio import sleep
from plugins.PandoraChatGPT import ask_chatgpt
from plugins.RandomStr import random_str
from plugins.chatGLMonline import chatGLM1
from plugins.googleGemini import geminirep

from plugins.translater import translate
from plugins.vitsGenerate import taffySayTest, sovits, edgetts, voiceGenerate, outVits



class CListen(threading.Thread):
    def __init__(self, loop):
        threading.Thread.__init__(self)
        self.mLoop = loop

    def run(self):
        asyncio.set_event_loop(self.mLoop)  # 在新线程中开启一个事件循环

        self.mLoop.run_forever()
def main(bot,logger,master):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    app_id=resulttr.get("youdao").get("app_id")
    app_key = resulttr.get("youdao").get("app_key")
    geminiapikey=resulttr.get("gemini")
    proxy=resulttr.get("proxy")
    berturl=resulttr.get("bert_colab")
    os.environ["http_proxy"] = proxy
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        rte = yaml.load(f.read(), Loader=yaml.FullLoader)

    with open('data/GeminiData.yaml', 'r', encoding='utf-8') as f:
        cha = yaml.load(f.read(), Loader=yaml.FullLoader)
    global GeminiData
    GeminiData=cha


    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    chineseVoiceRate=result.get("wReply").get("chineseVoiceRate")
    voicegg=result.get("voicegenerate")
    trustDays=result.get("trustDays")
    glmReply = result.get("chatGLM").get("glmReply")
    privateGlmReply=result.get("chatGLM").get("privateGlmReply")
    trustglmReply = result.get("chatGLM").get("trustglmReply")
    context= result.get("chatGLM").get("context")
    maxPrompt = result.get("chatGLM").get("maxPrompt")
    turnMessage=result.get("wReply").get("turnMessage")
    maxTextLen = result.get("chatGLM").get("maxLen")
    voiceRate = result.get("chatGLM").get("voiceRate")
    speaker = result.get("chatGLM").get("speaker")
    withText=result.get("chatGLM").get("withText")
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    global userdict
    userdict = data
    trustUser = []
    for i in userdict.keys():
        data = userdict.get(i)
        times = int(str(data.get('sts')))
        if times > trustDays:
            trustUser.append(str(i))

    logger.info('chatglm部分已读取信任用户' + str(len(trustUser)) + '个')

    #线程预备
    newLoop = asyncio.new_event_loop()
    listen = CListen(newLoop)
    listen.setDaemon(True)
    listen.start()




    @bot.on(Startup)
    async def upDate(event: Startup):
        while True:
            await sleep(60)
            with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
                result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
            global chatGLMapikeys
            chatGLMapikeys = result222
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            global trustUser
            global userdict
            userdict = data
            trustUser = []
            for i in userdict.keys():
                data = userdict.get(i)
                times = int(str(data.get('sts')))
                if times > trustDays:
                    trustUser.append(str(i))
            logger.info('已读取信任用户' + str(len(trustUser)) + '个')


    #群内chatGLM回复
    @bot.on(GroupMessage)
    async def atReply(event: GroupMessage):
        global trustUser,GeminiData
        if str(event.message_chain).startswith("/g"):
            text = str(event.message_chain).replace("@" + str(bot.qq) + "", '').replace(" ","").replace("/g","")
            logger.info("gemini开始运行")
            if text=="" or text==" ":
                text="在吗"
            #构建新的prompt
            tep={"role": "user","parts": [text]}
            #print(type(tep))
            #获取以往的prompt
            if event.sender.id in GeminiData and context==True:
                prompt=GeminiData.get(event.sender.id)
                prompt.append({"role": "user",'parts': [text]})

            #没有该用户，以本次对话作为prompt
            else:
                await bot.send(event, "即将开始对话，请注意，如果遇到对话异常，请发送 /cGemini 以清理对话记录(不用艾特)",True)
                prompt=[tep]
                GeminiData[event.sender.id] =prompt
            logger.info("gemini接收提问:" + text)
            try:
                #logger.info(geminiapikey)
                r=await geminirep(ak=geminiapikey,messages=prompt)
                # 更新该用户prompt
                prompt.append({"role": 'model', "parts": [r]})
                # 超过10，移除第一个元素
                GeminiData[event.sender.id] = prompt
                # 写入文件
                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(GeminiData, file, allow_unicode=True)
                await bot.send(event,r)
                #asyncio.run_coroutine_threadsafe(asyncgemini(geminiapikey,prompt, event,text), newLoop)
                #st1 = await chatGLM(selfApiKey, meta1, prompt)


            except Exception as e:
                logger.error(e)
                await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")
    
    #用于chatGLM清除本地缓存
    @bot.on(GroupMessage)
    async def clearPrompt(event:GroupMessage):
        global GeminiData
        if str(event.message_chain)=="/cGemini":
            try:
                GeminiData.pop(event.sender.id)
                # 写入文件
                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(GeminiData, file, allow_unicode=True)
                await bot.send(event,"已清除近期记忆")
            except:
                await bot.send(event,"清理缓存出错，无本地对话记录")
        if str(event.message_chain)=="/allclear" and event.sender.id==master:
            try:
                GeminiData={"f":"hhh"}
                #GeminiData.pop(event.sender.id)
                # 写入文件
                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(GeminiData, file, allow_unicode=True)
                await bot.send(event,"已清除所有用户的prompt")
            except:
                await bot.send(event,"清理缓存出错，无本地对话记录")


    # 创建一个异步函数
    async def asyncgemini(apiKey,prompt,event,text):
        global GeminiData

        loop = asyncio.get_event_loop()
        # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
        # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
        # 第二个参数是同步函数名，后面跟着任何你需要传递的参数

        st1 = await loop.run_in_executor(None, geminirep,apiKey,prompt)

        logger.info("chatGLM:" + st1)
        if len(st1)<maxTextLen and random.randint(0,100)<voiceRate and event.type!='FriendMessage':
            data1={}
            data1['speaker']=speaker

            #print(path)
            st8 = re.sub(r"（[^）]*）", "", st1)  # 使用r前缀表示原始字符串，避免转义字符的问题
            data1["text"] = st8

            if voicegg=="bert_vits2":
                logger.info("调用bert_vits语音回复")
                try:
                    path=await taffySayTest(data1,berturl,proxy)
                    await bot.send(event, Voice(path=path))
                    if withText==True:
                        await bot.send(event,st1, True)
                except:
                    logger.error("bert_vits2语音合成服务已关闭，请重新运行")
                    await bot.send(event, st1, True)
            elif voicegg=="so-vits":
                logger.info("调用so_vits语音回复")
                try:
                    path=await sovits(data1)
                    await bot.send(event, Voice(path=path))
                    if withText==True:
                        await bot.send(event,st1, True)
                except:
                    logger.error("sovits语音合成服务已关闭，请重新运行")
                    await bot.send(event, st1, True)
            elif voicegg=="outVits":
                logger.info("调用out_vits语音回复")
                try:
                    path=await outVits(data1)
                    await bot.send(event, Voice(path=path))
                    if withText==True:
                        await bot.send(event,st1, True)
                except:
                    logger.error("sovits语音合成服务已关闭，请重新运行")
                    await bot.send(event, st1, True)
            elif voicegg=="edgetts":
                logger.info("调用edgetts语音回复")
                try:
                    path=await edgetts(data1)
                    await bot.send(event, Voice(path=path))
                    if withText==True:
                        await bot.send(event,st1, True)
                except Exception as e:
                    await bot.send(event, st1, True)
                    logger.error(e)
                    logger.error("edgetts语音合成服务已关闭，请重新运行")
            elif voicegg=="vits":
                logger.info("调用vits语音回复")
                try:
                    path = 'data/voices/' + random_str() + '.wav'
                    if random.randint(1, 100) > chineseVoiceRate:
                        text = await translate(str(st8), app_id, app_key)
                        tex = '[JA]' + text + '[JA]'
                    else:
                        tex = "[ZH]" + st8 + "[ZH]"
                    logger.info("启动文本转语音：text: " + tex + " path: " + path)
                    spe = rte.get("defaultModel").get("speaker")
                    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                        resulte = yaml.load(f.read(), Loader=yaml.FullLoader)
                    modelSelect = resulte.get("defaultModel").get("modelSelect")
                    await voiceGenerate({"text": tex, "out": path, "speaker": spe, "modelSelect": modelSelect})
                    await bot.send(event, Voice(path=path))
                    if withText==True:
                        await bot.send(event,st1, True)
                except:
                    logger.error("vits服务运行出错，请检查是否开启或检查配置")
                    await bot.send(event, st1, True)

        else:

            await bot.send(event, st1, True)



        if turnMessage==True and event.type=='FriendMessage' and event.sender.id!=master:
            await bot.send_friend_message(int(master),"chatGLM接收消息：\n来源:"+str(event.sender.id)+"\n提问:"+text+"\n回复:"+st1)

        if context == True:
            # 更新该用户prompt
            prompt.append({"role": 'model', "parts": [st1]})
            # 超过10，移除第一个元素
            GeminiData[event.sender.id] = prompt
            # 写入文件
            with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(GeminiData, file, allow_unicode=True)


    # 运行异步函数




