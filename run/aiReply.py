# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
import random
import re
import shutil
import threading
from asyncio import sleep

import yaml
from mirai import At
from mirai import FriendMessage, GroupMessage, Image
from mirai import Voice, Startup
from mirai.models import NudgeEvent

from plugins.aiReplyCore import modelReply, clearAllPrompts, clearsinglePrompt
from plugins.toolkits import random_str
from plugins.vitsGenerate import superVG


def wontrep(noeRes1, text, logger):
    p1 = noeRes1.get("noResMatch1")
    text = text.replace("壁纸", "").replace("涩图", "").replace("色图", "").replace("图",
                                                                                    "").replace(
        "r18", "")
    for i in p1:
        if text == i:
            logger.warning(f"与屏蔽词 {i} 匹配，不回复")
            return False
    p2 = noeRes1.get("startswith")
    for i in p2:
        if str(text).startswith(i):
            logger.warning(f"与屏蔽词 {i} 匹配，不回复")
            return False
    p2 = noeRes1.get("endswith")
    for i in p2:
        if str(text).endswith(i):
            logger.warning(f"与屏蔽词 {i} 匹配，不回复")
            return False
    p2 = noeRes1.get("Regular")
    for i in p2:
        match1 = re.search(i, text)
        if match1:
            logger.warning(f"与表达式 {i} 匹配，不回复")
            return False
    return True


# 1
class CListen(threading.Thread):
    def __init__(self, loop):
        super().__init__()
        self.mLoop = loop

    def run(self):
        asyncio.set_event_loop(self.mLoop)  # 在新线程中开启一个事件循环

        self.mLoop.run_forever()


def main(bot, master, logger):
    class Main:
        def __init__(self):
            self.colorfulCharacterList = os.listdir("data/colorfulAnimeCharacter")
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                self.result = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.wReply = self.result.get("wReply")
            with open('config/welcome.yaml', 'r', encoding='utf-8') as f:
                wecYaml = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.chattingError = wecYaml.get("chattingError")
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                resul = yaml.load(f.read(), Loader=yaml.FullLoader)

            self.trustG = resul.get("trustGroups")
            # 读取个性化角色设定
            with open('data/chatGLMCharacters.yaml', 'r', encoding='utf-8') as f:
                result2223 = yaml.load(f.read(), Loader=yaml.FullLoader)

            self.chatGLMCharacters = result2223
            with open('config/api.yaml', 'r', encoding='utf-8') as f:
                resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
            proxy = resulttr.get("proxy")
            if proxy != "":
                os.environ["http_proxy"] = proxy
            with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
                cha = yaml.load(f.read(), Loader=yaml.FullLoader)

            self.chatGLMData = cha
            # logger.info(chatGLMData)
            with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
                self.noRes1 = yaml.load(f.read(), Loader=yaml.FullLoader)

            self.totallink = False
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.friendsAndGroups = result.get("加群和好友")
            self.trustDays = self.friendsAndGroups.get("trustDays")
            self.glmReply = result.get("chatGLM").get("glmReply")
            self.privateGlmReply = result.get("chatGLM").get("privateGlmReply")
            self.nudgeornot = result.get("chatGLM").get("nudgeReply")
            self.replyModel = result.get("chatGLM").get("model")
            self.MaxRecursionTimes = result.get("chatGLM").get("MaxRecursionTimes")
            self.multiplyReply = result.get("chatGLM").get("multiplyReply")
            self.multiplyReplyReExpression = result.get("chatGLM").get("multiplyReplyReExpression")
            self.trustglmReply = result.get("chatGLM").get("trustglmReply")
            self.allcharacters = result.get("chatGLM").get("bot_info")
            self.allowUserSetModel = result.get("chatGLM").get("allowUserSetModel")
            self.maxTextLen = result.get("chatGLM").get("maxLen")
            self.voiceRate = result.get("chatGLM").get("voiceRate")
            self.withText = result.get("chatGLM").get("withText")
            self.speaker = result.get("语音功能设置").get("speaker")
            self.voicegenerateMode = result.get("语音功能设置").get("voicegenerate")
            self.voiceLangType = result.get("语音功能设置").get("voiceLangType")
            with open('config.json', 'r', encoding='utf-8') as f:
                data = yaml.load(f.read(), Loader=yaml.FullLoader)
            config = data
            try:
                self.mainGroup = int(config.get("mainGroup"))
            except:
                logger.error("致命错误！mainGroup只能填写一个群的群号!")
                self.mainGroup = 0
            try:
                with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                    data = yaml.load(file, Loader=yaml.FullLoader)
            except Exception as e:
                # logger.error(e)
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

            self.userdict = data
            self.trustUser = []
            for i in self.userdict.keys():
                data = self.userdict.get(i)
                try:
                    times = int(str(data.get('sts')))
                    if times > self.trustDays:
                        self.trustUser.append(str(i))

                except Exception as e:
                    logger.error(f"用户{i}的sts数值出错，请打开data/userData.yaml检查，将其修改为正常数值")
            logger.info('chatglm部分已读取信任用户' + str(len(self.trustUser)) + '个')

            self.coziData = {}
            # 线程预备
            newLoop = asyncio.new_event_loop()
            listen = CListen(newLoop)
            listen.setDaemon(True)
            listen.start()

            self.chattingUser = {}  # 无需艾特即可对话的用户列表
            self.timeout = datetime.timedelta(minutes=5)  # 5分钟没有对话则超时

            # 递归计数
            self.RecurionDepthCount = {}

        @bot.on(GroupMessage)
        async def AddChatWithoutAt(self, event: GroupMessage):
            if str(event.message_chain) == "开始对话" or str(event.message_chain) == "开始聊天":
                user = str(event.sender.id)
                self.chattingUser[user] = datetime.datetime.now()
                await bot.send(event, "发送 退出 可退出当前对话", True)

        @bot.on(GroupMessage)
        async def removeChatWithoutAt(self, event: GroupMessage):

            if str(event.message_chain) == "退出" and str(event.sender.id) in self.chattingUser:
                user = str(event.sender.id)
                self.chattingUser.pop(user)
                await bot.send(event, "已结束当前对话", True)

        @bot.on(NudgeEvent)
        async def NudgeReply(self, event: NudgeEvent):
            # 戳一戳使用ai回复的话，和这部分放在一起会更好。
            if event.target == bot.qq and self.nudgeornot:
                logger.info("接收到来自" + str(event.from_id) + "的戳一戳")

                text = random.choice(["戳你一下", "摸摸头", "戳戳你的头", "摸摸~"])
                if event.from_id in self.chatGLMCharacters:
                    # print(chatGLMCharacters.get(event.target), type(chatGLMCharacters.get(event.target)))
                    r = await modelReply("指挥", event.from_id, text, self.chatGLMCharacters.get(event.from_id))
                # 判断模型类型
                else:
                    r = await modelReply("指挥", event.from_id, text)
                if r == "出错，请重试\n或联系master更换默认模型":
                    logger.warning("模型出错了，看来只有使用递归了凸(艹皿艹 )")
                    if event.from_id in self.RecurionDepthCount:
                        self.RecurionDepthCount[event.from_id] += 1
                        if self.RecurionDepthCount[event.from_id] > self.MaxRecursionTimes:
                            logger.warning("递归深度超过设置限度，自动退出。")
                            await bot.send(event, random.choice(self.chattingError))
                            self.RecurionDepthCount.pop(event.from_id)
                            return
                    else:
                        self.RecurionDepthCount[event.from_id] = 0
                    await clearsinglePrompt(event.from_id)
                    await self.NudgeReply(event)  # 真是递递又归归
                    return
                if self.withText:
                    await bot.send_group_message(event.subject.id, r)
                if len(r) < self.maxTextLen and random.randint(0, 100) < self.voiceRate and "出错，请重试" not in r:
                    try:
                        path = 'data/voices/' + random_str() + '.wav'
                        logger.info("语音生成_文本" + r)
                        logger.info("语音生成_模型:" + self.speaker)
                        data = {"text": r, "out": path, 'speaker': self.speaker}
                        voiceP = await superVG(data, mode=self.voicegenerateMode, urls="", langmode=self.voiceLangType)
                        await bot.send_group_message(event.subject.id, Voice(path=voiceP))
                        return
                    except:
                        logger.error("语音合成调用失败")
                if not self.withText:
                    await bot.send_group_message(event.subject.id, r)

        # 私聊使用chatGLM,对信任用户或配置了apiKey的用户开启
        @bot.on(FriendMessage)
        async def GLMFriendChat(self, event: FriendMessage):
            # 用非常丑陋的复制粘贴临时解决bug，这下成石山代码了

            text = str(event.message_chain)
            if text == "/clear":
                return
            if event.sender.id == master:
                noresm = ["群列表", "/bl", "退群#", "/quit"]
                for saa in noresm:
                    if text == saa or text.startswith(saa):
                        logger.warning("与屏蔽词匹配，不回复")
                        return
            if self.privateGlmReply or (self.trustglmReply and str(event.sender.id) in self.trustUser):
                pass
            else:
                return

            text = str(event.message_chain)  # 初始text
            imgurl = None
            if event.message_chain.count(Image):
                lst_img = event.message_chain.get(Image)
                imgurl = [i.url for i in lst_img]

            if event.sender.id in self.chatGLMCharacters:
                print(type(self.chatGLMCharacters.get(event.sender.id)), self.chatGLMCharacters.get(event.sender.id))
                r, firstRep = await modelReply(event.sender.nickname, event.sender.id, text,
                                               self.chatGLMCharacters.get(event.sender.id), self.trustUser, imgurl,
                                               checkIfRepFirstTime=True)
            else:
                r, firstRep = await modelReply(event.sender.nickname, event.sender.id, text, self.replyModel,
                                               self.trustUser,
                                               imgurl,
                                               checkIfRepFirstTime=True)

            # if firstRep:
            # await bot.send(event, "如对话异常请发送 /clear 以清理对话", True)
            if r == "出错，请重试\n或联系master更换默认模型":
                logger.warning("模型出错了，看来只有使用递归了凸(艹皿艹 )")
                if event.sender.id in self.RecurionDepthCount:
                    self.RecurionDepthCount[event.sender.id] += 1
                    if self.RecurionDepthCount[event.sender.id] > self.MaxRecursionTimes:
                        logger.warning("递归深度超过设置限度，自动退出。")
                        await bot.send(event, random.choice(self.chattingError))
                        self.RecurionDepthCount.pop(event.sender.id)
                        return
                else:
                    self.RecurionDepthCount[event.sender.id] = 0
                await clearsinglePrompt(event.sender.id)
                await self.GLMFriendChat(event)  # 真是递递又归归
                return
            if self.withText:
                if self.multiplyReply:
                    sentences = re.split(self.multiplyReplyReExpression, r)
                    check_num = 0
                    for sentence in sentences:
                        if sentence:
                            check_num += 1
                            if check_num == 3:
                                await bot.send(event, "".join(sentences[2:]).strip(),
                                               True if random.random() < 0.35 else None)
                                if random.randint(0, 100) < self.wReply.get("colorfulCharacter"):
                                    logger.info("本次使用彩色小人替代匹配回复")
                                    c = random.choice(self.colorfulCharacterList)
                                    await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                                break
                            await bot.send(event, sentence.strip(), True if random.random() < 0.35 else None)
                            if random.randint(0, 100) < self.wReply.get("colorfulCharacter"):
                                logger.info("本次使用彩色小人替代匹配回复")
                                c = random.choice(self.colorfulCharacterList)
                                await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                            waitTime = random.randint(1, 6)
                            await sleep(waitTime)
                else:
                    await bot.send(event, r, True)

            if (len(r) < self.maxTextLen and random.randint(0,
                                                            100) < self.voiceRate and "出错，请重试" not in r) or not self.withText:
                try:
                    path = 'data/voices/' + random_str() + '.wav'
                    logger.info("语音生成_文本" + r)
                    logger.info("语音生成_模型:" + self.speaker)
                    data = {"text": r, "out": path, 'speaker': self.speaker}
                    voiceP = await superVG(data, mode=self.voicegenerateMode, urls="", langmode=self.voiceLangType)
                    await bot.send(event, Voice(path=voiceP))
                    return
                except:
                    logger.error("语音合成调用失败")
                    if not self.withText:
                        await bot.send(event, r, True)

        # 私聊中chatGLM清除本地缓存
        @bot.on(FriendMessage)
        async def clearPrompt(self, event: FriendMessage):

            if str(event.message_chain) == "/clear":
                reff = await clearsinglePrompt(event.sender.id)
                await bot.send(event, reff, True)
            elif str(event.message_chain) == "/allclear" and event.sender.id == master:
                reff = await clearAllPrompts()
                await bot.send(event, reff, True)

        # 私聊设置bot角色
        # print(trustUser)
        @bot.on(FriendMessage)
        async def showCharacter(self, event: FriendMessage):
            if str(event.message_chain) == "可用角色模板" or "角色模板" in str(event.message_chain):
                st1 = ""
                for isa in self.allcharacters:
                    st1 += isa + "\n"
                await bot.send(event, "对话可用角色模板：\n" + st1 + "\n发送：设定#角色名 以设定角色")

        @bot.on(FriendMessage)
        async def setCharacter(self, event: FriendMessage):

            if str(event.message_chain).startswith("设定#"):
                if str(event.message_chain).split("#")[1] in self.allcharacters and self.allowUserSetModel:
                    meta12 = str(event.message_chain).split("#")[1]

                    self.chatGLMCharacters[event.sender.id] = meta12
                    logger.info("当前：" + str(self.chatGLMCharacters))
                    with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(self.chatGLMCharacters, file, allow_unicode=True)
                    await bot.send(event, "设定成功")
                else:
                    if self.allowUserSetModel:
                        await bot.send(event, "不存在的角色")
                    else:
                        await bot.send(event, "禁止用户自行设定模型(可联系master修改配置)")

        # print(trustUser)
        @bot.on(GroupMessage)
        async def showCharacter(self, event: GroupMessage):
            if str(event.message_chain) == "可用角色模板" or (
                    At(bot.qq) in event.message_chain and "角色模板" in str(event.message_chain)):
                st1 = ""
                for isa in self.allcharacters:
                    st1 += isa + "\n"
                await bot.send(event, "对话可用角色模板：\n" + st1 + "\n发送：设定#角色名 以设定角色")

        @bot.on(GroupMessage)
        async def setCharacter(self, event: GroupMessage):
            if str(event.message_chain).startswith("设定#"):
                if str(event.message_chain).split("#")[1] in self.allcharacters and self.allowUserSetModel:
                    meta12 = str(event.message_chain).split("#")[1]
                    self.chatGLMCharacters[event.sender.id] = meta12
                    logger.info("当前：" + str(self.chatGLMCharacters))
                    with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(self.chatGLMCharacters, file, allow_unicode=True)
                    await bot.send(event, "设定成功")
                else:
                    if self.allowUserSetModel:
                        await bot.send(event, "不存在的角色")
                    else:
                        await bot.send(event, "禁止使用此指令。")

        @bot.on(Startup)
        async def upDate(self, event: Startup):
            while True:
                await sleep(60)
                with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                    data = yaml.load(file, Loader=yaml.FullLoader)

                self.userdict = data
                self.trustUser = []
                for i in self.userdict.keys():
                    data = self.userdict.get(i)
                    times = int(str(data.get('sts')))
                    if times > self.trustDays:
                        self.trustUser.append(str(i))
                # 定时清理用户

                now = datetime.datetime.now()
                to_remove = [user for user, timestamp in self.chattingUser.items() if now - timestamp > self.timeout]
                for user in to_remove:
                    del self.chattingUser[user]
                    logger.info(f"Removed user {user} due to inactivity")

        @bot.on(GroupMessage)
        async def upddd(self, event: GroupMessage):
            if str(event.message_chain).startswith("授权") and event.sender.id == master:
                await sleep(15)
                with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                    resul = yaml.load(f.read(), Loader=yaml.FullLoader)

                self.trustG = resul.get("trustGroups")
                with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                    data = yaml.load(file, Loader=yaml.FullLoader)

                self.userdict = data
                self.trustUser = []
                for i in self.userdict.keys():
                    data = self.userdict.get(i)
                    times = int(str(data.get('sts')))
                    if times > self.trustDays:
                        self.trustUser.append(str(i))
                logger.info('已读取信任用户' + str(len(self.trustUser)) + '个')

        # 群内chatGLM回复
        @bot.on(GroupMessage)
        async def atReply(self, event: GroupMessage):
            if At(bot.qq) in event.message_chain or str(event.sender.id) in self.chattingUser:
                try:
                    if not wontrep(self.noRes1, str(event.message_chain).replace(str(At(bot.qq)), "").replace(" ", ""),
                                   logger):
                        return
                except Exception as e:
                    logger.error(f"无法运行屏蔽词审核，请检查noResponse.yaml配置格式--{e}")
            if (At(bot.qq) in event.message_chain or str(event.sender.id) in self.chattingUser) and (
                    self.glmReply or (self.trustglmReply and str(
                event.sender.id) in self.trustUser) or event.group.id in self.trustG or event.group.id == int(
                self.mainGroup)):
                logger.info("ai聊天启动")
                text = str(event.message_chain).replace("@" + str(bot.qq) + "", '')
            else:
                if str(event.message_chain).startswith(self.result.get("chatGLM").get("prefix")):
                    text = str(event.message_chain).replace(self.result.get("chatGLM").get("prefix"), '')
                elif self.result.get("chatGLM").get("随机触发对话") and random.random() < float(
                        self.result.get("chatGLM").get("随机触发几率")):
                    text = str(event.message_chain)
                else:
                    return

            imgurl: list = []
            if event.message_chain.count(Image):
                lst_img = event.message_chain.get(Image)
                imgurl = [i.url for i in lst_img]

            if event.sender.id in self.chatGLMCharacters:
                print(type(self.chatGLMCharacters.get(event.sender.id)), self.chatGLMCharacters.get(event.sender.id))
                r, firstRep = await modelReply(event.sender.member_name, event.sender.id, text,
                                               self.chatGLMCharacters.get(event.sender.id), self.trustUser, imgurl,
                                               True)
            # 判断模型
            else:
                r, firstRep = await modelReply(event.sender.member_name, event.sender.id, text, self.replyModel,
                                               self.trustUser,
                                               imgurl, True)
            # if firstRep:
            # await bot.send(event, "如对话异常请发送 /clear", True)
            if r == "出错，请重试\n或联系master更换默认模型":
                logger.warning("模型出错了，看来只有使用递归了凸(艹皿艹 )")
                if event.sender.id in self.RecurionDepthCount:
                    self.RecurionDepthCount[event.sender.id] += 1
                    if self.RecurionDepthCount[event.sender.id] > self.MaxRecursionTimes:
                        logger.warning("递归深度超过设置限度，自动退出。")
                        await bot.send(event, random.choice(self.chattingError))
                        self.RecurionDepthCount.pop(event.sender.id)
                        return
                else:
                    self.RecurionDepthCount[event.sender.id] = 0
                await clearsinglePrompt(event.sender.id)
                await self.atReply(event)  # 真是递递又归归
                return
            # 刷新时间
            user = str(event.sender.id)
            if user in self.chattingUser:
                self.chattingUser[user] = datetime.datetime.now()
            if self.withText:
                if self.multiplyReply:
                    sentences = re.split(self.multiplyReplyReExpression, r)
                    check_num = 0
                    for sentence in sentences:
                        if sentence:
                            check_num += 1
                            if check_num == 3:
                                await bot.send(event, [At(event.sender.id) if random.random() < 0.25 else '',
                                                       "".join(sentences[2:]).strip()],
                                               True if random.random() < 0.35 else None)
                                if random.randint(0, 100) < self.wReply.get("colorfulCharacter"):
                                    logger.info("本次使用彩色小人替代匹配回复")
                                    c = random.choice(self.colorfulCharacterList)
                                    await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                                break
                            await bot.send(event,
                                           [At(event.sender.id) if random.random() < 0.25 else '', sentence.strip()],
                                           True if random.random() < 0.35 else None)
                            if random.randint(0, 100) < self.wReply.get("colorfulCharacter"):
                                logger.info("本次使用彩色小人替代匹配回复")
                                c = random.choice(self.colorfulCharacterList)
                                await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                            waitTime = random.randint(1, 6)
                            await sleep(waitTime)
                else:
                    await bot.send(event, r, True)
            if (len(r) < self.maxTextLen and random.randint(0,
                                                            100) < self.voiceRate and "出错，请重试" not in r) or not self.withText:
                try:
                    path = 'data/voices/' + random_str() + '.wav'
                    logger.info("语音生成_文本" + r)
                    logger.info("语音生成_模型:" + self.speaker)
                    data = {"text": r, "out": path, 'speaker': self.speaker}
                    voiceP = await superVG(data, mode=self.voicegenerateMode, urls="", langmode=self.voiceLangType)
                    await bot.send(event, Voice(path=voiceP))
                    return
                except Exception as e:
                    logger.error(e)
                    logger.error("语音合成失败")
                    if not self.withText:
                        await bot.send(event, r, True)

        # 用于chatGLM清除本地缓存
        @bot.on(GroupMessage)
        async def clearPrompt(self, event: GroupMessage):
            if str(event.message_chain) == "/clear":
                reff = await clearsinglePrompt(event.sender.id)
                await bot.send(event, reff, True)
            elif str(event.message_chain) == "/allclear" and event.sender.id == master:
                reff = await clearAllPrompts()
                await bot.send(event, reff, True)
            elif str(event.message_chain).startswith("/clear") and event.sender.id == master:
                message_content = event.message_chain
                for element in message_content:
                    if isinstance(element, At):
                        target_qq = element.target
                        reff = await clearsinglePrompt(target_qq)
                        await bot.send(event, reff, True)

    return Main()
