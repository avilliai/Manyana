# -*- coding: utf-8 -*-
import re

import yaml
from mirai import GroupMessage, At, Plain,MessageChain
from mirai import Voice
from mirai.models import ForwardMessageNode, Forward
from plugins.RandomStr import random_str
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, superVG, fetch_FishTTS_ModelId, sovits, taffySayTest


def main(bot, master, logger):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    FishTTSAuthorization = result0.get("FishTTSAuthorization")
    berturl = result0.get("bert_colab")
    proxy = result0.get("proxy")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    spe = result.get("语音功能设置").get("bert_speakers")
    prefix=result.get("语音功能设置").get("prefix")
    modelScope = ["BT", "塔菲", "阿梓", "otto", "丁真", "星瞳", "东雪莲", "嘉然", "孙笑川", "亚托克斯", "文静", "鹿鸣",
                  "奶绿", "七海", "恬豆", "科比"]
    outVitsSpeakers="派蒙, 纳西妲, 娜维娅, 荒泷一斗, 凯亚, 林尼, 温迪, 阿贝多, 芙宁娜, 钟离, 赛诺, 那维莱特, 提纳里, 枫原万叶, 艾尔海森, 八重神子, 宵宫, 卡维, 迪希雅, 莱依拉, 诺艾尔, 托马, 莫娜, 凝光, 神里绫华, 北斗, 莱欧斯利, 柯莱, 迪奥娜, 可莉, 丽莎, 琳妮特, 五郎, 雷电将军, 芭芭拉, 珊瑚宫心海, 鹿野院平藏, 魈, 达达利亚, 琴, 胡桃, 砂糖, 安柏, 重云, 夜兰, 班尼特, 珐露珊, 妮露, 辛焱, 香菱, 迪卢克, 刻晴, 烟绯, 久岐忍, 早柚, 云堇, 夏洛蒂, 夏沃蕾, 优菈, 克洛琳德, 神里绫人, 甘雨, 流浪者, 行秋, 千织, 戴因斯雷布, 希格雯, 阿蕾奇诺, 闲云, 白术, 菲谢尔, 荧, 空, 申鹤, 九条裟罗, 菲米尼, 雷泽, 嘉明, 多莉, 凯瑟琳, 迪娜泽黛, 绮良良, 坎蒂丝, 罗莎莉亚, 米卡, 萍姥姥, 赛索斯, 留云借风真君, 埃德, 爱贝尔, 瑶瑶, 伊迪娅, 七七, 式大将, 奥兹, 德沃沙克, 泽维尔, 哲平, 大肉丸, 浮游水蕈兽·元素生命, 蒂玛乌斯, 塞琉斯, 欧菲妮, 昆钧, 主持人, 言笑, 迈勒斯, 杜拉夫, 拉赫曼, 旁白, 伊利亚斯, 爱德琳, 居勒什, 埃洛伊, 远黛, 弗洛莱恩, 柊千里, 塞塔蕾, 海芭夏, 回声海螺, 阿扎尔, 博士, 天叔, 祖莉亚·德斯特雷, 三月七, 瓦尔特, 丹恒, 砂金, 希儿, 姬子, 流萤, 穹, 星, 希露瓦, 娜塔莎, 黄泉, 黑天鹅, 佩拉, 布洛妮娅, 虎克, 素裳, 克拉拉, 符玄, 白露, 景元, 杰帕德, 藿藿, 星期日, 桑博, 卡芙卡, 艾丝妲, 托帕, 真理医生, 桂乃芬, 加拉赫, 米沙, 知更鸟, 彦卿, 玲可, 波提欧, 黑塔, 驭空, 停云, 镜流, 银枝, 银狼, 卢卡, 帕姆, 罗刹, 阮•梅, 翡翠, 青雀, 阿兰, 浮烟, 螺丝咕姆, 花火, 史瓦罗, 明曦, 寒鸦, 雪衣, 乔瓦尼, 伦纳德, 公输师傅, 晴霓, 奥列格, 丹枢, 刃, 尾巴, 可可利亚, 青镞, 半夏, 梦主".replace(" ","").split(",")
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global modelSelect
    global speaker
    speaker = result2.get("defaultModel").get("speaker")
    modelSelect = result2.get("defaultModel").get("modelSelect")

    global models
    global characters
    try:
        from plugins.modelsLoader import modelLoader
        models, default, characters = modelLoader()  # 读取模型
    except Exception as e:
        characters = {"None": "无可用模型"}

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
    async def characterSpeake(event: GroupMessage):
        if "说" in str(event.message_chain) and str(event.message_chain).startswith(prefix):

            text = str(event.message_chain)[len(str(event.message_chain).split("说")[0]) + 1:]
            speaker = str(event.message_chain).split("说")[0].replace(prefix,"")
            if speaker in characters:
                    text = await translate(text)
                    path = 'data/voices/' + random_str() + '.wav'
                    logger.info("语音生成_文本" + text)
                    logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
                    data = {"text": "[JA]" + text + "[JA]", "out": path, 'speaker': characters.get(speaker)[0],
                            'modelSelect': characters.get(speaker)[1]}
                    await voiceGenerate(data)
                    await bot.send(event, Voice(path=path))
                    return
            if speaker in modelScope:
                try:
                    data = {"speaker": speaker,
                            "text": text}
                    logger.info("modelscopeTTS语音合成:" + data["text"])
                    path = await superVG(data, "modelscopeTTS")
                    await bot.send(event, Voice(path=path))
                    return
                except Exception as e:
                    logger.error(e)
                    #await bot.send(event, "出错了喵，呜呜呜", True)
            if speaker in outVitsSpeakers:
                try:
                    data = {"speaker": speaker,
                            "text": text}
                    logger.info("outVits语音合成:" + data["text"])
                    path = await superVG(data, "outVits")
                    await bot.send(event, Voice(path=path))
                    return
                except Exception as e:
                    logger.error(e)
                    await bot.send(event, "出错了喵，呜呜呜", True)
            try:
                sp1 = await fetch_FishTTS_ModelId(proxy, FishTTSAuthorization, speaker)
                if sp1 is None or sp1 == "":
                    logger.warning("未能在FishTTS中找到对应角色")
                    return
                else:
                    logger.info(f"获取到FishTTS模型id {speaker} {sp1}")
                    p = await superVG({"text": text, "speaker": sp1}, "FishTTS")
                    await bot.send(event, Voice(path=p))
            except Exception as e:
                logger.error(e)

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "中文" in str(event.message_chain) and str(event.message_chain).split("中文")[0].replace(prefix,"") in characters and str(event.message_chain).startswith(prefix):
            speaker = str(event.message_chain).split("中文")[0].replace(prefix,"")
            text = str(event.message_chain).split("中文")[1]

            path = f'data/voices/{random_str()}.wav'
            logger.info("语音生成_文本" + text)
            logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
            data = {"text": "[ZH]" + text + "[ZH]", "out": path, 'speaker': characters.get(speaker)[0],
                    'modelSelect': characters.get(speaker)[1]}
            await voiceGenerate(data)
            await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "日文" in str(event.message_chain) and str(event.message_chain).startswith(prefix):
            speaker = str(event.message_chain).split("日文")[0].replace(prefix,"")
            text = str(event.message_chain)[len(str(event.message_chain).split("日文")[0]) + 1:]

            logger.info("语音生成_文本" + text)
            if speaker in characters:
                path = f'data/voices/{random_str()}.wav'
                logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
                data = {"text": f"[JA]{text}[JA]", "out": path, 'speaker': speaker,
                        'modelSelect': characters.get(speaker)[1]}
                await voiceGenerate(data)
                await bot.send(event, Voice(path=path))

            try:
                sp1 = await fetch_FishTTS_ModelId(proxy, FishTTSAuthorization,speaker)
                if sp1 is None or sp1 == "":
                    logger.warning("未能在FishTTS中找到对应角色")
                    return
                else:
                    logger.info(f"获取到FishTTS模型id {speaker} {sp1}")
                    p = await superVG(data={"text": text, "speaker": sp1}, mode="FishTTS", langmode="<jp>")
                    await bot.send(event, Voice(path=p))
            except Exception as e:
                logger.error(e)

    @bot.on(GroupMessage)
    async def checkCharacters(event: GroupMessage):
        if "角色" in str(event.message_chain) and At(bot.qq) in event.message_chain and "模板" not in str(
                event.message_chain) and len(str(event.message_chain).replace(str(At(bot.qq))))<6:
            #print(len(str(event.message_chain).replace(str(At(bot.qq)))))
            try:
                str1 = "vits可用角色如下：\n"
                for i in characters:
                    str1 += i + " |"
            except:
                str1 = ""
            b1=[]
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                    message_chain=MessageChain(str1)))
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                         message_chain=MessageChain("bert_vits2可用角色如下：\n" + str(["BT", "塔菲", "阿梓", "otto", "丁真", "星瞳", "东雪莲", "嘉然", "孙笑川", "亚托克斯", "文静", "鹿鸣","奶绿", "七海", "恬豆", "科比"]))))
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                         message_chain=MessageChain("\n\nFishTTS可用角色请查看https://fish.audio/zh-CN/，均可通过 xx说调用。\n")))
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                         message_chain=MessageChain(f"outVits可用角色如下：\n{outVitsSpeakers}")))
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                         message_chain=MessageChain("可发送 xx说.......  以进行语音合成")))
            await bot.send(event, Forward(node_list=b1))

    @bot.on(GroupMessage)
    async def sovitsHelper(event: GroupMessage):
        if str(event.message_chain).startswith("/sovits"):
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            speaker1 = result.get("chatGLM").get("speaker")
            bsf = str(event.message_chain).replace("/sovits", "")
            logger.info("sovits文本推理任务：" + bsf)
            r = await sovits({"text": bsf, "speaker": speaker1})
            logger.info("tts 完成")
            await bot.send(event, Voice(path=r))

    '''@bot.on(GroupMessage)
    async def edgettsHelper(event: GroupMessage):
        if str(event.message_chain).startswith("/edgetts"):
            bsf = str(event.message_chain).replace("/edgetts", "")
            logger.info("edgetts文本推理任务：" + bsf)
            r = await edgetts({"text": bsf, "speaker": speaker})
            logger.info("edgetts 完成")
            await bot.send(event, Voice(path=r))'''

    #外部bert_vits2以及Modelscopetts
    @bot.on(GroupMessage)
    async def taffySayf(event: GroupMessage):
        if "说" in str(event.message_chain) and str(event.message_chain).split("说")[0] in spe and str(event.message_chain).startswith(prefix):
            data = {"speaker": str(event.message_chain).split("说")[0].replace(prefix,""),
                    "text": str(event.message_chain).replace(prefix,"").replace(str(event.message_chain).split("说")[0] + "说", "")}

            try:
                path = await taffySayTest(data, berturl, proxy)
                await bot.send(event, Voice(path=path))
            except:
                pass
