# -*- coding: utf-8 -*-
import asyncio
import json
import os
import random
import re
import uuid
from asyncio import sleep

import httpx
#import poe
import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
import threading
from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
import zhipuai

from plugins.RandomStr import random_str
from plugins.chatGLMonline import chatGLM1, glm4
from plugins.cozeBot import cozeBotRep
from plugins.googleGemini import geminirep
from plugins.gptOfficial import gptOfficial,gptUnofficial

from plugins.rwkvHelper import rwkvHelper
from plugins.translater import translate
from plugins.vitsGenerate import superVG, voiceGenerate
from plugins.wReply.mohuReply import mohuaddReplys
from plugins.yubanGPT import lolimigpt, lolimigpt2


#1
class CListen(threading.Thread):
    def __init__(self, loop):
        threading.Thread.__init__(self)
        self.mLoop = loop

    def run(self):
        asyncio.set_event_loop(self.mLoop)  # 在新线程中开启一个事件循环

        self.mLoop.run_forever()
def main(bot, master, logger):
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        resul = yaml.load(f.read(), Loader=yaml.FullLoader)
    global trustG
    trustG = resul.get("trustGroups")
    #读取个性化角色设定
    with open('data/chatGLMCharacters.yaml', 'r', encoding='utf-8') as f:
        result2223 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMCharacters
    chatGLMCharacters = result2223
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    CoziUrl=resulttr.get("cozi")
    gptdev=resulttr.get("gpt3.5-dev")
    geminiapikey=resulttr.get("gemini")
    proxy=resulttr.get("proxy")
    berturl=resulttr.get("bert_colab")
    os.environ["http_proxy"] = proxy
    gptkeys=resulttr.get("openai-keys")
    chatGLM_api_key=resulttr.get("chatGLM")
    with open('data/GeminiData.yaml', 'r', encoding='utf-8') as f:
        cha0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global GeminiData
    GeminiData=cha0

    with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
        result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMapikeys
    chatGLMapikeys = result222


    with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
        cha = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMData
    chatGLMData=cha
    #logger.info(chatGLMData)
    with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
        noRes1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    noRes=noRes1.get("noRes")

    global totallink
    totallink = False
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    chineseVoiceRate=result.get("wReply").get("chineseVoiceRate")
    voicegg=result.get("voicegenerate")
    trustDays=result.get("trustDays")
    RateIfUnavailable=result.get("RateIfUnavailable")
    glmReply = result.get("chatGLM").get("glmReply")
    privateGlmReply=result.get("chatGLM").get("privateGlmReply")
    replyModel = result.get("chatGLM").get("model")
    trustglmReply = result.get("chatGLM").get("trustglmReply")
    meta = result.get("chatGLM").get("bot_info").get("default")
    context= result.get("chatGLM").get("context")
    maxPrompt = result.get("chatGLM").get("maxPrompt")
    voiceLangType = str(result.get("chatGLM").get("voiceLangType"))
    allcharacters=result.get("chatGLM").get("bot_info")
    turnMessage=result.get("wReply").get("turnMessage")
    maxTextLen = result.get("chatGLM").get("maxLen")
    voiceRate = result.get("chatGLM").get("voiceRate")
    speaker = result.get("chatGLM").get("speaker")
    withText=result.get("chatGLM").get("withText")

    with open('config.json', 'r', encoding='utf-8') as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)
    config = data
    mainGroup = int(config.get("mainGroup"))
    botName = config.get("botName")
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    global userdict
    userdict = data
    trustUser = []
    for i in userdict.keys():
        data = userdict.get(i)
        try:
            times = int(str(data.get('sts')))
            if times > trustDays:
                trustUser.append(str(i))

        except Exception as e:
            logger.error(f"用户{i}的sts数值出错，请打开data/userData.yaml检查，将其修改为正常数值")
    logger.info('chatglm部分已读取信任用户' + str(len(trustUser)) + '个')

    with open('config/chatGLMSingelUser.yaml', 'r', encoding='utf-8') as f:
        result224 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMsingelUserKey
    chatGLMsingelUserKey=result224

    global coziData
    coziData={}
    #线程预备
    newLoop = asyncio.new_event_loop()
    listen = CListen(newLoop)
    listen.setDaemon(True)
    listen.start()
    #私聊使用chatGLM,对信任用户或配置了apiKey的用户开启
    @bot.on(FriendMessage)
    async def GLMFriendChat(event:FriendMessage):
        #用非常丑陋的复制粘贴临时解决bug，这下成石山代码了
        global chatGLMData,chatGLMCharacters,trustUser,chatGLMsingelUserKey,userdict,GeminiData,coziData
        text = str(event.message_chain)
        if event.sender.id==master:
            noresm=["群列表","/bl","退群#","/quit"]
            for saa in noresm:
                if text == saa or text.startswith(saa):
                    logger.warning("与屏蔽词匹配，不回复")
                    return
        if event.sender.id in chatGLMCharacters:
            #print("在")
            print(chatGLMCharacters.get(event.sender.id),type(chatGLMCharacters.get(event.sender.id)))
            if type(chatGLMCharacters.get(event.sender.id))==dict:
                #如果用户有自己的key
                if event.sender.id in chatGLMsingelUserKey:
                    selfApiKey=chatGLMsingelUserKey.get(event.sender.id)
                    #构建prompt
                #或者开启了信任用户回复且为信任用户
                elif str(event.sender.id) in trustUser and trustglmReply==True:
                    logger.info("信任用户进行chatGLM提问")
                    selfApiKey=chatGLM_api_key
                elif privateGlmReply==True:
                    selfApiKey = chatGLM_api_key
                else:
                    return
                if str(event.message_chain) == "/clearGLM" or str(event.message_chain) == "/clear":
                    return
                text = str(event.message_chain)
                logger.info("私聊glm接收消息："+text)
                # 构建新的prompt
                tep = {"role": "user", "content": text}
                # print(type(tep))
                # 获取以往的prompt
                if event.sender.id in chatGLMData:
                    prompt = chatGLMData.get(event.sender.id)
                    prompt.append({"role": "user", "content": text})
                # 没有该用户，以本次对话作为prompt
                else:
                    await bot.send(event,"即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)")
                    prompt = [tep]
                    chatGLMData[event.sender.id] = prompt
                if event.sender.id in chatGLMCharacters:
                    meta1 = chatGLMCharacters.get(event.sender.id)
                else:
                    logger.warning("读取meta模板")
                    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                        resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                    meta1 = resy.get("chatGLM").get("bot_info").get("default")

                try:
                    setName = userdict.get(str(event.sender.id)).get("userName")
                except:
                    setName = event.sender.nickname
                if setName == None:
                    setName = event.sender.nickname

                meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
                meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
                meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca",botName)
                meta1["bot_name"] = botName

                try:
                    logger.info("当前meta:" + str(meta1))
                    #st1 = await chatGLM(selfApiKey, meta1, prompt)
                    asyncio.run_coroutine_threadsafe(asyncchatGLM(selfApiKey, meta1, prompt, event, setName, text), newLoop)

                except:
                    await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试\n或发送 @bot 可用角色模板 以更换其他模型")
            elif chatGLMCharacters.get(event.sender.id)=="Gemini":
                if str(event.message_chain)=="/cGemini" or str(event.message_chain)=="/clear":
                    return
                if privateGlmReply!=True:
                    return
                logger.info("gemini开始运行")
                text = str(event.message_chain)
                if text == "" or text == " ":
                    text = "在吗"

                geminichar=allcharacters.get("Gemini").replace("【bot】",botName).replace("【用户】", event.sender.nickname)
                # 构建新的prompt
                tep = {"role": "user", "parts": [text]}
                # print(type(tep))
                # 获取以往的prompt
                if event.sender.id in GeminiData and context == True:
                    prompt = GeminiData.get(event.sender.id)
                    prompt.append({"role": "user", 'parts': [text]})
                # 没有该用户，以本次对话作为prompt
                else:
                    await bot.send(event, "即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)", True)
                    prompt=[{"role": "user", "parts": [geminichar]},{"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]}]
                    prompt.append(tep)


                logger.info("gemini接收提问:" + text)
                try:
                    # logger.info(geminiapikey)
                    r = asyncio.run_coroutine_threadsafe(geminirep(ak=random.choice(geminiapikey), messages=prompt),
                                                         newLoop)
                    r = r.result()
                    # 更新该用户prompt
                    prompt.append({"role": 'model', "parts": [r]})
                    # 超过10，移除第一个元素
                    logger.info("gemini回复：" + r)
                    if len(prompt) > maxPrompt:
                        logger.error("gemini prompt超限，移除元素")
                        del prompt[2]
                        del prompt[2]
                    GeminiData[event.sender.id] = prompt
                    # 写入文件
                    with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(GeminiData, file, allow_unicode=True)
                    await bot.send(event, r)
                    # asyncio.run_coroutine_threadsafe(asyncgemini(geminiapikey,prompt, event,text), newLoop)
                    # st1 = await chatGLM(selfApiKey, meta1, prompt)
                except Exception as e:
                    logger.error(e)
                    GeminiData.pop(event.sender.id)
                    await bot.send(event, "gemini启动出错,请重试\n或发送 @bot 可用角色模板 以更换其他模型")
            else:
                if privateGlmReply!=True:
                    return
                await modelReply(event, chatGLMCharacters.get(event.sender.id))
        #判断模型类型
        elif replyModel=="characterglm":
            #如果用户有自己的key
            if event.sender.id in chatGLMsingelUserKey:
                selfApiKey=chatGLMsingelUserKey.get(event.sender.id)
                #构建prompt
            #或者开启了信任用户回复且为信任用户
            elif str(event.sender.id) in trustUser and trustglmReply==True:
                logger.info("信任用户进行chatGLM提问")
                selfApiKey=chatGLM_api_key
            elif privateGlmReply==True:
                selfApiKey = chatGLM_api_key
            else:
                return
            if str(event.message_chain) == "/clearGLM" or str(event.message_chain) == "/clear":
                return
            text = str(event.message_chain)
            logger.info("私聊glm接收消息："+text)
            # 构建新的prompt
            tep = {"role": "user", "content": text}
            # print(type(tep))
            # 获取以往的prompt
            if event.sender.id in chatGLMData:
                prompt = chatGLMData.get(event.sender.id)
                prompt.append({"role": "user", "content": text})
            # 没有该用户，以本次对话作为prompt
            else:
                await bot.send(event,"即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)")
                prompt = [tep]
                chatGLMData[event.sender.id] = prompt
            if event.sender.id in chatGLMCharacters:
                meta1 = chatGLMCharacters.get(event.sender.id)
            else:
                logger.warning("读取meta模板")
                with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                    resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                meta1 = resy.get("chatGLM").get("bot_info").get("default")

            try:
                setName = userdict.get(str(event.sender.id)).get("userName")
            except:
                setName = event.sender.nickname
            if setName == None:
                setName = event.sender.nickname

            meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
            meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
            meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca",botName)
            meta1["bot_name"] = botName

            try:
                logger.info("当前meta:" + str(meta1))
                #st1 = await chatGLM(selfApiKey, meta1, prompt)
                asyncio.run_coroutine_threadsafe(asyncchatGLM(selfApiKey, meta1, prompt, event, setName, text), newLoop)

            except:
                await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试\n或发送 @bot 可用角色模板 以更换其他模型")
        elif replyModel=="Gemini":
            if str(event.message_chain)=="/cGemini" or str(event.message_chain)=="/clear":
                return
            if privateGlmReply!=True:
                return
            logger.info("gemini开始运行")
            text = str(event.message_chain)
            if text == "" or text == " ":
                text = "在吗"
            geminichar=allcharacters.get("Gemini").replace("【bot】",botName).replace("【用户】", event.sender.nickname)
            # 构建新的prompt
            tep = {"role": "user", "parts": [text]}
            # print(type(tep))
            # 获取以往的prompt
            if event.sender.id in GeminiData and context == True:
                prompt = GeminiData.get(event.sender.id)
                prompt.append({"role": "user", 'parts': [text]})
                # 没有该用户，以本次对话作为prompt
            else:
                await bot.send(event, "即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)", True)
                prompt=[{"role": "user", "parts": [geminichar]},{"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]}]
                prompt.append(tep)


            logger.info("gemini接收提问:" + text)
            try:
                # logger.info(geminiapikey)
                r = asyncio.run_coroutine_threadsafe(geminirep(ak=random.choice(geminiapikey), messages=prompt),
                                                     newLoop)
                r = r.result()
                # 更新该用户prompt
                prompt.append({"role": 'model', "parts": [r]})
                # 超过10，移除第一个元素
                logger.info("gemini回复：" + r)
                if len(prompt) > maxPrompt:
                    logger.error("gemini prompt超限，移除元素")
                    del prompt[2]
                    del prompt[2]
                GeminiData[event.sender.id] = prompt
                # 写入文件
                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(GeminiData, file, allow_unicode=True)
                await bot.send(event, r)
                # asyncio.run_coroutine_threadsafe(asyncgemini(geminiapikey,prompt, event,text), newLoop)
                # st1 = await chatGLM(selfApiKey, meta1, prompt)
            except Exception as e:
                logger.error(e)
                GeminiData.pop(event.sender.id)
                await bot.send(event, "gemini启动出错,请重试\n或发送 @bot 可用角色模板 以更换其他模型")
        else:
            if privateGlmReply!=True:
                return
            await modelReply(event, replyModel)
    # 私聊中chatGLM清除本地缓存
    @bot.on(FriendMessage)
    async def clearPrompt(event: FriendMessage):
        global chatGLMData,GeminiData,coziData
        if str(event.message_chain) == "/clearGLM" or str(event.message_chain) =="/clear" or str(event.message_chain) == "/cGemini":
            try:
                chatGLMData.pop(event.sender.id)
                # 写入文件
                with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMData, file, allow_unicode=True)
                await bot.send(event,"已清除近期记忆")
            except:
                logger.error("清理缓存出错，无本地对话记录")
            try:
                GeminiData.pop(event.sender.id)
                # 写入文件
                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(GeminiData, file, allow_unicode=True)
                await bot.send(event,"已清除近期记忆")
            except:
                logger.error("清理缓存出错，无本地对话记录")
            try:
                coziData.pop(event.sender.id)
            except:
                logger.error("清理缓存出错，无本地对话记录")
    @bot.on(FriendMessage)
    async def setChatGLMKey(event: FriendMessage):
        global chatGLMsingelUserKey
        if str(event.message_chain).startswith("设置密钥#"):
            key12 = str(event.message_chain).split("#")[1] + ""
            try:
                prompt = [{"user": "你好"}]
                st1 = chatGLM1(key12, meta, prompt)
                #st1 = st1.replace("yucca", botName).replace("liris", str(event.sender.nickname))
                await bot.send(event, st1, True)
            except:
                await bot.send(event, "chatGLM启动出错，请联系检查apiKey或重试")
                return
            chatGLMsingelUserKey[event.sender.id] = key12
            with open('config/chatGLMSingelUser.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMsingelUserKey, file, allow_unicode=True)
            await bot.send(event, "设置apiKey成功")

    @bot.on(FriendMessage)
    async def setChatGLMKey(event: FriendMessage):
        global chatGLMsingelUserKey
        if str(event.message_chain).startswith("取消密钥") and event.sender.id in chatGLMsingelUserKey:
            chatGLMsingelUserKey.pop(event.sender.id)
            with open('config/chatGLMSingelUser.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMsingelUserKey, file, allow_unicode=True)
            await bot.send(event, "设置apiKey成功")
    #私聊设置bot角色
    # print(trustUser)
    @bot.on(FriendMessage)
    async def showCharacter(event:FriendMessage):
        if str(event.message_chain)=="可用角色模板" or "角色模板" in str(event.message_chain):
            st1=""
            for isa in allcharacters:
                st1+=isa+"\n"
            await bot.send(event,"对话可用角色模板：\n"+st1+"\n发送：设定#角色名 以设定角色")
    @bot.on(FriendMessage)
    async def setCharacter(event:FriendMessage):
        global chatGLMCharacters
        if str(event.message_chain).startswith("设定#"):
            if str(event.message_chain).split("#")[1] in allcharacters:
                meta12=str(event.message_chain).split("#")[1]

                if meta12=="Gemini" or meta12=="Cozi" or meta12=="lolimigpt" or meta12=="gpt3.5" or meta12=="glm-4":
                    pass
                else:
                    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                        resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                    meta12 = resy.get("chatGLM").get("bot_info").get(str(meta12))
                    try:
                        setName = userdict.get(str(event.sender.id)).get("userName")
                    except:
                        setName = event.sender.nickname
                    if setName == None:
                        setName = event.sender.nickname
                    meta12["user_info"] = meta12.get("user_info").replace(meta12.get("user_name"), setName).replace(meta12.get("bot_name"), botName)
                    meta12["bot_info"] = meta12.get("bot_info").replace(meta12.get("user_name"), setName).replace(meta12.get("bot_name"), botName)
                    meta12["bot_name"] = botName
                    meta12["user_name"] = setName
                chatGLMCharacters[event.sender.id] = meta12

                logger.info("当前："+str(chatGLMCharacters))
                with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMCharacters, file, allow_unicode=True)
                await bot.send(event,"设定成功")
            else:
                await bot.send(event,"不存在的角色")



    # print(trustUser)
    @bot.on(GroupMessage)
    async def showCharacter(event:GroupMessage):
        if str(event.message_chain)=="可用角色模板" or (At(bot.qq) in event.message_chain and "角色模板" in str(event.message_chain)):
            st1=""
            for isa in allcharacters:
                st1+=isa+"\n"
            await bot.send(event,"对话可用角色模板：\n"+st1+"\n发送：设定#角色名 以设定角色")
    @bot.on(GroupMessage)
    async def setCharacter(event:GroupMessage):
        global chatGLMCharacters,userdict
        if str(event.message_chain).startswith("设定#"):
            if str(event.message_chain).split("#")[1] in allcharacters:
                meta12=str(event.message_chain).split("#")[1]
                #print(meta1)
                if meta12=="Gemini" or meta12=="Cozi" or meta12=="lolimigpt" or meta12=="gpt3.5" or meta12=="glm-4":
                    pass
                else:
                    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                        resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                    meta12 = resy.get("chatGLM").get("bot_info").get(str(meta12))
                    try:
                        setName = userdict.get(str(event.sender.id)).get("userName")
                    except:
                        setName = event.sender.member_name
                    if setName == None:
                        setName = event.sender.member_name
                    meta12["user_info"] = meta12.get("user_info").replace(meta12.get("user_name"), setName).replace(meta12.get("bot_name"), botName)
                    meta12["bot_info"] = meta12.get("bot_info").replace(meta12.get("user_name"), setName).replace(meta12.get("bot_name"), botName)
                    meta12["bot_name"] = botName
                    meta12["user_name"] = setName
                chatGLMCharacters[event.sender.id] = meta12
                logger.info("当前："+str(meta12))
                with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMCharacters, file, allow_unicode=True)
                await bot.send(event,"设定成功")
            else:
                await bot.send(event,"不存在的角色")

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

    @bot.on(GroupMessage)
    async def upddd(event: GroupMessage):
        if str(event.message_chain).startswith("授权") and event.sender.id==master:
            logger.info("更新数据")
            await sleep(15)
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                resul = yaml.load(f.read(), Loader=yaml.FullLoader)
            global trustG
            trustG=  resul.get("trustGroups")
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
        global trustUser, chatGLMapikeys,chatGLMData,chatGLMCharacters,chatGLMsingelUserKey,userdict,GeminiData,coziData,trustG
        pattern1 = r'(\d+)张(\w+)'
        if At(bot.qq) in event.message_chain:
            text1 = str(event.message_chain).replace("壁纸", "").replace("涩图", "").replace("色图", "").replace("图",
                                                                                                           "").replace(
                "r18", "")
            match1 = re.search(pattern1, text1)
            if match1:
                if len(match1.group(2))>5:
                    pass
                else:
                    return
        if (At(bot.qq) in event.message_chain) and (glmReply == True or (trustglmReply == True and str(event.sender.id) in trustUser) or event.group.id in trustG):
            logger.info("ai聊天启动")
        else:

            return
        if event.sender.id in chatGLMCharacters:
            if chatGLMCharacters.get(event.sender.id) == "Gemini":
                text = str(event.message_chain).replace("@" + str(bot.qq) + "", '').replace(" ", "").replace("/g", "")
                for saa in noRes:
                    if text == saa:
                        logger.warning("与屏蔽词匹配，Gemini不回复")
                        return
                logger.info("gemini开始运行")
                if text == "" or text == " ":
                    text = "在吗"
                geminichar=allcharacters.get("Gemini").replace("【bot】",botName).replace("【用户】", event.sender.member_name)
            # 构建新的prompt
                tep = {"role": "user", "parts": [text]}
            # print(type(tep))
            # 获取以往的prompt
                if event.sender.id in GeminiData and context == True:
                    prompt = GeminiData.get(event.sender.id)
                    prompt.append({"role": "user", 'parts': [text]})
                # 没有该用户，以本次对话作为prompt
                else:
                    await bot.send(event, "即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)", True)
                    prompt=[{"role": "user", "parts": [geminichar]},{"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]}]
                    prompt.append(tep)
                logger.info("gemini接收提问:" + text)
                try:
                    # logger.info(geminiapikey)
                    r = asyncio.run_coroutine_threadsafe(geminirep(ak=random.choice(geminiapikey), messages=prompt),
                                                         newLoop)
                    r = r.result()
                    # 更新该用户prompt
                    prompt.append({"role": 'model', "parts": [r]})
                    await tstt(r, event)
                    logger.info("gemini回复：" + r)
                    if len(prompt) > maxPrompt:
                        logger.error("gemini prompt超限，移除元素")
                        del prompt[2]
                        del prompt[2]
                    GeminiData[event.sender.id] = prompt
                    # 写入文件
                    with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(GeminiData, file, allow_unicode=True)

                    # asyncio.run_coroutine_threadsafe(asyncgemini(geminiapikey,prompt, event,text), newLoop)
                    # st1 = await chatGLM(selfApiKey, meta1, prompt)
                except Exception as e:
                    logger.error(e)
                    GeminiData.pop(event.sender.id)
                    await bot.send(event, "gemini启动出错,请重试\n或发送 @bot 可用角色模板 以更换其他模型")
            elif type(chatGLMCharacters.get(event.sender.id)) == dict:
                text = str(event.message_chain).replace("@" + str(bot.qq) + "", '').replace(" ", "")
                logger.info("分支1")
                for saa in noRes:
                    if text == saa:
                        logger.warning("与屏蔽词匹配，chatGLM不回复")
                        return
                if text == "" or text == " ":
                    text = "在吗"
                # 构建新的prompt
                tep = {"role": "user", "content": text}
                # print(type(tep))
                # 获取以往的prompt
                if event.sender.id in chatGLMData and context == True:
                    prompt = chatGLMData.get(event.sender.id)
                    prompt.append({"role": "user", "content": text})

                # 没有该用户，以本次对话作为prompt
                else:
                    await bot.send(event, "即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)", True)
                    prompt = [tep]
                    chatGLMData[event.sender.id] = prompt
                # logger.info("当前prompt"+str(prompt))

                if event.sender.id in chatGLMsingelUserKey:
                    selfApiKey = chatGLMsingelUserKey.get(event.sender.id)
                    # 构建prompt
                # 或者开启了信任用户回复且为信任用户
                elif str(event.sender.id) in trustUser and trustglmReply == True:
                    logger.info("信任用户进行chatGLM提问")
                    selfApiKey = chatGLM_api_key
                elif glmReply==True:
                    logger.info("开放群聊glm提问")
                    selfApiKey = chatGLM_api_key
                else:
                    await bot.send(event,"Error,该模型不可用")
                    return

                # 获取角色设定
                if event.sender.id in chatGLMCharacters:
                    meta1 = chatGLMCharacters.get(event.sender.id)
                else:
                    logger.warning("读取meta模板")
                    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                        resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                    meta1 = resy.get("chatGLM").get("bot_info").get("default")
                try:
                    setName = userdict.get(str(event.sender.id)).get("userName")
                except:
                    setName = event.sender.member_name
                if setName == None:
                    setName = event.sender.member_name
                meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
                meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca", botName)
                meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca", botName)
                meta1["bot_name"] = botName

                logger.info("chatGLM接收提问:" + text)
                try:
                    logger.info("当前meta:" + str(meta1))
                    asyncio.run_coroutine_threadsafe(asyncchatGLM(selfApiKey, meta1, prompt, event, setName, text), newLoop)
                    # st1 = await chatGLM(selfApiKey, meta1, prompt)


                except:
                    await bot.send(event, "chatGLM启动出错，请联系master\n或发送 @bot 可用角色模板 以更换其他模型")
            else:
                await modelReply(event, chatGLMCharacters.get(event.sender.id))
        #判断模型
        elif replyModel=="Gemini":
            text = str(event.message_chain).replace("@" + str(bot.qq) + "", '').replace(" ", "").replace("/g", "")
            for saa in noRes:
                if text == saa:
                    logger.warning("与屏蔽词匹配，Gemini不回复")
                    return
            logger.info("gemini开始运行")
            if text == "" or text == " ":
                text = "在吗"
            geminichar=allcharacters.get("Gemini").replace("【bot】",botName).replace("【用户】", event.sender.member_name)
            # 构建新的prompt
            tep = {"role": "user", "parts": [text]}
            # print(type(tep))
            # 获取以往的prompt
            if event.sender.id in GeminiData and context == True:
                prompt = GeminiData.get(event.sender.id)
                prompt.append({"role": "user", 'parts': [text]})
                # 没有该用户，以本次对话作为prompt
            else:
                await bot.send(event, "即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)", True)
                prompt=[{"role": "user", "parts": [geminichar]},{"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]}]
                prompt.append(tep)
            logger.info("gemini接收提问:" + text)
            try:
                # logger.info(geminiapikey)
                r=asyncio.run_coroutine_threadsafe(geminirep(ak=random.choice(geminiapikey), messages=prompt),
                                                 newLoop)
                r = r.result()
                # 更新该用户prompt
                prompt.append({"role": 'model', "parts": [r]})
                await tstt(r,event)
                logger.info("gemini回复："+r)
                if len(prompt) > maxPrompt:
                    logger.error("gemini prompt超限，移除元素")
                    del prompt[2]
                    del prompt[2]
                GeminiData[event.sender.id] = prompt
                # 写入文件
                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(GeminiData, file, allow_unicode=True)


                # asyncio.run_coroutine_threadsafe(asyncgemini(geminiapikey,prompt, event,text), newLoop)
                # st1 = await chatGLM(selfApiKey, meta1, prompt)
            except Exception as e:
                logger.error(e)
                GeminiData.pop(event.sender.id)
                await bot.send(event, "gemini启动出错,请重试\n或发送 @bot 可用角色模板 以更换其他模型")
        elif replyModel=="characterglm":
            text = str(event.message_chain).replace("@" + str(bot.qq) + "", '').replace(" ","")
            logger.info("分支1")
            for saa in noRes:
                if text==saa:
                    logger.warning("与屏蔽词匹配，chatGLM不回复")
                    return
            if text=="" or text==" ":
                text="在吗"
            #构建新的prompt
            tep={"role": "user","content": text}
            #print(type(tep))
            #获取以往的prompt
            if event.sender.id in chatGLMData and context==True:
                prompt=chatGLMData.get(event.sender.id)
                prompt.append({"role": "user","content": text})

            #没有该用户，以本次对话作为prompt
            else:
                await bot.send(event, "即将开始对话，请注意，如果遇到对话异常，请发送 /clear 以清理对话记录(不用艾特)",True)
                prompt=[tep]
                chatGLMData[event.sender.id] =prompt
            #logger.info("当前prompt"+str(prompt))

            if event.sender.id in chatGLMsingelUserKey:
                selfApiKey = chatGLMsingelUserKey.get(event.sender.id)
                # 构建prompt
            # 或者开启了信任用户回复且为信任用户
            elif str(event.sender.id) in trustUser and trustglmReply == True:
                logger.info("信任用户进行chatGLM提问")
                selfApiKey = chatGLM_api_key
            elif glmReply==True:
                logger.info("开放群聊glm提问")
                selfApiKey = chatGLM_api_key
            else:
                await bot.send(event,"Error,该模型不可用")
                return

            #获取角色设定
            if event.sender.id in chatGLMCharacters:
                meta1=chatGLMCharacters.get(event.sender.id)
            else:
                logger.warning("读取meta模板")
                with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                    resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                meta1 = resy.get("chatGLM").get("bot_info").get("default")
            try:
                setName = userdict.get(str(event.sender.id)).get("userName")
            except:
                setName = event.sender.member_name
            if setName == None:
                setName = event.sender.member_name
            meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
            meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
            meta1["bot_info"]=meta1.get("bot_info").replace("指挥",setName).replace("yucca",botName)
            meta1["bot_name"]=botName

            logger.info("chatGLM接收提问:" + text)
            try:
                logger.info("当前meta:"+str(meta1))
                asyncio.run_coroutine_threadsafe(asyncchatGLM(selfApiKey, meta1, prompt, event, setName, text), newLoop)
                #st1 = await chatGLM(selfApiKey, meta1, prompt)


            except:
                await bot.send(event, "chatGLM启动出错，请联系master\n或发送 @bot 可用角色模板 以更换其他模型")
        elif ((str(event.group.id) == str(mainGroup) and chatGLM_api_key!="sdfafjsadlf;aldf") or (event.group.id in chatGLMapikeys)) and At(
                bot.qq) in event.message_chain:
            text = str(event.message_chain).replace("@" + str(bot.qq) + "", '').replace(" ","")
            logger.info("分支2")
            for saa in noRes:
                if text==saa:
                    logger.warning("与屏蔽词匹配，chatGLM不回复")
                    return
            if text=="" or text==" ":
                text="在吗"
            # 构建新的prompt
            tep = {"role": "user", "content": text}

            # 获取以往的prompt
            if event.sender.id in chatGLMData and context==True:
                prompt = chatGLMData.get(event.sender.id)
                prompt.append({"role": "user","content": text})
            # 没有该用户，以本次对话作为prompt
            else:
                prompt = [tep]
                chatGLMData[event.sender.id] = prompt
            #logger.info("当前prompt" + str(prompt))
            #获取专属meta
            if event.sender.id in chatGLMCharacters:
                meta1=chatGLMCharacters.get(event.sender.id)
            else:
                logger.warning("读取meta模板")
                with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                    resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                meta1 = resy.get("chatGLM").get("bot_info").get("default")
            try:
                setName = userdict.get(str(event.sender.id)).get("userName")
            except:
                setName = event.sender.member_name
            if setName==None:
                setName = event.sender.member_name
            meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
            meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
            meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca",botName)
            meta1["bot_name"] = botName

            logger.info("chatGLM接收提问:" + text)
            #获取apiKey
            logger.info("当前meta:"+str(meta1))
            if str(event.group.id) == str(mainGroup):
                key1 = chatGLM_api_key
            else:
                key1 = chatGLMapikeys.get(event.group.id)
            try:
                #分界线
                asyncio.run_coroutine_threadsafe(asyncchatGLM(key1, meta1, prompt,event,setName,text), newLoop)
            except:
                await bot.send(event, "chatGLM启动出错，请联系master\n或发送 @bot 可用角色模板 以更换其他模型")
        else:
            await modelReply(event, replyModel)
    async def tstt(r,event):
        if len(r) < maxTextLen and random.randint(0, 100) < voiceRate and event.type != 'FriendMessage':
            data1 = {}
            data1['speaker'] = speaker

            # print(path)
            st8 = re.sub(r"（[^）]*）", "", r)  # 使用r前缀表示原始字符串，避免转义字符的问题
            data1["text"] = st8
            st1 = r
            try:
                if voicegg == "vits":
                    logger.info("调用vits语音回复")
                    try:
                        path = 'data/voices/' + random_str() + '.wav'
                        if random.randint(1, 100) > chineseVoiceRate:
                            text = await translate(str(st8))
                            tex = '[JA]' + text + '[JA]'
                        else:
                            tex = "[ZH]" + st8 + "[ZH]"
                        logger.info("启动文本转语音：text: " + tex + " path: " + path)
                        # spe = rte.get("defaultModel").get("speaker")
                        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                            resulte = yaml.load(f.read(), Loader=yaml.FullLoader)
                        spe = resulte.get("defaultModel").get("speaker")
                        modelSelect = resulte.get("defaultModel").get("modelSelect")
                        await voiceGenerate({"text": tex, "out": path, "speaker": spe, "modelSelect": modelSelect})
                        await bot.send(event, Voice(path=path))
                    except:
                        logger.error("vits服务运行出错，请检查是否开启或检查配置")
                        await bot.send(event, st1, True)
                else:
                    logger.info(f"调用{voicegg}语音合成")
                    path = await superVG(data1, voicegg, berturl,voiceLangType)
                    await bot.send(event, Voice(path=path))
                if withText == True:
                    await bot.send(event, st1, True)
            except Exception as e:
                logger.error(e)
                if random.randint(0, 100) < RateIfUnavailable:
                    logger.info("出错，改用vits")
                    try:
                        path = 'data/voices/' + random_str() + '.wav'
                        if random.randint(1, 100) > chineseVoiceRate:
                            text = await translate(str(st8))
                            tex = '[JA]' + text + '[JA]'
                        else:
                            tex = "[ZH]" + st8 + "[ZH]"
                        logger.info("启动文本转语音：text: " + tex + " path: " + path)
                        # spe = rte.get("defaultModel").get("speaker")
                        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                            resulte = yaml.load(f.read(), Loader=yaml.FullLoader)
                        spe = resulte.get("defaultModel").get("speaker")
                        modelSelect = resulte.get("defaultModel").get("modelSelect")
                        await voiceGenerate(
                            {"text": tex, "out": path, "speaker": spe, "modelSelect": modelSelect})
                        await bot.send(event, Voice(path=path))
                        if withText == True:
                            await bot.send(event, st1, True)
                    except Exception as e:
                        logger.error(e)
                        logger.error("vits服务运行出错，请检查是否开启或检查配置")
                        await bot.send(event, st1, True)
                        return
                else:
                    await bot.send(event, st1, True)

        else:
            await bot.send(event, r, True)
    #用于chatGLM清除本地缓存
    @bot.on(GroupMessage)
    async def clearPrompt(event:GroupMessage):
        global chatGLMData,GeminiData,coziData
        if str(event.message_chain)=="/clearGLM" or str(event.message_chain)=="/cGemini" or str(event.message_chain)=="/clear":
            try:
                chatGLMData.pop(event.sender.id)
                # 写入文件
                with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMData, file, allow_unicode=True)
                await bot.send(event,"已清除近期记忆")
            except:
                logger.error("清理缓存出错，无本地对话记录")
            try:
                GeminiData.pop(event.sender.id)
                # 写入文件
                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(GeminiData, file, allow_unicode=True)
                await bot.send(event,"已清除近期记忆")
            except:
                logger.error("清理缓存出错，无本地对话记录")
            try:
                coziData.pop(event.sender.id)
            except:
                logger.error("清理缓存出错，无本地对话记录")
        elif str(event.message_chain)=="/allclear" and event.sender.id==master:
            try:
                chatGLMData={"f":"hhh"}
                #chatGLMData.pop(event.sender.id)
                # 写入文件
                with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMData, file, allow_unicode=True)

                with open('data/GeminiData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMData, file, allow_unicode=True)
                await bot.send(event,"已清除所有用户的prompt")
            except:
                await bot.send(event,"清理缓存出错，无本地对话记录")

    @bot.on(GroupMessage)
    async def setChatGLMKey(event:GroupMessage):
        global chatGLMapikeys
        if str(event.message_chain).startswith("设置密钥#"):
            key12=str(event.message_chain).split("#")[1]+""
            try:
                prompt=[{"user":"你好"}]
                st1 = chatGLM1(key12, meta,prompt)
                #asyncio.run_coroutine_threadsafe(asyncchatGLM(key1, meta1, prompt, event, setName, text), newLoop)
                st1 = st1.replace("yucca", botName).replace("liris", str(event.sender.member_name))
                await bot.send(event, st1, True)
            except:
                await bot.send(event, "chatGLM启动出错，\n或发送 @bot 可用角色模板 以更换其他模型")
                return
            chatGLMapikeys[event.group.id]=key12
            with open('config/chatGLM.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMapikeys, file, allow_unicode=True)
            await bot.send(event, "设置apiKey成功")

    @bot.on(GroupMessage)
    async def setChatGLMKey(event: GroupMessage):
        global chatGLMapikeys
        if str(event.message_chain).startswith("取消密钥") and event.group.id in chatGLMapikeys:
            chatGLMapikeys.pop(event.group.id)
            with open('config/chatGLM.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMapikeys, file, allow_unicode=True)
            await bot.send(event, "设置apiKey成功")


    @bot.on(GroupMessage)
    async def gpt3(event: GroupMessage):
        if str(event.message_chain).startswith("/chat"):
            s = str(event.message_chain).replace("/chat", "")
            try:
                logger.info("gpt3.5接收信息：" + s)
                url = "https://api.lolimi.cn/API/AI/mfcat3.5.php?sx=你是一个可爱萝莉&msg="+s+"&type=json"
                async with httpx.AsyncClient(timeout=40) as client:
                    # 用get方法发送请求
                    response = await client.get(url=url)
                s=response.json().get("data")
                s = s.replace(r"\n", "\n")

                logger.info("gpt3.5:" + s)
                await bot.send(event, s, True)
            except:
                logger.error("调用gpt3.5失败，请检查网络或重试")
                await bot.send(event, "无法连接到gpt3.5，请检查网络或重试")
    #科大讯飞星火ai
    @bot.on(GroupMessage)
    async def gpt3(event: GroupMessage):
        if str(event.message_chain).startswith("/xh"):
            s = str(event.message_chain).replace("/xh", "")
            try:
                logger.info("讯飞星火接收信息：" + s)
                url = "https://api.lolimi.cn/API/AI/xh.php?msg=" + s
                async with httpx.AsyncClient(timeout=40) as client:
                    # 用get方法发送请求
                    response = await client.get(url=url)
                s = response.json().get("data").get("output")
                s = s.replace(r"\n", "\n")
                logger.info("讯飞星火:" + s)
                await bot.send(event, s, True)
            except:
                logger.error("调用讯飞星火失败，请检查网络或重试")
                await bot.send(event, "无法连接到讯飞星火，请检查网络或重试")

    # 文心一言
    @bot.on(GroupMessage)
    async def gpt3(event: GroupMessage):
        if str(event.message_chain).startswith("/wx"):
            s = str(event.message_chain).replace("/wx", "")
            try:
                logger.info("文心一言接收信息：" + s)
                url = "https://api.lolimi.cn/API/AI/wx.php?msg=" + s
                async with httpx.AsyncClient(timeout=40) as client:
                    # 用get方法发送请求
                    response = await client.get(url=url)
                s = response.json().get("data").get("output")
                s=s.replace(r"\n","\n")

                logger.info("文心一言:" + s)
                await bot.send(event, s, True)
            except:
                logger.error("调用文心一言失败，请检查网络或重试")
                await bot.send(event, "无法连接到文心一言，请检查网络或重试")

    @bot.on(GroupMessage)
    async def rwkv(event: GroupMessage):
        if str(event.message_chain).startswith("/rwkv"):
            s = str(event.message_chain).replace("/rwkv", "")
            try:
                logger.info("rwkv接收信息：" + s)
                s = await rwkvHelper(s)
                logger.info("rwkv:" + s)
                await bot.send(event, s, True)
            except:
                logger.error("调用rwkv失败，请检查本地rwkv是否启动或端口是否配置正确(8000)")
                await bot.send(event, "无法连接到本地rwkv")


    #CharacterchatGLM部分
    def chatGLM(api_key,bot_info,prompt,model1):
        model1="characterglm"
        logger.info("当前模式:"+model1)
        zhipuai.api_key = api_key
        if model1=="chatglm_pro":
            response = zhipuai.model_api.sse_invoke(
                model="chatglm_pro",
                prompt=prompt,
                temperature=0.95,
                top_p=0.7,
                incremental=True
            )
        elif model1=="chatglm_std":
            response = zhipuai.model_api.sse_invoke(
                model="chatglm_std",
                prompt=prompt,
                temperature=0.95,
                top_p=0.7,
                incremental=True
            )
        elif model1=="chatglm_lite":
            response = zhipuai.model_api.sse_invoke(
                model="chatglm_lite",
                prompt=prompt,
                temperature=0.95,
                top_p=0.7,
            )
        else:
            response = zhipuai.model_api.sse_invoke(
                model="characterglm",
                meta= bot_info,
                prompt= prompt,
                incremental=True
            )
        str1=""
        for event in response.events():
          if event.event == "add":
              str1+=event.data
              #print(event.data)
          elif event.event == "error" or event.event == "interrupted":
              str1 += event.data
              #print(event.data)
          elif event.event == "finish":
              str1 += event.data
              #print(event.data)
              print(event.meta)
          else:
              str1 += event.data
              #print(event.data)
        #print(str1)
        return str1
    # 创建一个异步函数
    async def asyncchatGLM(apiKey,bot_info,prompt,event,setName,text):
        global chatGLMData

        loop = asyncio.get_event_loop()
        # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
        # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
        # 第二个参数是同步函数名，后面跟着任何你需要传递的参数
        #result=chatGLM(apiKey,bot_info,prompt)
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
        model1 = result.get("chatGLM").get("model")
        st1 = await loop.run_in_executor(None, chatGLM,apiKey,bot_info,prompt,model1)
        # 打印结果
        #print(result)
        st11 = st1.replace(setName, "指挥")
        logger.info("chatGLM:" + st1)
        if len(st1)<maxTextLen and random.randint(0,100)<voiceRate and event.type!='FriendMessage':
            data1={}
            data1['speaker']=speaker

            #print(path)
            st8 = re.sub(r"（[^）]*）", "", st1)  # 使用r前缀表示原始字符串，避免转义字符的问题
            data1["text"] = st8

            try:
                if voicegg == "vits":
                    logger.info("调用vits语音回复")
                    try:
                        path = 'data/voices/' + random_str() + '.wav'
                        if random.randint(1, 100) > chineseVoiceRate:
                            text = await translate(str(st8))
                            tex = '[JA]' + text + '[JA]'
                        else:
                            tex = "[ZH]" + st8 + "[ZH]"
                        logger.info("启动文本转语音：text: " + tex + " path: " + path)
                        # spe = rte.get("defaultModel").get("speaker")
                        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                            resulte = yaml.load(f.read(), Loader=yaml.FullLoader)
                        spe = resulte.get("defaultModel").get("speaker")
                        modelSelect = resulte.get("defaultModel").get("modelSelect")
                        await voiceGenerate({"text": tex, "out": path, "speaker": spe, "modelSelect": modelSelect})
                        await bot.send(event, Voice(path=path))

                    except:
                        logger.error("vits服务运行出错，请检查是否开启或检查配置")
                        await bot.send(event, st1, True)
                else:
                    logger.info(f"调用{voicegg}语音合成")
                    path=await superVG(data1,voicegg,berturl,voiceLangType)
                    await bot.send(event,Voice(path=path))
                if withText == True:
                    await bot.send(event, st1, True)
            except Exception as e:
                logger.error(e)
                if random.randint(0, 100) < RateIfUnavailable:
                    logger.info("出错，改用vits")
                    try:
                        path = 'data/voices/' + random_str() + '.wav'
                        if random.randint(1, 100) > chineseVoiceRate:
                            text = await translate(str(st8))
                            tex = '[JA]' + text + '[JA]'
                        else:
                            tex = "[ZH]" + st8 + "[ZH]"
                        logger.info("启动文本转语音：text: " + tex + " path: " + path)
                        # spe = rte.get("defaultModel").get("speaker")
                        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                            resulte = yaml.load(f.read(), Loader=yaml.FullLoader)
                        spe = resulte.get("defaultModel").get("speaker")
                        modelSelect = resulte.get("defaultModel").get("modelSelect")
                        await voiceGenerate(
                            {"text": tex, "out": path, "speaker": spe, "modelSelect": modelSelect})
                        await bot.send(event, Voice(path=path))
                        if withText == True:
                            await bot.send(event, st1, True)
                    except Exception as e:
                        logger.error(e)
                        logger.error("vits服务运行出错，请检查是否开启或检查配置")
                        await bot.send(event, st1, True)
                else:
                    await bot.send(event, st1, True)



        else:
            if len(st1) > 400:
                await bot.send(event, st1[:100],True)
                await bot.send(event, "🐱‍💻回复可能存在异常，\n请发送 /clear 以清理当前聊天(无需艾特)", True)
                try:
                    prompt.remove(prompt[-1])
                    chatGLMData[event.sender.id] = prompt
                except:
                    logger.error("chatGLM删除上一次对话失败")
                return
            await bot.send(event, st1, True)



        if turnMessage==True and event.type=='FriendMessage' and event.sender.id!=master:
            await bot.send_friend_message(int(master),"chatGLM接收消息：\n来源:"+str(event.sender.id)+"\n提问:"+text+"\n回复:"+st1)
        try:
            addStr = '添加' + text + '#' + st11
            mohuaddReplys(addStr, str("chatGLMReply"))
        except:
            logger.error("写入本地词库失败")
        if context == True:
            # 更新该用户prompt
            prompt.append({"role": "assistant", "content": st1})
            # 超过10，移除第一个元素

            if len(prompt) > maxPrompt:
                logger.error("glm prompt超限，移除元素")
                del prompt[0]
                del prompt[0]
            chatGLMData[event.sender.id] = prompt
            # 写入文件
            with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMData, file, allow_unicode=True)


    # 运行异步函数

    async def modelReply(event,modelHere):
        global trustUser, chatGLMapikeys, chatGLMData, chatGLMCharacters, chatGLMsingelUserKey, userdict, GeminiData, coziData
        if event.type != 'FriendMessage':
            bot_in = str("你是" + botName + ",我是" + event.sender.member_name + "," + allcharacters.get(
            "gpt3.5")).replace("【bot】",
                               botName).replace("【用户】", event.sender.member_name)
            lolimi_bot_in = str("你是" + botName + ",我是" + event.sender.member_name + "," + allcharacters.get(
                "lolimigpt")).replace("【bot】",
                                   botName).replace("【用户】", event.sender.member_name)
            glm4_bot_in = str("你是" + botName + ",我是" + event.sender.member_name + "," + allcharacters.get(
                "glm-4")).replace("【bot】",
                                      botName).replace("【用户】", event.sender.member_name)
        else:
            bot_in = str("你是" + botName + ",我是" + event.sender.nickname + "," + allcharacters.get(
                "gpt3.5")).replace("【bot】",
                                   botName).replace("【用户】", event.sender.nickname)
            lolimi_bot_in = str("你是" + botName + ",我是" + event.sender.nickname + "," + allcharacters.get(
                "lolimigpt")).replace("【bot】",
                                      botName).replace("【用户】", event.sender.nickname)
            glm4_bot_in = str("你是" + botName + ",我是" + event.sender.nickname + "," + allcharacters.get(
                "glm-4")).replace("【bot】",
                                      botName).replace("【用户】", event.sender.nickname)
        try:
            text = str(event.message_chain).replace("@" + str(bot.qq) + " ", '')
            if text == "" or text == " ":
                text = "在吗"
            for saa in noRes:
                #print(text, saa)
                if text == saa:

                    logger.warning("与屏蔽词匹配，不回复")
                    return
            if event.sender.id in chatGLMData:
                prompt1 = chatGLMData.get(event.sender.id)
                prompt1.append({"content": text, "role": "user"})
            else:
                prompt1 = [{"content": text, "role": "user"}]
                await bot.send(event, "即将开始对话，如果遇到异常请发送 /clear 清理对话")
            logger.info(f"{modelHere}  bot 接受提问：" + text)
            loop = asyncio.get_event_loop()
            if modelHere == "gpt3.5-dev":
                rep = await loop.run_in_executor(None, gptUnofficial, prompt1, gptkeys, proxy, bot_in)
            elif modelHere=="gpt3.5":
                rep = await loop.run_in_executor(None, gptOfficial, prompt1, gptkeys, proxy, bot_in)
            elif modelHere=="Cozi":
                rep = await loop.run_in_executor(None, cozeBotRep, CoziUrl, prompt1, proxy)
            elif modelHere=="lolimigpt":
                rep = await lolimigpt2(prompt1,lolimi_bot_in)
                if "令牌额度" in rep.get("content"):
                    logger.error("没金币了喵")
                    await bot.send(event, "api没金币了喵\n请发送 @bot 可用角色模板 以更换其他模型", True)
                    return
                if "敏感词汇" in rep.get("content"):
                    logger.error("敏感词了搁这")
                    await bot.send(event, "触发了敏感词审核，已自动清理聊天记录", True)
                    try:
                        chatGLMData.pop(event.sender.id)
                    except Exception as e:
                        logger.error(e)
                    return

            elif modelHere=="glm-4":
                rep=await glm4(prompt1,glm4_bot_in)
                if "禁止违规问答" == rep.get("content"):
                    logger.error("敏感喽，不能用了")
                    await bot.send(event,rep.get("content"))
                    await bot.send(event,"触发了敏感内容审核，已自动清理聊天记录")
                    try:
                        chatGLMData.pop(event.sender.id)
                    except Exception as e:
                        logger.error(e)
                    return
            prompt1.append(rep)
            # 超过10，移除第一个元素

            if len(prompt1) > maxPrompt:
                logger.error(f"{modelHere} prompt超限，移除元素")
                del prompt1[0]
                del prompt1[0]
            chatGLMData[event.sender.id] = prompt1
            # 写入文件
            with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMData, file, allow_unicode=True)
            logger.info(f"{modelHere} bot 回复：" + rep.get('content'))
            await tstt(rep.get('content').replace("Content is blocked",""), event)
        except Exception as e:
            logger.error(e)
            try:
                chatGLMData.pop(event.sender.id)
                logger.info("清理用户prompt")
            except Exception as e:
                logger.error("清理用户prompt出错")

            await bot.send(event, "出错，自动清理异常prompt.....请重试，如果无效请 联系master反馈问题\n或发送 \n@bot 可用角色模板\n 以更换其他模型", True)

if __name__ == '__main__':



    while True:
        input("任意键以结束")
