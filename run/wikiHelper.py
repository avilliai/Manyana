# -*- coding: utf-8 -*-
import os

import requests
import yaml
from mirai import GroupMessage,MessageChain
from mirai import Image, Voice
from mirai.models import ForwardMessageNode, Forward
from plugins.BlackMythWuKongWiki import wukongwiki
from plugins.toolkits import random_str,screenshot_to_pdf_and_png
from plugins.newsEveryDay import nong
from plugins.vitsGenerate import voiceGenerate


def main(bot, logger):
    logger.info("blueArchive")
    global punishing
    with open('data/text/Punishing.yaml', 'r', encoding='utf-8') as f:
        punishing = yaml.load(f.read(), Loader=yaml.FullLoader)
    global newResult
    with open('data/blueArchive/character.yaml', 'r', encoding='utf-8') as f:
        newResult = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    @bot.on(GroupMessage)
    async def screenShoot(event: GroupMessage):
        if str(event.message_chain).startswith("截图#"):
            url = str(event.message_chain).split("#")[1]
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("接收网页截图任务url:" + url)
            try:
                await screenshot_to_pdf_and_png(url, path, width=1024, height=980)
            except:
                logger.error("截图失败!")
            await bot.send(event, Image(path=path), True)

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        global punishing
        if "战双查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("战双查询")[1]
            logger.info("查询战双角色:" + aimCharacter)
            for i in punishing:
                if aimCharacter in punishing.get(i).get('otherName'):
                    if 'detail' in punishing.get(i):
                        logger.info("存在本地数据文件，直接发送")
                        path = punishing.get(i).get("detail")
                        try:
                            await bot.send(event, Image(path=path), True)
                            return
                        except:
                            logger.error("失败，重新抓取")

                    if True:
                        logger.warning("没有本地数据文件，启用下载")
                        await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                        url = 'https://wiki.biligame.com' + punishing.get(i).get('url')
                        path = "data/pictures/punishing/" + random_str() + '.png'
                        data1 = punishing.get(i)
                        try:
                            #webScreenShoot(url,path,1200,6500)
                            await screenshot_to_pdf_and_png(url, path)
                        except:
                            logger.warning("查询战双角色:" + aimCharacter + " 失败，未收录对应数据")
                            logger.info("发送语音()：数据库里好像没有这个角色呢,要再检查一下吗？")
                            await bot.send(event, "查询战双角色:" + aimCharacter + " 失败，未收录对应数据")
                            return
                        data1["detail"] = path
                        punishing[i] = data1
                        logger.info("写入文件")
                        # logger.info(newResult)
                        with open('data/text/Punishing.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(punishing, file, allow_unicode=True)

                        logger.info("发送成功")
                        await bot.send(event, Image(path=path), True)
                    return
                else:
                    continue

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        if "明日方舟查询" in str(event.message_chain) or "方舟查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("查询")[1]
            logger.info("查询明日方舟角色:" + aimCharacter)
            cha = os.listdir("data/arknights")
            if aimCharacter + ".png" in cha:
                logger.info("存在本地数据文件，直接发送")
                path = "data/arknights/" + aimCharacter + ".png"
                try:
                    await bot.send(event, Image(path=path), True)
                    return
                except:
                    logger.error("失败，重新抓取")

            if True:
                logger.warning("没有本地数据文件，启用下载")
                await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                url = 'https://wiki.biligame.com/arknights/' + aimCharacter
                path = "data/arknights/" + aimCharacter + ".png"

                try:
                    #webScreenShoot(url,path,1200,9500)
                    await screenshot_to_pdf_and_png(url, path)
                except:
                    logger.warning("查询方舟角色:" + aimCharacter + " 失败，未收录对应数据")
                    await bot.send(event, "查询方舟角色:" + aimCharacter + " 失败")
                    return
                await bot.send(event, Image(path=path), True)
                logger.info("发送成功")
                return

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        if "王者查询" in str(event.message_chain) or "农查询" in str(event.message_chain) or "王者荣耀查询" in str(
                event.message_chain):
            aimCharacter = str(event.message_chain).split("查询")[1]
            logger.info("查询王者荣耀角色:" + aimCharacter)
            cha = os.listdir("data/Elo")
            if aimCharacter + ".png" in cha:
                logger.info("存在本地数据文件，直接发送")
                path = "data/Elo/" + aimCharacter + ".png"
                try:
                    st1 = " "
                    try:
                        r = requests.get(
                            url="https://www.sapi.run/hero/select.php?hero=" + aimCharacter + "&type=aqq").json()
                        logger.info("王者战力查询：" + str(r.get("data")).replace(",", "\n"))
                        st1 = str(r.get("data")).replace(",", "\n")
                    except:
                        logger.error("战力查询error")
                    await bot.send(event, (Image(path=path), st1))
                    return
                except:
                    logger.error("失败，重新抓取")

            if True:
                logger.warning("没有本地数据文件，启用下载")
                await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                url = 'https://xiaoapi.cn/API/wzry_pic.php?msg=' + aimCharacter
                path = "data/Elo/" + aimCharacter + ".png"
                st1 = " "
                try:
                    # webScreenShoot(url,path,1200,9500)
                    await nong(url, aimCharacter)
                    r = requests.get(
                        url="https://www.sapi.run/hero/select.php?hero=" + aimCharacter + "&type=aqq").json()
                    logger.info("王者战力查询：" + str(r.get("data")).replace(",", "\n"))
                    st1 = str(r.get("data")).replace(",", "\n")
                    #await bot.send(event,str(r.get("data")).replace(",", "\n"))
                except:
                    logger.warning("查询农角色:" + aimCharacter + " 失败，未收录对应数据")
                    logger.info("发送语音()：数据库里好像没有这个角色呢,要再检查一下吗？")
                    if not os.path.exists("data/autoReply/voiceReply/queryFalse.wav"):
                        data = {"text": "[ZH]数据库里好像没有这个角色呢,要再检查一下吗？[ZH]",
                                "out": "data/autoReply/voiceReply/queryFalse.wav"}
                        await voiceGenerate(data)
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                    else:
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                        return

                await bot.send(event, (Image(path=path), st1))
                logger.info("发送成功")
                return

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        if "后室查询" in str(event.message_chain) or "br查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("查询")[1]
            logger.info("查询后室层级:" + aimCharacter)
            cha = os.listdir("data/backrooms")
            if aimCharacter + ".png" in cha:
                logger.info("存在本地数据文件，直接发送")
                path = "data/backrooms/" + aimCharacter + ".png"
                try:
                    await bot.send(event, Image(path=path), True)
                    return
                except:
                    logger.error("失败，重新抓取")

            if True:
                logger.warning("没有本地数据文件，启用下载")
                await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                url = 'http://backrooms-wiki-cn.wikidot.com//' + aimCharacter
                path = "data/backrooms/" + aimCharacter + ".png"

                try:
                    # webScreenShoot(url,path,1200,9500)
                    await screenshot_to_pdf_and_png(url, path)
                except:
                    logger.warning("查询后室层级:" + aimCharacter + " 失败，未收录对应数据")
                    logger.info("发送语音()：数据库里好像没有这个层级呢,要再检查一下吗？")
                    await bot.send(event, "查询失败")
                    return

                await bot.send(event, Image(path=path), True)
                logger.info("发送成功")
                return
    @bot.on(GroupMessage)
    async def wukongwikiQ(event: GroupMessage):
        if str(event.message_chain).startswith("黑神话查询"):
            try:
                aim=str(event.message_chain).replace("黑神话查询","")
                logger.info(f"黑神话查询{aim}")
                mesChain=await wukongwiki(aim,controller["黑神话wiki"]["技能招式"])
                if controller["黑神话wiki"]["以聊天记录形式发送"]:
                    b1=[]
                    for i in mesChain:
                        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain(i)))
                    await bot.send(event, Forward(node_list=b1))
                else:
                    for i in mesChain:
                        await bot.send(event,MessageChain(i),True)
            except Exception as e:
                logger.error(e)
                await bot.send(event,f"查询{aim}失败，请重试或检查bot网络连接")