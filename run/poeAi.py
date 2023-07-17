# -*- coding: utf-8 -*-
import json

import poe
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
'''def gptHelper():
    client = poe.Client("BHai3yLdvOcKajS6UnIX6A%3D%3D", proxy="http://127.0.0.1:1080")
    json.dumps(client.bot_names, indent=2)
    while True:
        message = input("you:")
        s=""
        for chunk in client.send_message("capybara", message):
            #print(chunk["text_new"],end="", flush=True)
            s+=chunk["text_new"]
        print(s)'''

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





def main(bot,master,KEY,proxy):
    global client
    client = poe.Client(KEY, proxy=proxy)
    json.dumps(client.bot_names, indent=2)

    @bot.on(GroupMessage)
    async def AiHelper(event:GroupMessage):
        global client
        if str(event.message_chain).startswith("/poe"):
            mes=str(event.message_chain)[4:]
            s = ""
            try:
                for chunk in client.send_message("capybara", mes):
                    # print(chunk["text_new"],end="", flush=True)
                    s += chunk["text_new"]
                print("bot:"+s)
                await bot.send(event,s)
            except:
                await bot.send(event,"出错，达到每分钟限制或token已失效。")
        if str(event.message_chain)=="/clear" and str(event.sender.id)==str(master):
            client.send_chat_break("capybara")
            await bot.send(event,"已清除对话上下文。")
        if str(event.message_chain)=="/reload" and str(event.sender.id)==str(master):
            client = poe.Client(token=KEY, proxy=proxy)
            json.dumps(client.bot_names, indent=2)
            await bot.send(event,"已重启")
#if __name__ == '__main__':
    #gptHelper()