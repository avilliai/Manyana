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
from plugins.vitsGenerate import voiceGenerate, outVits, superVG


def main(bot,master,logger):
    logger.info("语音合成用户端启动....")



    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    voicegg=result0.get("语音功能设置").get("voicegenerate")
    outSpeaker=result0.get("语音功能设置").get("speaker")


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
    fireflySpeaker=['艾米绮_JP', '爱德琳_ZH', '安守实里', '神里绫华_JP', '天目十五_JP', '迪希雅_JP', '讨嫌的小孩_ZH', '丝柯克_ZH', '沙坎_EN', '埃斯蒙德_JP', '埃斯蒙德_ZH', '博来_EN', '迪肯_ZH', '班尼特_EN', '知贵_JP', '劳伦斯_EN', '甘雨_ZH', '安托万_JP', '柴田_EN', '艾米绮_ZH', '托帕&账账_ZH', '卡西迪_ZH', '马姆杜_JP', '幻胧_EN', '安柏_ZH', '欧菲妮_EN', '十六夜野宫', '嘉良_EN', '会场广播_JP', '奇怪的云骑_ZH', '穹_JP', '忠诚的侍从_JP', '戈尔代_JP', '姬子_EN', '维多利亚_JP', '商华_JP', '嘉玛_JP', '帕梅拉_EN', '克洛琳德_JP', '才羽桃井', '恶龙_JP', '宫子（泳装）', '咲（泳装）', '杜吉耶_ZH', '村田_ZH', '嚣张的小孩_ZH', '锭前纱织', '甘雨_JP', '雷泽_ZH', '吉莲_EN', '造物翻译官_ZH', '阿拉夫_JP', '竺子_EN', '阿往_EN', '阿幸_EN', '符玄_EN', '塔杰·拉德卡尼_JP', '黄泉_EN', '科尔特_JP', '男声_EN', '河和静子', '阿斯法德_ZH', '阿尔卡米_ZH', '警长_JP', '林尼_ZH', '慧心_EN', '居勒什_ZH', '稻城萤美_JP', '巴蒂斯特_ZH', '巫女_ZH', '加拉赫_ZH', '德沃沙克_ZH', '西尔弗_JP', '小乐_EN', '贡达法_ZH', '菲约尔_ZH', '胡桃_ZH', '公主_ZH', '费迪南德_ZH', '伊织（泳装）', '黑泽京之介_ZH', '李丁_EN', '长野原龙之介_EN', '时（兔女郎）', '贾拉康_JP', '鬼婆婆_EN', '瑶瑶_ZH', '吴船长_ZH', '阿汉格尔_JP', '阿雩_EN', '黛比_JP', '查尔斯_EN', '绿芙蓉_ZH', '辛焱_JP', '伊德里西_EN', '白术_JP', '雅各_JP', '桂乃芬_ZH', '安东尼娜_ZH', '那维莱特_ZH', '沃特林_JP', '优香（体操服）', '叶卡捷琳娜_JP', '竺子_JP', '耕一_JP', '迪肯_JP', '哈伦_JP', '维多利亚_EN', '芙宁娜_JP', '星期日_ZH', '半夏_EN', '贾拉康_ZH', '一平_JP', '铁尔南_EN', '莫塞伊思_ZH', '星期日_JP', '九条裟罗_ZH', '银枝_ZH', '会场广播_EN', '艾丽_EN', '焦躁的丹鼎司医士_ZH', '琳妮特_EN', '昌虎_EN', '鹿野奈奈_JP', '徐六石_EN', '间宵时雨', '村田_EN', '加福尔_JP', '艾莉丝_EN', '库斯图_ZH', '恕筠_JP', '嘉良_JP', '昆恩_EN', '菲米尼_ZH', '卡维_ZH', '白石歌原', '布洛妮娅_EN', '丹吉尔_ZH', '杰洛尼_ZH', '丽莎_JP', '艾薇拉_ZH', '莫娜_ZH', '枫原万叶_JP', '岚姐_JP', '塞德娜_ZH', '明曦_JP', '信使_ZH', '响（应援团）', '穹_EN', '向导_ZH', '维尔芒_ZH', '浣溪_EN', '沙寅_EN', '厨子_JP', '加福尔_ZH', '香菱_EN', '科林斯_ZH', '长生_EN', '斯万_JP', '神智昏乱的云骑_EN', '薇若妮卡_EN', '拉赫曼_EN', '博士_EN', '波洛_JP', '沃特林_EN', '赛索斯_EN', '古山_EN', '有乐斋_ZH', '室笠朱音(茜)', '优菈_EN', '柊慎介_JP', '凯瑟琳_JP', '智树_EN', '奇妙的船_EN', '田铁嘴_ZH', '小乐_JP', '远黛_EN', '巴穆恩_JP', '守护者的意志_EN', '凯瑟琳_EN', '望雅_ZH', '维尔德_ZH', '露尔薇_EN', '玥辉_ZH', '拉齐_ZH', '迪肯_EN', '珊瑚宫心海_ZH', '阿山婆_ZH', '星稀_ZH', '玛吉_EN', '浮烟_JP', '大慈树王_JP', '千鸟满', '尚博迪克_JP', '纯也_EN', '福尔茨_JP', '多莉_EN', '界种科科员_JP', '古山_ZH', '基娅拉_JP', '艾丝妲_JP', '玲可_ZH', '荧_JP', '爱德琳_JP', '老孟_EN', '西瓦尼_ZH', '智树_JP', '法伊兹_JP', '莱依拉_JP', '高善_EN', '居勒什_JP', '绘星_EN', '雷电将军_EN', '刀疤刘_EN', '薇若妮卡_ZH', '莱斯格_JP', '三月七_JP', '有原则的猎犬家系成员_ZH', '申鹤_ZH', '伊迪娅_EN', '德拉萝诗_EN', '安东尼娜_JP', '加萨尼_ZH', '西瓦尼_EN', '药王秘传魁首_ZH', '可可利亚_ZH', '传次郎_EN', '守月铃美', '木南杏奈_EN', '嘉义_JP', '沙扎曼_ZH', '夏妮_JP', '托帕_ZH', '塞萨尔的日记_ZH', '罗刹_EN', '黄泉_JP', '刻薄的小孩_JP', '早柚_JP', '马洛尼_EN', '拉伊德_EN', '舒蕾_EN', '若藻（泳装）', '贝努瓦_ZH', '荒谷_ZH', '卡莉娜_JP', '塔杰·拉德卡尼_ZH', '白洲梓', '德沃沙克_JP', '埃洛伊_JP', '元太_EN', '维多克_EN', '阿汉格尔_ZH', '刃_EN', '重云_JP', '巴列维_EN', '金人会长_EN', '梅里埃_ZH', '艾尔海森_EN', '石头_ZH', '燕翠_ZH', '杜拉夫_JP', '芭芭拉_ZH', '玛达赫_EN', '露子_EN', '信使_EN', '乾玮_EN', '克列门特_ZH', '寒鸦_EN', '芹奈（圣诞）', '大和田_EN', '薇尔_EN', '波提欧_JP', '白露_EN', '香菱_JP', '伦纳德_JP', '楠楠_JP', '尾巴_ZH', '刻晴_ZH', '伦纳德_ZH', '马姆杜_ZH', '夏妮_EN', '托帕_EN', '蒂玛乌斯_EN', '消沉的患者_EN', '洛恩_JP', '今谷香里_EN', '凝光_EN', '祖莉亚·德斯特雷_JP', '佐西摩斯_EN', '诗筠_ZH', '特纳_EN', '穹_ZH', '浦和花子', '托马_EN', '花冈柚子']
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

        if m and str(event.message_chain).split("说")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = 'data/voices/' + random_str() + '.wav'
            text = await translate(text)
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

        if m and str(event.message_chain).split("中文")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = 'data/voices/' + random_str() + '.wav'

            tex = '[ZH]' + text + '[ZH]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path)
            await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
            await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def botSaid(event: GroupMessage):

        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^日文\s*(.*)\s*$', msg.strip())
        if m and str(event.message_chain).split("日文")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = 'data/voices/' + random_str() + '.wav'

            tex = '[JA]' + text + '[JA]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path)
            await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
            await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def characterSpeake(event:GroupMessage):
        if "说" in str(event.message_chain):

            text = str(event.message_chain)[len(str(event.message_chain).split("说")[0])+1:]
            if str(event.message_chain).split("说")[0] in characters:
                speaker = str(event.message_chain).split("说")[0]
                text =await translate(text)
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_文本" + text)
                logger.info("语音生成_模型:"+speaker + str(characters.get(speaker)[1]))
                data = {"text": "[JA]" + text + "[JA]", "out": path,'speaker':characters.get(speaker)[0],'modelSelect':characters.get(speaker)[1]}
                await voiceGenerate(data)
                await bot.send(event, Voice(path=path))
            if str(event.message_chain).split("说")[0] in outVitsSpeakers:
                try:
                    p = await outVits({"text": text, "speaker": str(event.message_chain).split("说")[0]})
                    await bot.send(event, Voice(path=p))
                except:
                    pass
            if str(event.message_chain).split("说")[0]+"_ZH" in fireflySpeaker:
                p = await superVG({"text": text, "speaker": str(event.message_chain).split("说")[0]+"_ZH"},"firefly")
                await bot.send(event, Voice(path=p))
            if str(event.message_chain).split("说")[0]+"_JP" in fireflySpeaker:
                p = await superVG({"text": text, "speaker": str(event.message_chain).split("说")[0]+"_JP"},"firefly")
                await bot.send(event, Voice(path=p))
            if str(event.message_chain).split("说")[0]+"_EN" in fireflySpeaker:
                p = await superVG({"text": text, "speaker": str(event.message_chain).split("说")[0]+"_EN"},"firefly")
                await bot.send(event, Voice(path=p))
            if str(event.message_chain).split("说")[0] in fireflySpeaker:
                p = await superVG(data={"text": text, "speaker": str(event.message_chain).split("说")[0]},mode="firefly",langmode="<jp>")
                await bot.send(event, Voice(path=p))


    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "中文" in str(event.message_chain) and str(event.message_chain).split("中文")[0] in characters:
            speaker = str(event.message_chain).split("中文")[0]
            text = str(event.message_chain).split("中文")[1]

            path = 'data/voices/' + random_str() + '.wav'
            logger.info("语音生成_文本" + text)
            logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
            data = {"text": "[ZH]" + text + "[ZH]", "out": path, 'speaker': characters.get(speaker)[0],
                    'modelSelect': characters.get(speaker)[1]}
            await voiceGenerate(data)
            await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "日文" in str(event.message_chain) and str(event.message_chain).split("日文")[0] in characters:
            speaker = str(event.message_chain).split("日文")[0]
            text = str(event.message_chain).split("日文")[1]

            logger.info("语音生成_文本"+text)
            path = 'data/voices/' + random_str() + '.wav'
            logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
            data = {"text": "[JA]" + text + "[JA]", "out": path, 'speaker': characters.get(speaker)[0],
                    'modelSelect': characters.get(speaker)[1]}
            await voiceGenerate(data)
            await bot.send(event, Voice(path=path))
    @bot.on(GroupMessage)
    async def checkCharacters(event:GroupMessage):
        if "角色" in str(event.message_chain) and At(bot.qq) in event.message_chain and "模板" not in str(event.message_chain):

            '''str1="vits可用角色如下：\n"
            for i in characters:
                str1+=i+" |"
            str1+="\n\nfirefly可用角色如下:\n"+str(fireflySpeaker).replace("_JP","").replace("_EN","").replace("_ZH","")+"\n\nbert_vits2可用角色如下：\n"+str(["BT","塔菲","阿梓","otto","丁真","星瞳","东雪莲","嘉然","孙笑川","亚托克斯","文静","鹿鸣","奶绿","七海","恬豆","科比"])+"\n\noutVits语音合成可用角色如下：\n"+str(outVitsSpeakers)
            await bot.send(event, str1)'''
            await bot.send(event,Image(path="data/fonts/fireflyspeakers.jpg"))
            await bot.send(event,"可发送 xx说.......  以进行语音合成")



