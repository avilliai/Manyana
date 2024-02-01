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
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, outVits


def main(bot,master,app_id,app_key,logger):
    logger.info("语音合成用户端启动....")



    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    voicegg=result0.get("voicegenerate")
    outSpeaker=result0.get("chatGLM").get("speaker")
    if voicegg=="vits":

        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
            result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
        global modelSelect
        global speaker
        speaker = result2.get("defaultModel").get("speaker")
        modelSelect = result2.get("defaultModel").get("modelSelect")

        global models
        global characters
        models, default, characters = modelLoader()  # 读取模型
    outVitsSpeakers="空, 荧, 派蒙, 纳西妲, 阿贝多, 温迪, 枫原万叶, 钟离, 荒泷一斗, 八重神子, 艾尔海森, 提纳里, 迪希雅, 卡维, 宵宫, 莱依拉, 赛诺, 诺艾尔, 托马, 凝光, 莫娜, 北斗, 神里绫华, 雷电将军, 芭芭拉, 鹿野院平藏, 五郎, 迪奥娜, 凯亚, 安柏, 班尼特, 琴, 柯莱, 夜兰, 妮露, 辛焱, 珐露珊, 魈, 香菱, 达达利亚, 砂糖, 早柚, 云堇, 刻晴, 丽莎, 迪卢克, 烟绯, 重云, 珊瑚宫心海, 胡桃, 可莉, 流浪者, 久岐忍, 神里绫人, 甘雨, 戴因斯雷布, 优菈, 菲谢尔, 行秋, 白术, 九条裟罗, 雷泽, 申鹤, 迪娜泽黛, 凯瑟琳, 多莉, 坎蒂丝, 萍姥姥, 罗莎莉亚, 留云借风真君, 绮良良, 瑶瑶, 七七, 奥兹, 米卡, 夏洛蒂, 埃洛伊, 博士, 女士, 大慈树王, 三月七, 娜塔莎, 希露瓦, 虎克, 克拉拉, 丹恒, 希儿, 布洛妮娅, 瓦尔特, 杰帕德, 佩拉, 姬子, 艾丝妲, 白露, 星, 穹, 桑博, 伦纳德, 停云, 罗刹, 卡芙卡, 彦卿, 史瓦罗, 螺丝咕姆, 阿兰, 银狼, 素裳, 丹枢, 黑塔, 景元, 帕姆, 可可利亚, 半夏, 符玄, 公输师傅, 奥列格, 青雀, 大毫, 青镞, 费斯曼, 绿芙蓉, 镜流, 信使, 丽塔, 失落迷迭, 缭乱星棘, 伊甸, 伏特加女孩, 狂热蓝调, 莉莉娅, 萝莎莉娅, 八重樱, 八重霞, 卡莲, 第六夜想曲, 卡萝尔, 姬子, 极地战刃, 布洛妮娅, 次生银翼, 理之律者, 真理之律者, 迷城骇兔, 希儿, 魇夜星渊, 黑希儿, 帕朵菲莉丝, 天元骑英, 幽兰黛尔, 德丽莎, 月下初拥, 朔夜观星, 暮光骑士, 明日香, 李素裳, 格蕾修, 梅比乌斯, 渡鸦, 人之律者, 爱莉希雅, 爱衣, 天穹游侠, 琪亚娜, 空之律者, 终焉之律者, 薪炎之律者, 云墨丹心, 符华, 识之律者, 维尔薇, 始源之律者, 芽衣, 雷之律者, 苏莎娜, 阿波尼亚, 陆景和, 莫弈, 夏彦, 左然".replace(" ","").split(",")
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


    # modelSelect=['voiceModel/selina/selina.pth','voiceModel/selina/config.json']
    # print('------\n'+str(CHOISE))
    @bot.on(GroupMessage)
    async def botSaid(event:GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^说\s*(.*)\s*$', msg.strip())
        if voicegg=="vits":
            if m and str(event.message_chain).split("说")[0] not in characters and At(bot.qq) in event.message_chain:
                # 取出指令中的地名
                text = m.group(1)
                path = 'data/voices/' + random_str() + '.wav'
                text = await translate(text, app_id, app_key)
                tex = '[JA]' + text + '[JA]'
                logger.info("启动文本转语音：text: " + tex + " path: " + path)
                await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
                await bot.send(event, Voice(path=path))
        elif voicegg=="outVits":
            if m and str(event.message_chain).split("说")[0] not in outVitsSpeakers and At(bot.qq) in event.message_chain:
                text = m.group(1)
                p=await outVits({"text": text, "speaker": outSpeaker})
                await bot.send(event, Voice(path=p))

    @bot.on(GroupMessage)
    async def botSaid(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^中文\s*(.*)\s*$', msg.strip())
        if voicegg=="vits":
            if m and str(event.message_chain).split("中文")[0] not in characters and At(bot.qq) in event.message_chain:
                # 取出指令中的地名
                text = m.group(1)
                path = 'data/voices/' + random_str() + '.wav'
                #text = await translate(text, app_id, app_key)
                tex = '[ZH]' + text + '[ZH]'
                logger.info("启动文本转语音：text: " + tex + " path: " + path)
                await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
                await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def botSaid(event: GroupMessage):
        if voicegg=="vits":
            msg = "".join(map(str, event.message_chain[Plain]))
            # 匹配指令
            m = re.match(r'^日文\s*(.*)\s*$', msg.strip())
            if m and str(event.message_chain).split("日文")[0] not in characters and At(bot.qq) in event.message_chain:
                # 取出指令中的地名
                text = m.group(1)
                path = 'data/voices/' + random_str() + '.wav'
                # text = await translate(text, app_id, app_key)
                tex = '[JA]' + text + '[JA]'
                logger.info("启动文本转语音：text: " + tex + " path: " + path)
                await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
                await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def characterSpeake(event:GroupMessage):
        if "说" in str(event.message_chain):

            text = str(event.message_chain)[len(str(event.message_chain).split("说")[0])+1:]
            if voicegg=="vits" and str(event.message_chain).split("说")[0] in characters:
                speaker = str(event.message_chain).split("说")[0]
                text =await translate(text, app_id, app_key)
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_文本" + text)
                logger.info("语音生成_模型:"+speaker + str(characters.get(speaker)[1]))
                data = {"text": "[JA]" + text + "[JA]", "out": path,'speaker':characters.get(speaker)[0],'modelSelect':characters.get(speaker)[1]}
                await voiceGenerate(data)
                await bot.send(event, Voice(path=path))
            elif voicegg=="outVits" and str(event.message_chain).split("说")[0] in outVitsSpeakers:
                p = await outVits({"text": text, "speaker": str(event.message_chain).split("说")[0]})
                await bot.send(event, Voice(path=p))

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if voicegg=="vits":
            if "中文" in str(event.message_chain) and str(event.message_chain).split("中文")[0] in characters:
                speaker = str(event.message_chain).split("中文")[0]
                text = str(event.message_chain).split("中文")[1]
                #text = translate(text, app_id, app_key)不用翻译
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_文本" + text)
                logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
                data = {"text": "[ZH]" + text + "[ZH]", "out": path, 'speaker': characters.get(speaker)[0],
                        'modelSelect': characters.get(speaker)[1]}
                await voiceGenerate(data)
                await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if voicegg=="vits":
            if "日文" in str(event.message_chain) and str(event.message_chain).split("日文")[0] in characters:
                speaker = str(event.message_chain).split("日文")[0]
                text = str(event.message_chain).split("日文")[1]
                # text = translate(text, app_id, app_key)不用翻译
                logger.info("语音生成_文本"+text)
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
                data = {"text": "[JA]" + text + "[JA]", "out": path, 'speaker': characters.get(speaker)[0],
                        'modelSelect': characters.get(speaker)[1]}
                await voiceGenerate(data)
                await bot.send(event, Voice(path=path))
    @bot.on(GroupMessage)
    async def checkCharacters(event:GroupMessage):
        if "角色" in str(event.message_chain) and At(bot.qq) in event.message_chain:
            if voicegg=="vits":
                str1=""
                for i in characters:
                    str1+=i+" |"
                await bot.send(event,"可用角色如下：\n"+str1)
            elif voicegg=="outVits":
                await bot.send(event, "可用角色如下：\n" + str(outVitsSpeakers))
                await bot.send(event,"可发送 xx说....... 以进行语音合成")



