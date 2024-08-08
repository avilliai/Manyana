# -*- coding: utf-8 -*-
import re

import yaml
from mirai import GroupMessage, At, Plain,MessageChain
from mirai import Voice
from mirai.models import ForwardMessageNode, Forward
from plugins.toolkits import translate,random_str
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
                  "奶绿", "七海", "恬豆", "科比",'anzai', '「信使」', '「公子」', '「博士」', '「大肉丸」', '「女士」', '「散兵」', '「白老先生」', '七七', '三月七', '上杉',
     '丹吉尔', '丹恒', '丹枢', '丽莎', '久利须', '久岐忍', '九条裟罗', '九条镰治', '云堇', '五郎', '伊利亚斯', '伊迪娅',
     '优菈', '伦纳德', '佐西摩斯', '佩拉', '停云', '元太', '克列门特', '克拉拉', '克罗索', '八重神子', '公输师傅',
     '凝光', '凯亚', '凯瑟琳', '刃', '刻晴', '北斗', '半夏', '博易', '博来', '卡波特', '卡维', '卡芙卡', '卢卡',
     '可可利亚', '可莉', '史瓦罗', '吴船长', '哲平', '嘉玛', '嘉良', '回声海螺', '坎蒂丝', '埃勒曼', '埃尔欣根', '埃德',
     '埃泽', '埃洛伊', '埃舍尔', '塔杰·拉德卡尼', '塞塔蕾', '塞琉斯', '夏洛蒂', '多莉', '夜兰', '大慈树王', '大毫',
     '天叔', '天目十五', '奥兹', '奥列格', '女士', '妮露', '姬子', '娜塔莎', '娜维娅', '安柏', '安西', '宛烟', '宵宫',
     '岩明', '巴达维', '布洛妮娅', '希儿', '希露瓦', '帕姆', '帕斯卡', '常九爷', '康纳', '开拓者(女)', '开拓者(男)',
     '式大将', '彦卿', '影', '德沃沙克', '恕筠', '恶龙', '悦', '慧心', '戴因斯雷布', '托克', '托马', '拉赫曼', '拉齐',
     '掇星攫辰天君', '提纳里', '斯坦利', '斯科特', '旁白', '早柚', '昆钧', '明曦', '景元', '晴霓', '杜拉夫', '杰帕德',
     '松浦', '林尼', '枫原万叶', '柊千里', '查尔斯', '柯莱', '桑博', '欧菲妮', '毗伽尔', '沙扎曼', '派蒙', '流浪者',
     '浣溪', '浮游水蕈兽·元素生命', '海妮耶', '海芭夏', '深渊使徒', '深渊法师', '温迪', '烟绯', '爱德琳', '爱贝尔',
     '玛乔丽', '玛塞勒', '玛格丽特', '玲可', '珊瑚', '珊瑚宫心海', '珐露珊', '班尼特', '琳妮特', '琴', '瑶瑶', '瓦尔特',
     '甘雨', '田铁嘴', '申鹤', '留云借风真君', '白术', '白露', '百闻', '知易', '石头', '砂糖', '神里绫人', '神里绫华',
     '空', '符玄', '笼钓瓶一心', '米卡', '素裳', '纯水精灵？', '纳比尔', '纳西妲', '绮良良', '绿芙蓉', '罗刹',
     '罗莎莉亚', '羽生田千鹤', '老孟', '胡桃', '舒伯特', '艾丝妲', '艾伯特', '艾尔海森', '艾文', '艾莉丝', '芙宁娜',
     '芭芭拉', '荒泷一斗', '荧', '莎拉', '莫塞伊思', '莫娜', '莱依拉', '莺儿', '菲米尼', '菲谢尔', '萍姥姥', '萨赫哈蒂',
     '萨齐因', '蒂玛乌斯', '虎克', '螺丝咕姆', '行秋', '西拉杰', '言笑', '诺艾尔', '费斯曼', '赛诺', '辛焱', '达达利亚',
     '迈勒斯', '迈蒙', '迪卢克', '迪奥娜', '迪娜泽黛', '迪希雅', '那维莱特', '重云', '金人会长', '钟离', '银狼', '镜流',
     '长生', '阿佩普', '阿兰', '阿圆', '阿娜耶', '阿守', '阿尔卡米', '阿巴图伊', '阿扎尔', '阿拉夫', '阿晃', '阿洛瓦',
     '阿祇', '阿贝多', '陆行岩本真蕈·元素生命', '雷泽', '雷电将军', '霄翰', '霍夫曼', '青镞', '青雀', '香菱', '驭空',
     '魈', '鹿野奈奈', '鹿野院平藏', '黑塔', '龙二']
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
                event.message_chain) and len(str(event.message_chain).replace(str(At(bot.qq)),""))<6:
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
                                         message_chain=MessageChain("bert_vits2可用角色如下：\n" + str(modelScope))))
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                         message_chain=MessageChain("\n\nFishTTS可用角色请查看https://fish.audio/zh-CN/，均可通过 xx说调用。\n")))
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                         message_chain=MessageChain(f"outVits可用角色如下：\n{outVitsSpeakers}")))
            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                         message_chain=MessageChain(f"可发送 {prefix}xx说.......  以进行语音合成")))
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
