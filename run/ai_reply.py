# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
import random
import shutil
import threading
from asyncio import sleep
import sqlite3  # 导入sqlite3模块储存聊天数据，用于总结功能

import yaml
from mirai import FriendMessage, GroupMessage, At, Image
from mirai import Voice, Startup
from mirai.models import NudgeEvent

from plugins.aiReplyCore import modelReply, clearAllPrompts, tstt, clearsinglePrompt, direct_sending_to_model, logger
from plugins.wReply.wontRep import wontrep


# 1
class CListen(threading.Thread):
    def __init__(self, loop):
        threading.Thread.__init__(self)
        self.mLoop = loop

    def run(self):
        asyncio.set_event_loop(self.mLoop)  # 在新线程中开启一个事件循环

        self.mLoop.run_forever()


def initialize_database():
    conn = sqlite3.connect('group_messages.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS GroupMessages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT NOT NULL,
        group_id TEXT NOT NULL,
        message_content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def fetch_recent_messages(group_id, max_words=2000):
    logger.info("Fetching recent messages from the database")
    conn = sqlite3.connect('group_messages.db')
    cursor = conn.cursor()

    # Fetch the most recent messages from the database, ordering by timestamp in descending order
    cursor.execute('''
    SELECT message_content FROM GroupMessages 
    WHERE group_id = ? 
    ORDER BY timestamp DESC
    ''', (group_id,))

    messages = cursor.fetchall()
    conn.close()

    # Prepare the result and count words
    recent_messages = []
    total_words = 0

    for message in messages:
        words_in_message = len(message[0].split())
        if total_words + words_in_message <= max_words:
            recent_messages.append(message[0])
            total_words += words_in_message
        else:
            break

    return list(reversed(recent_messages))  # Reverse to maintain the original order

# Helper function for setting up user and group configurations
def setup_config():
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        resul = yaml.load(f.read(), Loader=yaml.FullLoader)
    global trustG
    trustG = resul.get("trustGroups")

    with open('data/chatGLMCharacters.yaml', 'r', encoding='utf-8') as f:
        global chatGLMCharacters
        chatGLMCharacters = yaml.load(f.read(), Loader=yaml.FullLoader)

    with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
        global chatGLMData
        chatGLMData = yaml.load(f.read(), Loader=yaml.FullLoader)

    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    return result


def main(bot, master, logger):
    initialize_database()  # Initialize the database

    config = setup_config()
    friends_and_groups = config.get("加群和好友")
    trust_days = friends_and_groups.get("trustDays")
    reply_model = config.get("chatGLM").get("model")
    max_text_len = config.get("chatGLM").get("maxLen")
    voice_rate = config.get("chatGLM").get("voiceRate")
    with_text = config.get("chatGLM").get("withText")

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


    glmReply = result.get("chatGLM").get("glmReply")
    privateGlmReply = result.get("chatGLM").get("privateGlmReply")
    nudgeornot = result.get("chatGLM").get("nudgeReply")

    trustglmReply = result.get("chatGLM").get("trustglmReply")
    allcharacters = result.get("chatGLM").get("bot_info")
    allowUserSetModel = result.get("chatGLM").get("allowUserSetModel")
    maxTextLen = result.get("chatGLM").get("maxLen")
    voiceRate = result.get("chatGLM").get("voiceRate")
    withText = result.get("chatGLM").get("withText")

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
    global trustUser
    global userdict
    userdict = data
    trustUser = []
    for i in userdict.keys():
        data = userdict.get(i)
        try:
            times = int(str(data.get('sts')))
            if times > trust_days:
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
    chattingUser = {}  # 无需艾特即可对话的用户列表
    timeout = datetime.timedelta(minutes=5)  # 5分钟没有对话则超时

    @bot.on(GroupMessage)
    async def AddChatWithoutAt(event: GroupMessage):
        if str(event.message_chain) == "开始对话" or str(event.message_chain) == "开始聊天":
            global chattingUser
            user = str(event.sender.id)
            chattingUser[user] = datetime.datetime.now()
            await bot.send(event, "发送 退出 可退出当前对话", True)

    @bot.on(GroupMessage)
    async def removeChatWithoutAt(event: GroupMessage):
        global chattingUser
        if str(event.message_chain) == "退出" and str(event.sender.id) in chattingUser:
            user = str(event.sender.id)
            chattingUser.pop(user)
            await bot.send(event, "已结束当前对话", True)

    @bot.on(NudgeEvent)
    async def NudgeReply(event: NudgeEvent):
        global trustUser
        # 戳一戳使用ai回复的话，和这部分放在一起会更好。
        if event.target == bot.qq and nudgeornot:
            global chatGLMCharacters
            logger.info("接收到来自" + str(event.from_id) + "的戳一戳")

            text = random.choice(["戳你一下", "摸摸头", "戳戳你的头", "摸摸~"])
            if event.from_id in chatGLMCharacters:
                # print(chatGLMCharacters.get(event.target), type(chatGLMCharacters.get(event.target)))
                r = await modelReply("指挥", event.from_id, text, chatGLMCharacters.get(event.from_id))
            # 判断模型类型
            else:
                r = await modelReply("指挥", event.from_id, text)
            if len(r) < maxTextLen and random.randint(0, 100) < voiceRate:
                try:
                    voiceP = await tstt(r)
                    await bot.send_group_message(event.subject.id, Voice(path=voiceP))
                    if withText:
                        await bot.send_group_message(event.subject.id, r)
                except:
                    logger.error("语音合成调用失败")
                    await bot.send_group_message(event.subject.id, r)
            else:
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
                                           chatGLMCharacters.get(event.sender.id), trustUser, imgurl,
                                           checkIfRepFirstTime=True)
        # 判断模型
        else:
            r, firstRep = await modelReply(event.sender.nickname, event.sender.id, text, reply_model, trustUser, imgurl,
                                           checkIfRepFirstTime=True)
        if firstRep:
            await bot.send(event, "如对话异常请发送 /clear 以清理对话", True)
        if len(r) < maxTextLen and random.randint(0, 100) < voiceRate:
            try:
                voiceP = await tstt(r)
                await bot.send(event, Voice(path=voiceP))
                if withText:
                    await bot.send(event, r, True)
            except:
                logger.error("语音合成调用失败")
                await bot.send(event, r, True)
        else:
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
                if times > trust_days:
                    trustUser.append(str(i))
            # 定时清理用户
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
                if times > trust_days:
                    trustUser.append(str(i))
            logger.info('已读取信任用户' + str(len(trustUser)) + '个')

    # 群内chatGLM回复
    @bot.on(GroupMessage)
    async def atReply(event: GroupMessage):
        global trustUser, chatGLMData, chatGLMCharacters, userdict, coziData, trustG, chattingUser
        if At(bot.qq) in event.message_chain or str(event.sender.id) in chattingUser:
            try:
                if not wontrep(noRes1, str(event.message_chain).replace(str(At(bot.qq)), "").replace(" ", ""),
                               logger):
                    return
            except Exception as e:
                logger.error(f"无法运行屏蔽词审核，请检查noResponse.yaml配置格式--{e}")
        if (At(bot.qq) in event.message_chain or str(event.sender.id) in chattingUser) and (
                glmReply or (trustglmReply and str(
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
                # print(url)
        if event.sender.id in chatGLMCharacters:
            print(type(chatGLMCharacters.get(event.sender.id)), chatGLMCharacters.get(event.sender.id))
            r, firstRep = await modelReply(event.sender.member_name, event.sender.id, text,
                                           chatGLMCharacters.get(event.sender.id), trustUser, imgurl, True)
        # 判断模型
        else:
            r, firstRep = await modelReply(event.sender.member_name, event.sender.id, text, reply_model, trustUser,
                                           imgurl, True)
        if firstRep:
            await bot.send(event, "如对话异常请发送 /clear", True)
        # 刷新时间
        user = str(event.sender.id)
        if user in chattingUser:
            chattingUser[user] = datetime.datetime.now()
        if len(r) < maxTextLen and random.randint(0, 100) < voiceRate:
            try:
                voiceP = await tstt(r)
                await bot.send(event, Voice(path=voiceP))
                if withText:
                    await bot.send(event, r, True)
            except Exception as e:
                logger.error(e)
                logger.error("语音合成失败")
                await bot.send(event, r, True)
        else:
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



    ##########################
    #### 聊天总结功能
    #### TODO - 解耦合、改进数据库结构和轮询方式
    ##########################

    # 用于储存聊天数据
    def store_group_message(sender_id, group_id, message_content):
        conn = sqlite3.connect('group_messages.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO GroupMessages (sender_id, group_id, message_content)
        VALUES (?, ?, ?)
        ''', (sender_id, group_id, message_content))
        conn.commit()
        logger.info("已储存 GroupMessage 至数据库")
        conn.close()

    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        sender_id = event.sender.id
        group_id = event.group.id
        message_content = str(event.message_chain)

        try:
            # Attempt to store the message in the database
            store_group_message(sender_id, group_id, message_content)
        except Exception as e:
            # Log a warning if storing the message fails
            logger.warning(f"Failed to store group message from {sender_id} in group {group_id}: {e}")

        # Additional logic (if any) can be placed here

    @bot.on(GroupMessage)
    async def summarizing_request(event: GroupMessage):
        sender_id = event.sender.id
        group_id = event.group.id

        # Check if the request is for generating a summary
        if str(event.message_chain) == "生成总结" and event.group.id in trustG or event.group.id == int(mainGroup):
            logger.info("收到总结请求")
            try:
                # Fetch recent messages from the database
                recent_messages = fetch_recent_messages(group_id, max_words=2000)
                logger.info(f"Fetched {len(recent_messages)} recent messages for group {group_id}")

                # Combine the messages into a single context string
                context = "请总结如下聊天的话题，以及对应话题活跃人员:\n" + "\n".join(recent_messages)
                logger.info(f"Generated full prompt for group {group_id}: {context}")

                # Generate a summary using the context (call your LLM API here)
                summary = await direct_sending_to_model(
                    sender_name=event.sender.member_name,
                    sender_id=event.sender.id,
                    text=context
                )
                logger.info(f"Generated summary for group {group_id}: {summary}")

                # Send the summary back to the group
                await bot.send(event, str(summary), True)
                logger.info(f"Sent summary to group {group_id}")

            except Exception as e:
                await bot.send(event, "生成总结失败，请稍后再试", True)
                logger.warning(f"Failed to generate summary for group {group_id}: {e}")

        else:
            return