# -*- coding: utf-8 -*-
import json
import random
import uuid

import poe
import yaml
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.PandoraChatGPT import ask_chatgpt
from plugins.rwkvHelper import rwkvHelper



def main(bot,master,apikey,proxy,logger):
    try:
        logger.info("正在启动poe-AI")
        global apiKey
        apiKey=apikey
        global KEY
        KEY=apiKey[0]
        logger.info("选择key:"+KEY)
        global client
        client = poe.Client(KEY, proxy=proxy)
        json.dumps(client.bot_names, indent=2)
    except:
        logger.error("poeAi启动失败，请检查代理或重试")
    logger.info("正在启动rwkv对话模型")
    try:
        logger.info("rwkv接收信息：" + "测试消息")
        s = await rwkvHelper("你好")
    except:
        logger.error("rwkv对话模型启动失败，未找到对应的本地服务")
    logger.info("正在启动pandora_ChatGPT")
    try:
        parent_message_id = None
        prompt = "我爱你啊！！！！！！！！！"

        # 向ChatGPT提问，等待其回复
        model = "text-davinci-002-render-sha"  # 选择一个可用的模型Default (GPT-3.5)：text-davinci-002-render-sha
        message_id = str(uuid.uuid4())  # 随机生成一个消息ID
        if parent_message_id is None:
            parent_message_id = "f0bf0ebe-1cd6-4067-9264-8a40af76d00e"
        conversation_id = None
        # conversation_id = None
        parent_message_id,conversation_id = ask_chatgpt(prompt, model, message_id, parent_message_id, conversation_id)
        print("当前会话的id:", parent_message_id)
    except:
        logger.error("未找到可用的pandora服务")
    global pandoraData
    with open('data/pandora_ChatGPT.yaml', 'r', encoding='utf-8') as file:
        pandoraData = yaml.load(file, Loader=yaml.FullLoader)

    @bot.on(GroupMessage)
    async def pandoraSever(event:GroupMessage):
        global pandoraData
        if str(event.message_chain).startswith("/p"):
            prompt=str(event.message_chain)[2:]
            message_id = str(uuid.uuid4())
            model = "text-davinci-002-render-sha"
            if event.group.id in pandoraData.keys():
                conversation_id=pandoraData.get(event.group.id).get("conversation_id")
                parent_message_id=pandoraData.get(event.group.id).get("parent_message_id")
            else:
                conversation_id=None
                parent_message_id="f0bf0ebe-1cd6-4067-9264-8a40af76d00e"
            parent_message_id, conversation_id = ask_chatgpt(prompt, model, message_id, parent_message_id,
                                                             conversation_id)
            pandoraData[event.group.id]={"parent_message_id":parent_message_id, "conversation_id":conversation_id}
            with open('data/pandora_ChatGPT.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(pandoraData, file, allow_unicode=True)



    @bot.on(GroupMessage)
    async def rwkv(event:GroupMessage):
        if str(event.message_chain).startswith("/rwkv"):
            s=str(event.message_chain).replace("/rwkv","")
            try:
                logger.info("rwkv接收信息："+s)
                s=await rwkvHelper(s)
                logger.info("rwkv:"+s)
                await bot.send(event,s)
            except:
                logger.error("调用rwkv失败，请检查本地rwkv是否启动或端口是否配置正确(8000)")
                await bot.send(event,"无法连接到本地rwkv")

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

                if len(apiKey)==0:
                    await bot.send(event,"令牌已全部失效，请联系master重新获取")
                    return
                else:
                    logger.error("移出token:" + KEY)
                    try:

                        apiKey.remove(KEY)
                        if len(apiKey) == 0:
                            apiKey.append(KEY)
                    except:
                        logger.error("移出token失败")
                    logger.info("当前token:"+str(apiKey))
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