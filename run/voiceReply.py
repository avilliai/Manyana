# -*- coding: utf-8 -*-
import re

import asyncio
import yaml
from mirai import GroupMessage, At, Plain,MessageChain
from mirai import Voice
from mirai.models import ForwardMessageNode, Forward

from plugins.modelsLoader import modelLoader
from plugins.toolkits import translate,random_str
from plugins.vitsGenerate import voiceGenerate, superVG, sovits, taffySayTest, gptVitsSpeakers


def main(bot, master, logger):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    FishTTSAuthorization = result0.get("FishTTSAuthorization")
    GPTSOVITS_SPEAKERS = asyncio.run(gptVitsSpeakers())
    berturl = result0.get("bert_colab")
    proxy = result0.get("proxy")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    spe = result.get("语音功能设置").get("bert_speakers")
    prefix=result.get("语音功能设置").get("prefix")
    modelScope = ["BT", "塔菲", "阿梓", "otto", "丁真", "星瞳", "东雪莲", "嘉然", "孙笑川", "亚托克斯", "文静", "鹿鸣",
                  "奶绿", "七海", "恬豆", "科比",'辛焱', '鹿野奈奈', '云堇', '瑶瑶', '珐露珊', '蒂玛乌斯', '那维莱特', '砂糖',
                  '康纳', '刻晴', '嘉玛', '知易', '魈', '阿拉夫', '塞塔蕾', '大毫', '伊利亚斯', '欧菲妮', '玛塞勒', '「白老先生」',
                  '式大将', '埃洛伊', '卡芙卡', '公输师傅', '舒伯特', '艾莉丝', '八重神子', '海妮耶', '克罗索', '明曦', '阿佩普',
                  '掇星攫辰天君', '奥兹', '菲米尼', '甘雨', '奥列格', '巴达维', '老孟', '阿圆', '坎蒂丝', '鹿野院平藏', '佐西摩斯',
                  '青镞', '凝光', '「博士」', '斯科特', '阿尔卡米', '沙扎曼', '白术', '派蒙', '纳比尔', '回声海螺', '荧', '帕斯卡',
                  '埃德', '五郎', '萨齐因', '帕姆', '西拉杰', '流浪者', '松浦', '驭空', '「大肉丸」', '莫娜', '多莉', '大慈树王',
                  '留云借风真君', '优菈', '希露瓦', '桑博', '宵宫', '元太', '温迪', '芙宁娜', '九条镰治', '开拓者(男)', '可可利亚',
                  '阿巴图伊', '埃尔欣根', '布洛妮娅', '琳妮特', '岩明', '安柏', '玛乔丽', '费斯曼', '娜维娅', '停云', '天目十五',
                  '莫塞伊思', '史瓦罗', '玛格丽特', '埃泽', '慧心', '绿芙蓉', '浮游水蕈兽·元素生命', '申鹤', '伊迪娅', '托马', '班尼特',
                  '卢卡', '罗刹', 'anzai', '姬子', '菲谢尔', '悦', '莺儿', '莎拉', '金人会长', '迪希雅', '柊千里', '博来', '三月七',
                  '烟绯', '拉齐', '丹吉尔', '赛诺', '虎克', '埃勒曼', '阿扎尔', '深渊法师', '刃', '戴因斯雷布', '神里绫华', '青雀',
                  '萍姥姥', '笼钓瓶一心', '石头', '海芭夏', '九条裟罗', '安西', '阿贝多', '行秋', '可莉', '上杉', '钟离', '提纳里',
                  '绮良良', '迪奥娜', '「公子」', '阿守', '言笑', '阿兰', '龙二', '阿洛瓦', '重云', '丹恒', '开拓者(女)', '常九爷',
                  '瓦尔特', '凯瑟琳', '恕筠', '百闻', '阿娜耶', '米卡', '塔杰·拉德卡尼', '莱依拉', '旁白', '吴船长', '田铁嘴',
                  '托克', '艾文', '香菱', '空', '迪卢克', '迪娜泽黛', '霄翰', '陆行岩本真蕈·元素生命', '七七', '神里绫人', '克列门特',
                  '久利须', '早柚', '「女士」', '半夏', '荒泷一斗', '佩拉', '斯坦利', '柯莱', '艾尔海森', '晴霓', '艾丝妲', '娜塔莎',
                  '白露', '珊瑚', '霍夫曼', '迈勒斯', '毗伽尔', '螺丝咕姆', '博易', '符玄', '嘉良', '胡桃', '彦卿', '卡波特', '丹枢',
                  '阿祇', '林尼', '久岐忍', '深渊使徒', '琴', '芭芭拉', '妮露', '天叔', '凯亚', '「信使」', '夏洛蒂', '纯水精灵？',
                  '羽生田千鹤', '影', '伦纳德', '罗莎莉亚', '哲平', '珊瑚宫心海', '素裳', '希儿', '查尔斯', '宛烟', '镜流', '克拉拉',
                  '迈蒙', '玲可', '长生', '女士', '爱德琳', '丽莎', '「散兵」', '杰帕德', '艾伯特', '塞琉斯', '萨赫哈蒂', '爱贝尔',
                  '枫原万叶', '雷电将军', '杜拉夫', '埃舍尔', '夜兰', '拉赫曼', '达达利亚', '阿晃', '纳西妲', '卡维', '诺艾尔',
                  '德沃沙克', '浣溪', '北斗', '银狼', '景元', '黑塔', '恶龙', '雷泽', '昆钧']
    outVitsSpeakers=[
        "丁真",
        "AD学姐",
        "赛马娘",
        "黑手",
        "蔡徐坤",
        "孙笑川",
        "邓紫棋",
        "东雪莲",
        "塔菲",
        "央视配音",
        "流萤",
        "郭德纲",
        "雷军",
        "周杰伦",
        "懒洋洋",
        "女大学生",
        "烧姐姐",
        "麦克阿瑟",
        "马老师",
        "孙悟空",
        "海绵宝宝",
        "光头强",
        "陈泽",
        "村民",
        "猪猪侠",
        "猪八戒",
        "薛之谦",
        "大司马",
        "刘华强",
        "特朗普",
        "满穗",
        "桑帛"
    ]

    models = modelLoader()

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "说" in str(event.message_chain) and str(event.message_chain).startswith(prefix):

            text = str(event.message_chain)[len(str(event.message_chain).split("说")[0]) + 1:]
            speaker = str(event.message_chain).split("说")[0].replace(prefix,"")
            if GPTSOVITS_SPEAKERS!=None:
                original_speaker=speaker
                if f"{speaker}【原神】" in list(GPTSOVITS_SPEAKERS.keys()):
                    speaker = f"{speaker}【原神】"
                elif f"{speaker}【崩坏3】" in list(GPTSOVITS_SPEAKERS.keys()):
                    speaker = f"{speaker}【崩坏3】"
                elif f"{speaker}【星穹铁道】" in list(GPTSOVITS_SPEAKERS.keys()):
                    speaker = f"{speaker}【星穹铁道】"
                if speaker in list(GPTSOVITS_SPEAKERS.keys()):
                    try:
                        data = {"speaker": speaker,
                                "text": text}
                        logger.info("gptSovits语音合成:" + data["text"])
                        path = await superVG(data, "gptSovits")
                        await bot.send(event, Voice(path=path))
                        return
                    except Exception as e:
                        logger.error(e)
                        speaker = original_speaker
            for i in models:
                if speaker in i and speaker != "":
                    path = 'data/voices/' + random_str() + '.wav'
                    logger.info("语音生成_文本" + text)
                    logger.info("语音生成_模型:" + speaker)
                    data = {"text": text, "out": path, 'speaker': speaker}
                    await superVG(data,"vits")
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




    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "日文" in str(event.message_chain) and str(event.message_chain).startswith(prefix):
            speaker = str(event.message_chain).split("日文")[0].replace(prefix,"")
            text = str(event.message_chain)[len(str(event.message_chain).split("日文")[0]) + 1:]

            logger.info("语音生成_文本" + text)
            for i in models:
                if speaker in i and speaker != "":
                    path = 'data/voices/' + random_str() + '.wav'
                    logger.info("语音生成_文本" + text)
                    logger.info("语音生成_模型:" + speaker)
                    data = {"text": text, "out": path, 'speaker': speaker}
                    await superVG(data, "vits",urls="",langmode="<jp>")
                    await bot.send(event, Voice(path=path))
                    return


    @bot.on(GroupMessage)
    async def checkCharacters(event: GroupMessage):
        if "角色" in str(event.message_chain) and At(bot.qq) in event.message_chain and "模板" not in str(
                event.message_chain) and len(str(event.message_chain).replace(str(At(bot.qq)),""))<6:
            #print(len(str(event.message_chain).replace(str(At(bot.qq)))))
            try:
                str1 = "vits可用角色如下：\n"
                for i in models:
                    str1+=i+" |"
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
            if GPTSOVITS_SPEAKERS!=None:
                b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                             message_chain=MessageChain(f"gptsoVits可用角色如下：\n{str(list(GPTSOVITS_SPEAKERS.keys()))}")))
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
