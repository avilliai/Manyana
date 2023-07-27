# -*- coding: utf-8 -*-
import json
import random

import poe
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
def gptHelper():
    client = poe.Client("", proxy="http://127.0.0.1:1080")
    json.dumps(client.bot_names, indent=2)
    while True:
        message = input("you:")
        s=""
        for chunk in client.send_message("capybara", message):
            #print(chunk["text_new"],end="", flush=True)
            s+=chunk["text_new"]
        print(s)

"""
{
  "capybara": "Sage",
  "a2": "Claude-instant",
  "nutria": "Dragonfly",
  "a2_100k": "Claude-instant-100k",
  "beaver": "GPT-4",
  "chinchilla": "ChatGPT",
  "a2_2": "Claude+"
}
"""





def main(bot,master,apikey,proxy,logger):
    logger.info("正在启动poe-AI")
    global apiKey
    apiKey=apikey
    global KEY
    KEY=apiKey[0]
    logger.info("选择key:"+KEY)
    global client
    client = poe.Client(KEY, proxy=proxy)
    json.dumps(client.bot_names, indent=2)

    @bot.on(GroupMessage)
    async def AiHelper(event:GroupMessage):
        global client
        global KEY
        if str(event.message_chain).startswith("/poe"):
            mes=str(event.message_chain).replace("/poe","")
            s = ""
            logger.info("poe接收消息："+mes)
            try:
                for chunk in client.send_message("capybara", mes):
                    # print(chunk["text_new"],end="", flush=True)
                    s += chunk["text_new"]
                logger.info("bot:"+s)
                await bot.send(event,s)
            except:
                logger.warning("出错，达到每分钟限制或token已失效。")
                apiKey.remove(KEY)
                if len(apiKey)==0:
                    await bot.send(event,"令牌已全部失效，请联系master重新获取")
                    return
                logger.warning("执行poe-api 重载指令")
                await bot.send(event,"出错，达到每分钟限制或token已失效。")
                try:
                    KEY=random.choice(apiKey)
                    client = poe.Client(token=KEY, proxy=proxy)
                    json.dumps(client.bot_names, indent=2)
                    logger.info("poe-api重载完成")
                    await bot.send(event,"poe重启完成")
                except:
                    logger.error("poe-api重载失败，请检查代理或更新token")
        if str(event.message_chain)=="/clear" and str(event.sender.id)==str(master):
            client.send_chat_break("capybara")
            await bot.send(event,"已清除对话上下文。")
        if str(event.message_chain)=="/reload" and str(event.sender.id)==str(master):
            client = poe.Client(token=random.choice(apiKey), proxy=proxy)
            json.dumps(client.bot_names, indent=2)
            await bot.send(event,"已重启")
if __name__ == '__main__':
    gptHelper()