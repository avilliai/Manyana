# -*- coding: utf-8 -*-
import json
import random
import uuid
from asyncio import sleep

import httpx
import poe
import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.PandoraChatGPT import ask_chatgpt
from plugins.chatGLMonline import chatGLM
from plugins.rwkvHelper import rwkvHelper
from plugins.wReply.mohuReply import mohuaddReplys


def main(bot, master, apikey, chatGLM_api_key, proxy, logger):
    #读取个性化角色设定
    with open('data/chatGLMCharacters.yaml', 'r', encoding='utf-8') as f:
        result2223 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMCharacters
    chatGLMCharacters = result2223

    with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
        result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMapikeys
    chatGLMapikeys = result222


    with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
        cha = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMData
    chatGLMData=cha
    #logger.info(chatGLMData)

    try:
        logger.info("正在启动poe-AI")
        global apiKey
        apiKey = apikey
        global KEY
        KEY = apiKey[0]
        logger.info("选择key:" + KEY)
        global client
        client = poe.Client(KEY, proxy=proxy)
        json.dumps(client.bot_names, indent=2)
    except:
        logger.error("poeAi启动失败，请检查代理或重试")
    logger.info("正在启动rwkv对话模型")

    logger.info("正在启动pandora_ChatGPT")
    '''try:
        parent_message_id = None
        prompt = "我爱你啊！！！！！！！！！"

        # 向ChatGPT提问，等待其回复
        model = "text-davinci-002-render-sha"  # 选择一个可用的模型Default (GPT-3.5)：text-davinci-002-render-sha
        message_id = str(uuid.uuid4())  # 随机生成一个消息ID
        if parent_message_id is None:
            parent_message_id = "f0bf0ebe-1cd6-4067-9264-8a40af76d00e"
        conversation_id = None
        # conversation_id = None
        parent_message_id,conversation_id,reply = ask_chatgpt(prompt, model, message_id, parent_message_id, conversation_id)
        print(reply)
        print("当前会话的id:", parent_message_id)
    except:
        logger.error("未找到可用的pandora服务")'''
    global pandoraData
    with open('data/pandora_ChatGPT.yaml', 'r', encoding='utf-8') as file:
        pandoraData = yaml.load(file, Loader=yaml.FullLoader)
    global totallink
    totallink = False
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    trustDays=result.get("trustDays")
    gptReply = result.get("gptReply")
    pandoraa = result.get("pandora")
    glmReply = result.get("chatGLM").get("glmReply")
    trustglmReply = result.get("chatGLM").get("trustglmReply")
    meta = result.get("chatGLM").get("bot_info").get("default")
    context= result.get("chatGLM").get("context")
    maxPrompt = result.get("chatGLM").get("maxPrompt")
    allcharacters=result.get("chatGLM").get("bot_info")

    with open('config.json', 'r', encoding='utf-8') as fp:
        data = fp.read()
    config = json.loads(data)
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
        times = int(str(data.get('sts')))
        if times > trustDays:
            trustUser.append(str(i))

    logger.info('chatglm部分已读取信任用户' + str(len(trustUser)) + '个')

    with open('config/chatGLMSingelUser.yaml', 'r', encoding='utf-8') as f:
        result224 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMsingelUserKey
    chatGLMsingelUserKey=result224
    #私聊使用chatGLM,对信任用户或配置了apiKey的用户开启
    @bot.on(FriendMessage)
    async def GLMFriendChat(event:FriendMessage):
        global chatGLMData,chatGLMCharacters,trustUser,chatGLMsingelUserKey
        #如果用户有自己的key
        if event.sender.id in chatGLMsingelUserKey:
            selfApiKey=chatGLMsingelUserKey.get(event.sender.id)
            #构建prompt
        #或者开启了信任用户回复且为信任用户
        elif str(event.sender.id) in trustUser and trustglmReply==True:
            logger.info("信任用户进行chatGLM提问")
            selfApiKey=chatGLM_api_key
        elif str(event.message_chain)=="/clearGLM":
            return
        else:
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
            prompt = [tep]
            chatGLMData[event.sender.id] = prompt
        if event.sender.id in chatGLMCharacters:
            meta1 = chatGLMCharacters.get(event.sender.id)
        else:
            meta1 = meta
        try:
            logger.info("当前meta:" + str(meta1))
            st1 = await chatGLM(selfApiKey, meta1, prompt)
            st1 = st1.replace("yucca", botName).replace("amore", str(event.sender.nickname)).replace("阿莫",
                                                                                                        str(event.sender.nickname)).replace(
                "阿莫尔", str(event.sender.nickname))
            await bot.send(event, st1, True)

            logger.info("chatGLM:" + st1)
            if str(event.sender.id)!=str(master):
                await bot.send_friend_message(int(master),"私聊chatGLM接收提问:\n" + text+"\n"+"chatGLM:\n" + st1)
            try:
                addStr = '添加' + text + '#' + st1
                mohuaddReplys(addStr, str("chatGLMReply"))
            except:
                logger.error("写入本地词库失败")
            # 更新该用户prompt
            prompt.append({"role": "assistant", "content": st1})
            # 超过10，移除第一个元素
            #
            logger.info("当前prompt" + str(prompt))
            if len(prompt) > maxPrompt:
                logger.error("glm prompt超限，移除元素")
                del prompt[0]
                del prompt[0]
            chatGLMData[event.sender.id] = prompt
            # 写入文件
            with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMData, file, allow_unicode=True)

        except:
            await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")

    # 私聊中chatGLM清除本地缓存
    @bot.on(FriendMessage)
    async def clearPrompt(event: FriendMessage):
        global chatGLMData
        if str(event.message_chain) == "/clearGLM":
            try:
                chatGLMData.pop(event.sender.id)
                # 写入文件
                with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMData, file, allow_unicode=True)
            except:
                await bot.send(event, "清理缓存出错，无本地对话记录")

    @bot.on(FriendMessage)
    async def setChatGLMKey(event: FriendMessage):
        global chatGLMsingelUserKey
        if str(event.message_chain).startswith("设置密钥#"):
            key12 = str(event.message_chain).split("#")[1] + ""
            try:
                st1 = await chatGLM(key12, meta, "你好呀")
                st1 = st1.replace("yucca", botName).replace("liris", str(event.sender.nickname))
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
                chatGLMCharacters[event.sender.id]=allcharacters.get(str(event.message_chain).split("#")[1])
                logger.info("当前：",chatGLMCharacters)
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
        global chatGLMCharacters
        if str(event.message_chain).startswith("设定#"):
            if str(event.message_chain).split("#")[1] in allcharacters:
                chatGLMCharacters[event.sender.id]=allcharacters.get(str(event.message_chain).split("#")[1])
                logger.info("当前：",chatGLMCharacters)
                with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMCharacters, file, allow_unicode=True)
                await bot.send(event,"设定成功")
            else:
                await bot.send(event,"不存在的角色")

    @bot.on(Startup)
    async def upDate(event: Startup):
        while True:
            await sleep(360)
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
        global trustUser, chatGLMapikeys,chatGLMData,chatGLMCharacters
        if gptReply == True and At(bot.qq) in event.message_chain:
            prompt = str(event.message_chain).replace("@" + str(bot.qq) + "", '')

            message_id = str(uuid.uuid4())
            model = "text-davinci-002-render-sha"
            logger.info("ask:" + prompt)

            if event.group.id in pandoraData.keys():
                pub = event.group.id
                conversation_id = pandoraData.get(event.group.id).get("conversation_id")
                parent_message_id = pandoraData.get(event.group.id).get("parent_message_id")
            else:
                if len(pandoraData.keys()) < 10:
                    pub = event.group.id
                    conversation_id = None
                    parent_message_id = "f0bf0ebe-1cd6-4067-9264-8a40af76d00e"
                else:
                    try:
                        pub = random.choice(pandoraData.keys())
                        conversation_id = pandoraData.get(pub).get("conversation_id")
                        parent_message_id = pandoraData.get(pub).get("parent_message_id")
                    except:
                        await bot.send(event, "当前服务器负载过大，请稍后再试", True)
                        return
            try:
                parent_message_id, conversation_id, response_message = ask_chatgpt(prompt, model, message_id,
                                                                                   parent_message_id,
                                                                                   conversation_id)
                logger.info("answer:" + response_message)
                logger.info("conversation_id:" + conversation_id)
                await bot.send(event, response_message, True)

                pandoraData[pub] = {"parent_message_id": parent_message_id, "conversation_id": conversation_id}
                with open('data/pandora_ChatGPT.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(pandoraData, file, allow_unicode=True)
            except:
                await bot.send(event, "当前服务器负载过大，请稍后再试", True)
        elif (glmReply == True or (trustglmReply == True and str(event.sender.id) in trustUser)) and At(
                bot.qq) in event.message_chain:
            text = str(event.message_chain).replace("@" + str(bot.qq) + "", '')
            logger.info("分支1")
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
                prompt=[tep]
                chatGLMData[event.sender.id] =prompt
            logger.info("当前prompt"+str(prompt))
            if event.sender.id in chatGLMCharacters:
                meta1=chatGLMCharacters.get(event.sender.id)
            else:
                meta1=meta
            try:
                logger.info("当前meta:"+str(meta1))
                st1 = await chatGLM(chatGLM_api_key, meta1, prompt)
                st1 = st1.replace("yucca", botName).replace("amore", str(event.sender.member_name)).replace("阿莫", str(event.sender.member_name)).replace("阿莫尔", str(event.sender.member_name))
                await bot.send(event, st1, True)
                logger.info("chatGLM接收提问:"+text)
                logger.info("chatGLM:"+st1)
                #将chatGLM写入本地词库
                try:
                    addStr = '添加' + text + '#' + st1
                    mohuaddReplys(addStr, str("chatGLMReply"))
                except:
                    logger.error("写入本地词库失败")
                if context==True:
                    #更新该用户prompt
                    prompt.append({"role": "assistant","content": st1})
                    #超过10，移除第一个元素
                    #
                    logger.info("当前prompt" + str(prompt))
                    if len(prompt)>maxPrompt:
                        logger.error("glm prompt超限，移除元素")
                        del prompt[0]
                        del prompt[0]
                    chatGLMData[event.sender.id]=prompt
                    #写入文件
                    with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(chatGLMData, file, allow_unicode=True)

            except:
                await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")
        elif ((str(event.group.id) == str(mainGroup) and chatGLM_api_key!="sdfafjsadlf;aldf") or (event.group.id in chatGLMapikeys)) and At(
                bot.qq) in event.message_chain:
            text = str(event.message_chain).replace("@" + str(bot.qq) + "", '')
            logger.info("分支2")
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
            logger.info("当前prompt" + str(prompt))
            #获取专属meta
            if event.sender.id in chatGLMCharacters:
                meta1=chatGLMCharacters.get(event.sender.id)
            else:
                meta1 = meta
            #获取apiKey
            logger.info("当前meta:"+str(meta1))
            if str(event.group.id) == str(mainGroup):
                key1 = chatGLM_api_key
            else:
                key1 = chatGLMapikeys.get(event.group.id)
            try:
                st1 = await chatGLM(key1, meta1, prompt)
                st1 = st1.replace("yucca", botName).replace("liris", str(event.sender.member_name))
                await bot.send(event, st1, True)
                logger.info("chatGLM接收提问:" + text)
                logger.info("chatGLM:" + st1)
                try:
                    addStr = '添加' + text + '#' + st1
                    mohuaddReplys(addStr, str("chatGLMReply"))
                except:
                    logger.error("写入本地词库失败")
                if context==True:
                    # 更新该用户prompt
                    prompt.append({"role": "assistant", "content": st1})
                    # 超过10，移除第一个元素

                    if len(prompt) > maxPrompt:
                        logger.error("glm prompt超限，移除元素")
                        del prompt[0]
                        del prompt[0]
                    chatGLMData[event.sender.id]= prompt
                    # 写入文件
                    with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(chatGLMData, file, allow_unicode=True)
            except:
                await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")
    #用于chatGLM清除本地缓存
    @bot.on(GroupMessage)
    async def clearPrompt(event:GroupMessage):
        global chatGLMData
        if str(event.message_chain)=="/clearGLM":
            try:
                chatGLMData.pop(event.sender.id)
                # 写入文件
                with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMData, file, allow_unicode=True)
            except:
                await bot.send(event,"清理缓存出错，无本地对话记录")
    @bot.on(GroupMessage)
    async def setChatGLMKey(event:GroupMessage):
        global chatGLMapikeys
        if str(event.message_chain).startswith("设置密钥#"):
            key12=str(event.message_chain).split("#")[1]+""
            try:
                st1 = await chatGLM(key12, meta, "你好呀")
                st1 = st1.replace("yucca", botName).replace("liris", str(event.sender.member_name))
                await bot.send(event, st1, True)
            except:
                await bot.send(event, "chatGLM启动出错，请联系检查apiKey或重试")
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
    async def pandoraSever(event: GroupMessage):
        global pandoraData
        global totallink
        if str(event.message_chain).startswith("/p") and str(event.message_chain).startswith("/poe") == False and str(
                event.message_chain).startswith("/pic") == False:
            if pandoraa:
                if totallink == False:
                    totallink += True
                    if gptReply == False or str(event.message_chain).startswith("/p"):
                        prompt = str(event.message_chain)[2:]
                    else:

                        prompt = str(event.message_chain).replace("@" + str(bot.qq) + "", '')

                    message_id = str(uuid.uuid4())
                    model = "text-davinci-002-render-sha"
                    logger.info("ask:" + prompt)

                    if event.group.id in pandoraData.keys():
                        pub = event.group.id
                        conversation_id = pandoraData.get(event.group.id).get("conversation_id")
                        parent_message_id = pandoraData.get(event.group.id).get("parent_message_id")
                    else:
                        if len(pandoraData.keys()) < 10:
                            pub = event.group.id
                            conversation_id = None
                            parent_message_id = "f0bf0ebe-1cd6-4067-9264-8a40af76d00e"
                        else:
                            try:
                                pub = random.choice(pandoraData.keys())
                                conversation_id = pandoraData.get(pub).get("conversation_id")
                                parent_message_id = pandoraData.get(pub).get("parent_message_id")
                            except:
                                await bot.send(event, "当前服务器负载过大，请稍后再试", True)
                                totallink = False
                                return
                    try:
                        parent_message_id, conversation_id, response_message = ask_chatgpt(prompt, model, message_id,
                                                                                           parent_message_id,
                                                                                           conversation_id)
                        logger.info("answer:" + response_message)
                        logger.info("conversation_id:" + conversation_id)
                        await bot.send(event, response_message, True)
                        totallink = False

                        pandoraData[pub] = {"parent_message_id": parent_message_id, "conversation_id": conversation_id}
                        with open('data/pandora_ChatGPT.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(pandoraData, file, allow_unicode=True)
                    except:
                        await bot.send(event, "当前服务器负载过大，请稍后再试", True)
                        totallink = False
                else:
                    await bot.send(event, "当前服务器负载过大，请稍后再试", True)
            else:
                await bot.send(event, "系统未启用pandora_chatGPT,可能是没有token了", True)

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

    @bot.on(GroupMessage)
    async def AiHelper(event: GroupMessage):
        global client
        global KEY
        if str(event.message_chain).startswith("/poe"):
            mes = str(event.message_chain).replace("/poe", "")
            s = ""
            logger.info("poe接收消息：" + mes)
            try:
                for chunk in client.send_message("capybara", mes):
                    # print(chunk["text_new"],end="", flush=True)
                    s += chunk["text_new"]
                logger.info("bot:" + s)
                await bot.send(event, s)
            except:
                logger.warning("出错，达到每分钟限制或token已失效。")

                if len(apiKey) == 0:
                    await bot.send(event, "令牌已全部失效，请联系master重新获取")
                    return
                else:
                    logger.error("移出token:" + KEY)
                    try:

                        apiKey.remove(KEY)
                        if len(apiKey) == 0:
                            apiKey.append(KEY)
                    except:
                        logger.error("移出token失败")
                    logger.info("当前token:" + str(apiKey))
                logger.warning("执行poe-api 重载指令")
                await bot.send(event, "出错，达到每分钟限制或token已失效。")
                try:
                    KEY = random.choice(apiKey)
                    client = poe.Client(token=KEY, proxy=proxy)
                    json.dumps(client.bot_names, indent=2)
                    logger.info("poe-api重载完成")
                    await bot.send(event, "poe重启完成")
                except:
                    logger.error("poe-api重载失败，请检查代理或更新token")
        if str(event.message_chain) == "/clear" and str(event.sender.id) == str(master):
            client.send_chat_break("capybara")
            await bot.send(event, "已清除对话上下文。")
        if str(event.message_chain) == "/reload" and str(event.sender.id) == str(master):
            client = poe.Client(token=random.choice(apiKey), proxy=proxy)
            json.dumps(client.bot_names, indent=2)
            await bot.send(event, "已重启")


if __name__ == '__main__':
    pass