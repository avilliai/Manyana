# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import re
import time
import sys

import httpx
import requests
import utils
import yaml
import zhipuai
from mirai import Image, Voice, Poke
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import NudgeEvent

from concurrent.futures import ThreadPoolExecutor
from plugins.RandomStr import random_str
from plugins.chatGLMonline import glm4
from plugins.gptOfficial import gptOfficial,kimi, qingyan, lingyi, stepAI, qwen, gptvvvv
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, taffySayTest, sovits, edgetts, outVits, modelscopeTTS, superVG
from plugins.yubanGPT import lolimigpt, lolimigpt2
from plugins.googleGemini import geminirep

def main(bot,master,logger,berturl,proxy):
    with open('config.json', 'r', encoding='utf-8') as f:
        datas = yaml.load(f.read(), Loader=yaml.FullLoader)
    configs = datas
    botName = configs.get("botName")
    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    normal_Reply = result.get("nudgedReply")
    special_Reply = result.get("BeatNudge")
    special_Reply1 = result.get("BeatNudge1")
    voiceReply = result.get("voiceReply")
    chineseVoiceRate=result.get("chineseVoiceRate")
    bert_vits2_mode=result.get("bert_vits2_mode")
    global transLateData
    with open('data/autoReply/transLateData.yaml', 'r', encoding='utf-8') as file:
        transLateData = yaml.load(file, Loader=yaml.FullLoader)

    prob=result.get("prob")
    withText=result.get("withText")
    logger.info("读取到apiKey列表")

    global models
    global characters
    models, default, characters = modelLoader()  # 读取模型
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    speaker92 = result0.get("chatGLM").get("speaker")
    voiceLangType = str(result0.get("chatGLM").get("voiceLangType"))
    voicegg=result0.get("voicegenerate")
    chatmodel=result0.get("chatGLM").get("model")
    nudgeornot=result0.get("chatGLM").get("nudgeReply")
    meta1 = result0.get("chatGLM").get("bot_info").get("default")
    gpt3=result0.get("chatGLM").get("bot_info").get("gpt3.5")
    lolimig = result0.get("chatGLM").get("bot_info").get("lolimigpt")
    glm_4=result0.get("chatGLM").get("bot_info").get("glm-4")
    allcharacters = result0.get("chatGLM").get("bot_info")
    Gem=result0.get("chatGLM").get("bot_info").get("Gemini")
    logger.info("语音合成模式："+voicegg+" 语音合成speaker："+speaker92)
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    chatGLM_api_key = resulttr.get("chatGLM")
    geminiapikey=resulttr.get("gemini")
    gptkeys=resulttr.get("openai-keys")
    proxy=resulttr.get("proxy")
    os.environ["http_proxy"] = proxy
    if voicegg=="vits":
        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
            result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
        global modelSelect
        global speaker
        speaker = result2.get("defaultModel").get("speaker")
        modelSelect = result2.get("defaultModel").get("modelSelect")
    @bot.on(GroupMessage)
    async def setDefaultModel(event: GroupMessage):
        if event.sender.id == master and str(event.message_chain).startswith("设定角色#"):
            global speaker
            global modelSelect
            if str(event.message_chain).split("#")[1] in characters:
                speaker1 = str(event.message_chain).split("#")[1]
                logger.info("尝试设定角色：" + speaker1)
                speaker = int(characters.get(speaker1)[0])
                modelSelect = characters.get(speaker1)[1]
                logger.info("设置了语音生成_speaker" + str(speaker))
                logger.info("设置了语音生成_模型:" + str(modelSelect))
                with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                    result = yaml.load(f.read(), Loader=yaml.FullLoader)
                defaultModel = result.get("defaultModel")
                defaultModel["speaker"] = speaker
                defaultModel["modelSelect"] = modelSelect
                result["defaultModel"] = defaultModel
                with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(result, file, allow_unicode=True)

                await bot.send(event, "成功设置了vits语音生成默认角色为：" + speaker1)
            else:
                await bot.send(event, "不存在的vits角色")

    @bot.on(NudgeEvent)
    async def NudgeReply(event:NudgeEvent):
        global transLateData
        if event.target==bot.qq:
            logger.info("接收到来自" + str(event.from_id) + "的戳一戳")
            if random.randint(0,100)>100-prob:
                await bot.send_group_message(event.subject.id, random.choice(special_Reply))
                try:
                    await bot.send_nudge(target=event.from_id,subject=event.subject.id,kind='Group')
                    await bot.send_group_message(event.subject.id, random.choice(special_Reply1))
                except:
                    try:
                        await bot.send_group_message(event.subject.id,Poke(name="ChuoYiChuo"))
                        await bot.send_group_message(event.subject.id, random.choice(special_Reply1))
                    except:
                        await bot.send_group_message(event.subject.id,"唔....似乎戳不了你呢....好可惜")
            else:
                bot_in = str("你是" + botName + ",我是" + event.sender.member_name + "," + allcharacters.get(
                    chatmodel)).replace("【bot】",
                                        botName).replace("【用户】", event.sender.member_name)
                prompt1 = [
                    {
                        "role": "user",
                        "content": random.choice(["戳你一下", "摸摸头", "戳戳你的头", "摸摸~"])
                    }
                ]
                loop = asyncio.get_event_loop()
                if nudgeornot==False:
                    rep = random.choice(normal_Reply)
                elif chatmodel=="lolimigpt":

                    rep=await lolimigpt2([{"role":"user","content":random.choice(["戳你一下","摸摸头","戳戳你的头"])}],str("你是"+meta1.get("bot_name")+","+lolimig.replace("【bot】",meta1.get("bot_name")).replace("【用户】","主人")))
                    rep = rep.get("content")
                elif chatmodel=="gpt3.5":
                    bot_in=str(gpt3.replace("【bot】",meta1.get("bot_name")).replace("【用户】","主人"))
                    rep = await loop.run_in_executor(None, gptOfficial, prompt1, gptkeys, proxy, bot_in)
                    rep=rep.get("content")
                elif chatmodel=="glm-4":
                    bot_in=str(glm_4.replace("【bot】",meta1.get("bot_name")).replace("【用户】","主人"))


                    rep = await glm4(prompt1,bot_in)
                    rep=rep.get("content")
                elif chatmodel == "kimi":
                    rep = await loop.run_in_executor(None, kimi, prompt1, bot_in)
                elif chatmodel == "清言":
                    rep = await loop.run_in_executor(None, qingyan, prompt1, bot_in)
                elif chatmodel == "lingyi":
                    rep = await loop.run_in_executor(None, lingyi, prompt1, bot_in)
                elif chatmodel == "step":
                    rep = await loop.run_in_executor(None, stepAI, prompt1, bot_in)
                elif chatmodel == "通义千问":
                    rep = await loop.run_in_executor(None, qwen, prompt1, bot_in)
                elif chatmodel == "gptX":
                    rep = await loop.run_in_executor(None, gptvvvv, prompt1, bot_in)
                elif chatmodel=="Gemini":
                    bot_in=str(Gem.replace("【bot】",meta1.get("bot_name")).replace("【用户】","主人"))
                    tep = {"role": "user","parts": [random.choice(["戳你一下", "摸摸头~"])]}
                    prompt=[{"role": "user", "parts": [bot_in]},{"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]}]
                    prompt.append(tep)
                    rep =await geminirep(ak=random.choice(geminiapikey), messages=prompt)
                else:
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(chatGLM1)
                        print()
                    rep=str(future.result())
                    #rep=chatGLM1(chatGLM_api_key,meta1,"戳你一下")
                logger.info("回复：" + str(rep))
                if random.randint(1, 100) > voiceReply:
                    await bot.send_group_message(event.subject.id, rep)
                else:
                    daf={}
                    daf["speaker"]=speaker92
                    st8 = re.sub(r"（[^）]*）", "", rep)
                    daf["text"]=st8

                    # print(path)
                      # 使用r前缀表示原始字符串，避免转义字符的问题
                    try:

                        if voicegg != "vits":
                            logger.info(f"调用{voicegg}语音回复")
                            try:
                                path = await superVG({"text": st8, "speaker": speaker92},voicegg,berturl,voiceLangType)
                                await bot.send_group_message(event.subject.id, Voice(path=path))
                            except:
                                logger.error(f"{voicegg}语音合成服务已关闭，请重新运行")
                                await bot.send_group_message(event.subject.id, rep)
                                return
                        elif voicegg=="vits":
                            path = 'data/voices/' + random_str() + '.wav'
                            if len(rep) > 80:
                                await bot.send_group_message(event.subject.id, rep)
                                return
                            if random.randint(1, 100) > chineseVoiceRate:
                                if rep in transLateData:
                                    text = transLateData.get(rep)
                                else:
                                    text = await translate(str(rep))
                                    transLateData[rep] = text


                                    with open('data/autoReply/transLateData.yaml', 'w', encoding="utf-8") as file:
                                        yaml.dump(transLateData, file, allow_unicode=True)
                                    logger.info("写入参照数据:" + rep + "| " + text)
                                tex = '[JA]' + text + '[JA]'
                            else:
                                tex = "[ZH]" + rep + "[ZH]"
                            logger.info("启动文本转语音：text: " + tex + " path: " + path)
                            await voiceGenerate(
                                {"text": tex, "out": path, "speaker": speaker, "modelSelect": modelSelect})
                            await bot.send_group_message(event.subject.id, Voice(path=path))
                            if withText == True:
                                await bot.send_group_message(event.subject.id, rep)
                                return
                    except Exception as e:
                        logger.error(e)
                        logger.error("出错，发送原文本")
                        await bot.send_group_message(event.subject.id, rep)
                        path = 'data/voices/' + random_str() + '.wav'
                        if len(rep) > 80:
                            await bot.send_group_message(event.subject.id, rep)
                            return
                        if random.randint(1, 100) > chineseVoiceRate:
                            if rep in transLateData:
                                text = transLateData.get(rep)
                            else:
                                text = await translate(str(rep))
                                transLateData[rep] = text
                                with open('data/autoReply/transLateData.yaml', 'w', encoding="utf-8") as file:
                                    yaml.dump(transLateData, file, allow_unicode=True)
                                logger.info("写入参照数据:" + rep + "| " + text)
                            tex = '[JA]' + text + '[JA]'
                        else:
                            tex = "[ZH]" + rep + "[ZH]"
                        logger.info("启动文本转语音：text: " + tex + " path: " + path)
                        await voiceGenerate(
                            {"text": tex, "out": path, "speaker": speaker, "modelSelect": modelSelect})
                        await bot.send_group_message(event.subject.id, Voice(path=path))
                        if withText == True:
                            await bot.send_group_message(event.subject.id, rep)
                            #await bot.send_group_message(event.subject.id,  rep)'''
    def chatGLM1():
        prompt = [
            {
                "role": "user",
                "content": random.choice(["戳你一下","摸摸头","戳戳你的头"])
            }
        ]
        zhipuai.api_key = chatGLM_api_key
        response = zhipuai.model_api.sse_invoke(
            model="characterglm",
            meta= meta1,
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




