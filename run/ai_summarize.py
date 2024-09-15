# -*- coding: utf-8 -*-
"""
This module provides functionalities for summarizing group chat messages using a chatbot.
It includes classes and functions for setting up configurations, handling group and friend messages,
storing messages in a database, and generating summaries.

Plugin Dependencies:
- mirai
- manyana main program
- aiReplyCore.py

version: 1.0.0
author: Bol_C
date: 2024-09-07

"""

import asyncio
import datetime
import os
import shutil
import threading
import sqlite3
import time
import yaml
from mirai import FriendMessage, GroupMessage, At, Image, TempMessage

from plugins.aiReplyCore import modelReply, clearAllPrompts, tstt, clearsinglePrompt, direct_sending_to_model, logger
from plugins.wReply.wontRep import wontrep

# Cooldown management (in seconds)
COOLDOWN_PERIOD = 900  # 15 minutes
cooldown_tracker = {}  # Dictionary to track last request time by sender_id


class CListen(threading.Thread):
    """
    A class to create a new thread for running an asyncio event loop.
    """

    def __init__(self, loop):
        """
        Initialize the thread with an event loop.

        :param loop: The asyncio event loop to run in the new thread.
        """
        threading.Thread.__init__(self)
        self.mLoop = loop

    def run(self):
        """
        Run the event loop in the new thread.
        """
        asyncio.set_event_loop(self.mLoop)  # Set the event loop for the new thread
        self.mLoop.run_forever()


def setup_config():
    """
    Helper function to set up user and group configurations.

    :return: The configuration settings.
    """
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

def is_cooldown_active(sender_id):
    """
    Check if the cooldown is active for the sender.

    :param sender_id: The ID of the sender.
    :return: True if the sender is still in cooldown, False otherwise.
    """
    current_time = time.time()
    if sender_id in cooldown_tracker:
        last_request_time = cooldown_tracker[sender_id]
        if current_time - last_request_time < COOLDOWN_PERIOD:
            remaining_time = COOLDOWN_PERIOD - (current_time - last_request_time)
            return True, remaining_time
    return False, 0


def update_cooldown(sender_id):
    """
    Update the cooldown tracker with the current time for the sender.

    :param sender_id: The ID of the sender.
    """
    cooldown_tracker[sender_id] = time.time()

def main(bot, master, logger):
    """
    Main function to initialize configurations and set up event handlers for the bot.

    :param bot: The bot instance.
    :param master: The master user ID.
    :param logger: The logger instance.
    """
    config = setup_config()
    friends_and_groups = config.get("加群和好友")
    trust_days = friends_and_groups.get("trustDays")

    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        auto_settings = yaml.load(f.read(), Loader=yaml.FullLoader)
    global trustG
    trustG = auto_settings.get("trustGroups")
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        api_settings = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = api_settings.get("proxy")
    if proxy != "":
        os.environ["http_proxy"] = proxy

    with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
        no_response_settings = yaml.load(f.read(), Loader=yaml.FullLoader)
    global totallink
    totallink = False
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        global_settings = yaml.load(f.read(), Loader=yaml.FullLoader)

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
            logger.error(f"用户{i}的sts数值出错, 请打开data/userData.yaml检查，将其修改为正常数值")
    logger.info('chatglm部分已读取信任用户' + str(len(trustUser)) + '个')

    global coziData
    coziData = {}

    # 线程预备
    newLoop = asyncio.new_event_loop()
    listen = CListen(newLoop)
    listen.setDaemon(True)
    listen.start()

    # Create a connection to the database
    def create_connection():
        """
        Create a connection to the SQLite database.

        :return: The SQLite connection object.
        """
        return sqlite3.connect('group_messages_v2.db')

    # Dynamically create a table for each group
    def create_group_table(group_id):
        """
        Dynamically create a table for each group to store messages.

        :param group_id: The ID of the group.
        """
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
        """
        Store a group message in the corresponding group's table.

        :param sender_id: The ID of the message sender.
        :param sender_name: The name of the message sender.
        :param group_id: The ID of the group.
        :param message_content: The content of the message.
        :param timestamp: The timestamp of the message.
        """
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
        """
        Fetch recent messages for a specific group.

        :param group_id: The ID of the group.
        :param max_words: The maximum number of words to fetch.
        :param max_messages: The maximum number of messages to fetch.
        :return: A list of recent messages.
        """
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
        """
        Handle storing of group messages.

        :param event: The group message event.
        """
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
        """
        Handle group summary request.

        :param event: The group message event.
        """
        group_id = event.group.id
        sender_id = event.sender.id
        sender_name = event.sender.member_name

        cooldown_active, remaining_time = is_cooldown_active(sender_id)
        if cooldown_active:
            await bot.send(event, f"请稍后再试，冷却时间还剩 {int(remaining_time)} 秒。", True)
            return

        if str(event.message_chain) == "生成总结" and sender_id == master and group_id == mainGroup:
            summary = await handle_summarizing_request(sender_name, sender_id, group_id)
            await bot.send(event, summary, True)
            update_cooldown(sender_id)  # Update cooldown after successful request

    @bot.on(FriendMessage)
    async def summarizing_request_friend(event: FriendMessage):
        """
        Handle friend summary request.

        :param event: The friend message event.
        """
        sender_id = event.sender.id
        friend_name = event.sender.nickname
        if str(event.message_chain) == "生成总结":
            await bot.send(event, "TIP: 请发送  生成总结#群号  以生成对应群的总结", True)
        elif str(event.message_chain).startswith("生成总结#"):
            group_id = str(event.message_chain).split("#")[1]
            if not group_id.isdigit() or len(group_id) < 5:
                await bot.send(event, "TIP: 请发送  生成总结#群号  以生成对应群的总结", True)
            elif True:

                cooldown_active, remaining_time = is_cooldown_active(sender_id)
                if cooldown_active:
                    await bot.send(event, f"请稍后再试，冷却时间还剩 {int(remaining_time)} 秒。", True)
                    return

                summary = await handle_summarizing_request(sender_id=sender_id, sender_name=friend_name,
                                                           group_id=group_id)
                await bot.send(event, summary, True)
                update_cooldown(sender_id)
            else:
                await bot.send(event, "ERROR: 该群聊尚未被添加 / 群聊号码错误", True)


    #
    # @bot.on(TempMessage)
    # async def summarizing_request_temp_msg(event: TempMessage):
    #     """
    #     Handle friend summary request.
    #
    #     :param event: The friend message event.
    #     """
    #     sender_id = event.sender.id
    #     sender_name = event.sender.member_name
    #     if str(event.message_chain) == "生成总结":
    #         await bot.send(event, "TIP: 请发送  生成总结#群号  以生成对应群的总结", True)
    #     elif str(event.message_chain).startswith("生成总结#"):
    #         group_id = str(event.message_chain).split("#")[1]
    #         if not group_id.isdigit() or len(group_id) < 5:
    #             await bot.send(event, "TIP: 请发送  生成总结#群号  以生成对应群的总结", True)
    #         elif group_id in trustG or group_id == str(mainGroup):
    #
    #             cooldown_active, remaining_time = is_cooldown_active(sender_id)
    #             if cooldown_active:
    #                 await bot.send(event, f"请稍后再试，冷却时间还剩 {int(remaining_time)} 秒。", True)
    #                 return
    #
    #             summary = await handle_summarizing_request(sender_id=sender_id, sender_name=sender_name,
    #                                                        group_id=group_id)
    #             await bot.send(event, summary, True)
    #             update_cooldown(sender_id)
    #         else:
    #             await bot.send(event, "ERROR: 该群聊尚未被添加 / 群聊号码错误", True)

    async def handle_summarizing_request(sender_id, sender_name, group_id):
        """
        Handle the summarizing request by fetching recent messages and generating a summary.

        :param sender_id: The ID of the sender.
        :param sender_name: The name of the sender.
        :param group_id: The ID of the group.
        :return: The generated summary.
        """
        logger.info("Received summary request")
        try:
            # Fetch recent messages from the database for the specific group
            recent_messages = fetch_recent_messages(group_id, max_words=2000, max_messages=1000)
            logger.info(f"Fetched {len(recent_messages)} recent messages for group {group_id}")

            # Combine the messages into a single context string
            context = "请总结如下聊天的话题，以及对应话题活跃人员, 提及人员时以【成员昵称】【成员账号】的形式表示: \n" + "\n".join(
                recent_messages)
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