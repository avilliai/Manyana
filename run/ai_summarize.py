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


    ##########################
    #### 聊天总结功能
    ##########################

    # Create a connection to the database
    def create_connection():
        return sqlite3.connect('group_messages_v2.db')

    # Dynamically create a table for each group
    def create_group_table(group_id):
        conn = create_connection()
        cursor = conn.cursor()
        table_name = f"GroupMessages_{group_id}"
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            message_content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()

    # Store a group message in the corresponding group's table
    def store_group_message(sender_id, sender_name, group_id, message_content, timestamp=None):
        create_group_table(group_id)  # Ensure the table for the group exists
        conn = create_connection()
        cursor = conn.cursor()
        table_name = f"GroupMessages_{group_id}"

        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp

        cursor.execute(f'''
        INSERT INTO {table_name} (sender_id, sender_name, message_content, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (sender_id, sender_name, message_content, timestamp))
        conn.commit()
        logger.info(f"Stored message in table {table_name}.")
        conn.close()

    # Fetch recent messages for a specific group (from oldest to newest, with a limit of 1000)
    def fetch_recent_messages(group_id, max_words=2000, max_messages=1000):
        conn = create_connection()
        cursor = conn.cursor()
        table_name = f"GroupMessages_{group_id}"

        # Fetch the most recent 1000 messages, ordered by timestamp in descending order, then reverse to get oldest-to-newest
        cursor.execute(f'''
        SELECT sender_id, sender_name, message_content, timestamp FROM {table_name}
        ORDER BY timestamp DESC
        LIMIT {max_messages}
        ''')

        rows = cursor.fetchall()
        conn.close()

        # Reverse the fetched rows to get them in oldest-to-newest order
        rows.reverse()

        # Combine messages into a single string while limiting the total word count
        message_list = []
        word_count = 0
        for row in rows:
            sender_id, sender_name, message_content, timestamp = row
            words_in_message = len(message_content.split())
            if word_count + words_in_message > max_words:
                break
            # Append each message with its sender and timestamp
            message_list.append(f"[{timestamp}] {sender_name}({sender_id}): {message_content}")
            word_count += words_in_message

        return message_list

    # Handle storing of group messages
    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        sender_id = event.sender.id
        sender_name = event.sender.member_name
        group_id = event.group.id
        message_content = str(event.message_chain)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # skip the message if it is a summary request
        if str(event.message_chain) == "生成总结":
            return

        try:
            # Store the message in the respective group table
            store_group_message(sender_id, sender_name, group_id, message_content, timestamp)
        except Exception as e:
            logger.warning(f"Failed to store group message from {sender_id} in group {group_id}: {e}")


    # Handle group summary request
    @bot.on(GroupMessage)
    async def summarizing_request_group(event: GroupMessage):
        group_id = event.group.id
        sender_id = event.sender.id
        sender_name = event.sender.member_name
        # Check if the request is for generating a summary
        if str(event.message_chain) == "生成总结" and sender_id == master and group_id == mainGroup:
            summary = await handle_summarizing_request(sender_name=sender_name, sender_id=sender_id, group_id=group_id)
            await bot.send(event, summary, True)


    @bot.on(FriendMessage)
    async def summarizing_request_friend(event: FriendMessage):
        sender_id = event.sender.id
        friend_name = event.sender.nickname
        if str(event.message_chain) == "生成总结":
            await bot.send(event, "TIP: 请发送  生成总结#群号  以生成对应群的总结", True)
        elif str(event.message_chain).startswith("生成总结#"):
            group_id = str(event.message_chain).split("#")[1]
            if not group_id.isdigit() or len(group_id) < 5:
                await bot.send(event, "TIP: 请发送  生成总结#群号  以生成对应群的总结", True)
            elif group_id in trustG or group_id == str(mainGroup):
                summary = await handle_summarizing_request(sender_id=sender_id, sender_name=friend_name, group_id=group_id)
                await bot.send(event, summary, True)
            else: await bot.send(event, "ERROR: 该群聊尚未被添加 / 群聊号码错误", True)


    async def handle_summarizing_request(sender_id, sender_name, group_id):
        logger.info("Received summary request")
        try:
            # Fetch recent messages from the database for the specific group
            recent_messages = fetch_recent_messages(group_id, max_words=2000, max_messages=1000)
            logger.info(f"Fetched {len(recent_messages)} recent messages for group {group_id}")

            # Combine the messages into a single context string
            context = "请总结如下聊天的话题，以及对应话题活跃人员, 提及人员时以【成员昵称】【成员账号】的形式表示: \n" + "\n".join(recent_messages)
            logger.info(f"Generated full prompt for group {group_id}: {context}")

            # Generate a summary using the context (call your LLM API here)
            summary = await direct_sending_to_model(
                sender_name=sender_name,
                sender_id=sender_id,
                text=context
            )
            logger.info(f"Generated summary for group {group_id}")

            return f"对于群聊ID: {group_id} 的总结如下: \n ========================\n" + str(summary)

        except Exception as error:
            logger.warning(f"Failed to generate summary for group {group_id}: {error}")
            return "出错啦！生成总结失败，请稍后再试！频繁出现该问题请报告给本服务管理者"