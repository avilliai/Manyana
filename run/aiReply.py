# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
import random
import shutil
import threading
from asyncio import sleep

import yaml
from mirai import FriendMessage, GroupMessage, At,Image
from mirai import Voice, Startup
from mirai.models import NudgeEvent

from plugins.aiReplyCore import modelReply, clearAllPrompts,clearsinglePrompt
from plugins.toolkits import random_str
from plugins.vitsGenerate import superVG
from plugins.wReply.wontRep import wontrep


# 1
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
    # 读取个性化角色设定
    with open('data/chatGLMCharacters.yaml', 'r', encoding='utf-8') as f:
        result2223 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMCharacters
    chatGLMCharacters = result2223
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = resulttr.get("proxy")
    if proxy != "":
        os.environ["http_proxy"] = proxy
    with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
        cha = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMData
    chatGLMData = cha
    # logger.info(chatGLMData)
    with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
        noRes1 = yaml.load(f.read(), Loader=yaml.FullLoader)

    global totallink
    totallink = False
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    friendsAndGroups = result.get("加群和好友")
    trustDays = friendsAndGroups.get("trustDays")
    glmReply = result.get("chatGLM").get("glmReply")
    privateGlmReply = result.get("chatGLM").get("privateGlmReply")
    nudgeornot = result.get("chatGLM").get("nudgeReply")
    replyModel = result.get("chatGLM").get("model")
    trustglmReply = result.get("chatGLM").get("trustglmReply")
    allcharacters = result.get("chatGLM").get("bot_info")
    allowUserSetModel = result.get("chatGLM").get("allowUserSetModel")
    maxTextLen = result.get("chatGLM").get("maxLen")
    voiceRate = result.get("chatGLM").get("voiceRate")
    withText = result.get("chatGLM").get("withText")
    speaker = result.get("语音功能设置").get("speaker")
    voicegenerateMode = result.get("语音功能设置").get("voicegenerate")
    voiceLangType = result.get("语音功能设置").get("voiceLangType")
    with open('config.json', 'r', encoding='utf-8') as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)
    config = data
    global mainGroup
    try:
        mainGroup = int(config.get("mainGroup"))
    except:
        logger.error("致命错误！mainGroup只能填写一个群的群号!")
        mainGroup = 0
    try:
        with open('data/userData.yaml', 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
    except Exception as e:
        #logger.error(e)
        logger.error("用户数据文件出错，自动使用最新备用文件替换")
        logger.warning(
            "备份文件在temp/userDataBack文件夹下，如数据不正确，请手动使用更早的备份，重命名并替换data/userData.yaml")
        directory = 'temp/userDataBack'

        # 列出文件夹中的所有文件，并按日期排序
        files = sorted(
            [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))],
            key=lambda x: datetime.datetime.strptime(os.path.splitext(x)[0], '%Y_%m_%d'),
            reverse=True
        )
        # 列表中的第一个文件将是日期最新的文件
        latest_file = files[0] if files else None
        logger.warning(f'The latest file is: {latest_file}')

        shutil.copyfile(f'{directory}/{latest_file}', 'data/userData.yaml')
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

    global coziData
    coziData = {}
    # 线程预备
    newLoop = asyncio.new_event_loop()
    listen = CListen(newLoop)
    listen.setDaemon(True)
    listen.start()
    global chattingUser
    chattingUser={} #无需艾特即可对话的用户列表
    timeout = datetime.timedelta(minutes=5) #5分钟没有对话则超时
    @bot.on(GroupMessage)
    async def AddChatWithoutAt(event: GroupMessage):
        if str(event.message_chain)=="开始对话" or str(event.message_chain)=="开始聊天":
            global chattingUser
            user = str(event.sender.id)
            chattingUser[user] = datetime.datetime.now()
            await bot.send(event, "发送 退出 可退出当前对话",True)
    @bot.on(GroupMessage)
    async def removeChatWithoutAt(event: GroupMessage):
        global chattingUser
        if str(event.message_chain)=="退出" and str(event.sender.id) in chattingUser:
            user = str(event.sender.id)
            chattingUser.pop(user)
            await bot.send(event, "已结束当前对话",True)

    @bot.on(NudgeEvent)
    async def NudgeReply(event: NudgeEvent):
        global trustUser
        #戳一戳使用ai回复的话，和这部分放在一起会更好。
        if event.target == bot.qq and nudgeornot:
            global chatGLMCharacters
            logger.info("接收到来自" + str(event.from_id) + "的戳一戳")

            text = random.choice(["戳你一下", "摸摸头", "戳戳你的头", "摸摸~"])
            if event.from_id in chatGLMCharacters:
                #print(chatGLMCharacters.get(event.target), type(chatGLMCharacters.get(event.target)))
                r = await modelReply("指挥", event.from_id, text,chatGLMCharacters.get(event.from_id))
            # 判断模型类型
            else:
                r= await modelReply("指挥", event.from_id, text)
            if withText:
                await bot.send_group_message(event.subject.id, r)
            if len(r) < maxTextLen and random.randint(0, 100) < voiceRate and "出错，请重试" not in r:
                try:
                    path = 'data/voices/' + random_str() + '.wav'
                    logger.info("语音生成_文本" + r)
                    logger.info("语音生成_模型:" + speaker)
                    data = {"text": r, "out": path, 'speaker': speaker}
                    voiceP = await superVG(data,mode=voicegenerateMode,urls="",langmode=voiceLangType )
                    await bot.send_group_message(event.subject.id, Voice(path=voiceP))
                    return
                except:
                    logger.error("语音合成调用失败")
            if not withText:
                await bot.send_group_message(event.subject.id, r)


    # 私聊使用chatGLM,对信任用户或配置了apiKey的用户开启
    @bot.on(FriendMessage)
    async def GLMFriendChat(event: FriendMessage):
        # 用非常丑陋的复制粘贴临时解决bug，这下成石山代码了
        global chatGLMData, chatGLMCharacters, trustUser, userdict
        text = str(event.message_chain)
        if text == "/clear":
            return
        if event.sender.id == master:
            noresm = ["群列表", "/bl", "退群#", "/quit"]
            for saa in noresm:
                if text == saa or text.startswith(saa):
                    logger.warning("与屏蔽词匹配，不回复")
                    return
        if privateGlmReply or (trustglmReply and str(event.sender.id) in trustUser):
            pass
        else:
            return
        text = str(event.message_chain)
        imgurl = None
        if event.message_chain.count(Image):
            lst_img = event.message_chain.get(Image)
            imgurl = []
            for i in lst_img:
                url = i.url
                imgurl.append(url)
                # print(url)
        if event.sender.id in chatGLMCharacters:
            print(type(chatGLMCharacters.get(event.sender.id)), chatGLMCharacters.get(event.sender.id))
            r, firstRep = await modelReply(event.sender.nickname, event.sender.id, text,
                                           chatGLMCharacters.get(event.sender.id), trustUser, imgurl,checkIfRepFirstTime=True)
        # 判断模型
        else:
            r, firstRep = await modelReply(event.sender.nickname, event.sender.id, text, replyModel, trustUser,imgurl,
                                           checkIfRepFirstTime=True)
        if firstRep:
            await bot.send(event, "如对话异常请发送 /clear 以清理对话", True)
        if withText:
            await bot.send(event, r, True)
        if len(r) < maxTextLen and random.randint(0, 100) < voiceRate and "出错，请重试" not in r:
            try:
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_文本" + r)
                logger.info("语音生成_模型:" + speaker)
                data = {"text": r, "out": path, 'speaker': speaker}
                voiceP = await superVG(data, mode=voicegenerateMode, urls="", langmode=voiceLangType)
                await bot.send(event, Voice(path=voiceP))
                return
            except:
                logger.error("语音合成调用失败")
        if not withText:
            await bot.send(event, r, True)


    # 私聊中chatGLM清除本地缓存
    @bot.on(FriendMessage)
    async def clearPrompt(event: FriendMessage):
        global chatGLMData, coziData
        if str(event.message_chain) == "/clear":
            reff = await clearsinglePrompt(event.sender.id)
            await bot.send(event, reff, True)
        elif str(event.message_chain) == "/allclear" and event.sender.id == master:
            reff = await clearAllPrompts()
            await bot.send(event, reff, True)

    # 私聊设置bot角色
    # print(trustUser)
    @bot.on(FriendMessage)
    async def showCharacter(event: FriendMessage):
        if str(event.message_chain) == "可用角色模板" or "角色模板" in str(event.message_chain):
            st1 = ""
            for isa in allcharacters:
                st1 += isa + "\n"
            await bot.send(event, "对话可用角色模板：\n" + st1 + "\n发送：设定#角色名 以设定角色")

    @bot.on(FriendMessage)
    async def setCharacter(event: FriendMessage):
        global chatGLMCharacters
        if str(event.message_chain).startswith("设定#"):
            if str(event.message_chain).split("#")[1] in allcharacters and allowUserSetModel:
                meta12 = str(event.message_chain).split("#")[1]

                chatGLMCharacters[event.sender.id] = meta12
                logger.info("当前：" + str(chatGLMCharacters))
                with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMCharacters, file, allow_unicode=True)
                await bot.send(event, "设定成功")
            else:
                if allowUserSetModel:
                    await bot.send(event, "不存在的角色")
                else:
                    await bot.send(event, "禁止用户自行设定模型(可联系master修改配置)")

    # print(trustUser)
    @bot.on(GroupMessage)
    async def showCharacter(event: GroupMessage):
        if str(event.message_chain) == "可用角色模板" or (
                At(bot.qq) in event.message_chain and "角色模板" in str(event.message_chain)):
            st1 = ""
            for isa in allcharacters:
                st1 += isa + "\n"
            await bot.send(event, "对话可用角色模板：\n" + st1 + "\n发送：设定#角色名 以设定角色")

    @bot.on(GroupMessage)
    async def setCharacter(event: GroupMessage):
        global chatGLMCharacters, userdict
        if str(event.message_chain).startswith("设定#"):
            if str(event.message_chain).split("#")[1] in allcharacters and allowUserSetModel:
                meta12 = str(event.message_chain).split("#")[1]

                chatGLMCharacters[event.sender.id] = meta12
                logger.info("当前：" + str(chatGLMCharacters))
                with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMCharacters, file, allow_unicode=True)
                await bot.send(event, "设定成功")
            else:
                if allowUserSetModel:
                    await bot.send(event, "不存在的角色")
                else:
                    await bot.send(event, "禁止用户自行设定模型(可联系master修改配置)")

    @bot.on(Startup)
    async def upDate(event: Startup):
        while True:
            await sleep(60)
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
            #定时清理用户
            global chattingUser
            now = datetime.datetime.now()
            to_remove = [user for user, timestamp in chattingUser.items() if now - timestamp > timeout]
            for user in to_remove:
                del chattingUser[user]
                logger.info(f"Removed user {user} due to inactivity")
    @bot.on(GroupMessage)
    async def upddd(event: GroupMessage):
        if str(event.message_chain).startswith("授权") and event.sender.id == master:
            await sleep(15)
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                resul = yaml.load(f.read(), Loader=yaml.FullLoader)
            global trustG
            trustG = resul.get("trustGroups")
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

    # 群内chatGLM回复
    @bot.on(GroupMessage)
    async def atReply(event: GroupMessage):
        global trustUser, chatGLMData, chatGLMCharacters, userdict, coziData, trustG,chattingUser
        if At(bot.qq) in event.message_chain or str(event.sender.id) in chattingUser:
            try:
                if not wontrep(noRes1, str(event.message_chain).replace(str(At(bot.qq)), "").replace(" ", ""),
                               logger):
                    return
            except Exception as e:
                logger.error(f"无法运行屏蔽词审核，请检查noResponse.yaml配置格式--{e}")
        if (At(bot.qq) in event.message_chain or str(event.sender.id) in chattingUser) and (glmReply or (trustglmReply and str(
                event.sender.id) in trustUser) or event.group.id in trustG or event.group.id == int(mainGroup)):
            logger.info("ai聊天启动")
        else:
            return
        text = str(event.message_chain).replace("@" + str(bot.qq) + "", '')
        imgurl = None
        if event.message_chain.count(Image):
            lst_img = event.message_chain.get(Image)
            imgurl = []
            for i in lst_img:
                url = i.url
                imgurl.append(url)
                #print(url)
        if event.sender.id in chatGLMCharacters:
            print(type(chatGLMCharacters.get(event.sender.id)), chatGLMCharacters.get(event.sender.id))
            r, firstRep = await modelReply(event.sender.member_name, event.sender.id, text,
                                           chatGLMCharacters.get(event.sender.id), trustUser, imgurl,True)
        # 判断模型
        else:
            r, firstRep = await modelReply(event.sender.member_name, event.sender.id, text, replyModel, trustUser, imgurl,True)
        if firstRep:
            await bot.send(event, "如对话异常请发送 /clear", True)
        #刷新时间
        user = str(event.sender.id)
        if user in chattingUser:
            chattingUser[user] = datetime.datetime.now()
        if withText:
            await bot.send(event, r, True)
        if len(r) < maxTextLen and random.randint(0, 100) < voiceRate and "出错，请重试" not in r:
            try:
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_文本" + r)
                logger.info("语音生成_模型:" + speaker)
                data = {"text": r, "out": path, 'speaker': speaker}
                voiceP = await superVG(data, mode=voicegenerateMode, urls="", langmode=voiceLangType)
                await bot.send(event, Voice(path=voiceP))
                return
            except Exception as e:
                logger.error(e)
                logger.error("语音合成失败")
        if not withText:
            await bot.send(event, r, True)

    # 用于chatGLM清除本地缓存
    @bot.on(GroupMessage)
    async def clearPrompt(event: GroupMessage):
        global chatGLMData, coziData
        if str(event.message_chain) == "/clear":
            reff = await clearsinglePrompt(event.sender.id)
            await bot.send(event, reff, True)
        elif str(event.message_chain) == "/allclear" and event.sender.id == master:
            reff = await clearAllPrompts()
            await bot.send(event, reff, True)
