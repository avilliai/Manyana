# -*- coding: utf-8 -*-
import os
import random

import httpx
import yaml
from mirai import GroupMessage
from mirai import Image, MessageChain
from mirai.models import ForwardMessageNode, Forward

from plugins.imgSearch import superSearch, test1, test
from plugins.setuModerate import setuModerate


def main(bot, api_key, proxy, logger):
    logger.info("搜图功能启动完毕")
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    cookies = result.get("e-hentai")
    moderateK = result.get("moderate")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    selfsensor = result1.get("moderate").get("selfsensor")
    selfthreshold = result1.get("moderate").get("selfthreshold")
    global dataGet
    dataGet = {}
    global userSearch

    @bot.on(GroupMessage)
    async def startYourSearch(event: GroupMessage):
        global dataGet
        if str(event.message_chain) == "搜图":
            await bot.send(event, "请发送要搜索的图片")
            dataGet[event.sender.id] = []

    @bot.on(GroupMessage)
    async def imgSearcher(event: GroupMessage):
        global dataGet
        if ("搜图" in str(event.message_chain) or event.sender.id in dataGet) and event.message_chain.count(Image):
            logger.info("接收来自群：" + str(event.group.id) + " 用户：" + str(event.sender.id) + " 的搜图指令")
            dataGet[event.sender.id] = []
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            proxies = {
                "http://": proxy,
                "https://": proxy
            }

            # Replace the key with your own
            dataa = {"url": img_url, "db": "999", "api_key": api_key, "output_type": "2", "numres": "3"}
            logger.info("发起搜图请求")
            await bot.send(event, "正在检索....请稍候")
            #sauceno搜图

            try:
                async with httpx.AsyncClient(proxies=proxies) as client:
                    response = await client.post(url="https://saucenao.com/search.php", data=dataa)
                #response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
                logger.info("sauceno获取到结果" + str(response.json().get("results")[0]))
                #logger.info("下载缩略图")
                #filename=dict_download_img(img_url,dirc="data/pictures/imgSearchCache")
                result = ' similarity:' + str(
                    response.json().get("results")[0].get('header').get('similarity')) + "\n" + str(
                    response.json().get("results")[0].get('data')).replace(",", "\n").replace("{", " ").replace("}",
                                                                                                                "").replace(
                    "'", "").replace("[", "").replace("]", "")
                urlss = str(response.json().get("results")[0].get('header').get('thumbnail'))
                #聊天记录模式不再可用，因此关闭

                if selfsensor:
                    try:
                        thurs = await setuModerate(urlss, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            urlss = "data/colorfulAnimeCharacter/" + random.choice(
                                os.listdir("data/colorfulAnimeCharacter"))
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey不可用")
                '''b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(["sauceno获取到结果:\n" + result, Image(url=urlss)]))'''
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(["sauceno获取到结果：\n" + result]))
                # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
                dataGet.get(event.sender.id).append(b1)

                #await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
            except:
                logger.error("sauceno搜图失败，无结果或访问次数过多，请稍后再试")
                #b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                #message_chain=MessageChain(["sauceno搜图失败，无结果或访问次数过多，请稍后再试",Image(path="data/autoReply/imageReply/axaAaRaUaaafa7a.png")]))
                #聊天记录不再可用，暂时关闭
                #dataGet.get(event.sender.id).append(b1)

            #使用TraceMoe搜图
            try:
                result, piccc = await test(url=img_url, proxies=proxy)
                logger.info("TraceMoe获取到结果：" + result)

                if selfsensor:
                    try:
                        thurs = await setuModerate(piccc, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            piccc = "data/colorfulAnimeCharacter/" + random.choice(
                                os.listdir("data/colorfulAnimeCharacter"))
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey不可用")
                '''b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(
                                            ["TraceMoe获取到结果：\n" + result, Image(url=piccc)]))'''
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(
                                            ["TraceMoe获取到结果：\n" + result]))
                dataGet.get(event.sender.id).append(b1)
            except:
                logger.error("TraceMoe未获取到结果")
                #b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                #message_chain=MessageChain(["TraceMoe搜图失败，无结果或访问次数过多，请稍后再试", Image(
                #path="data/autoReply/imageReply/axaAaRaUaaafa7a.png")]))
                # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
                #dataGet.get(event.sender.id).append(b1)
            #使用Ascii2D
            try:
                result, piccc = await test1(url=img_url, proxies=proxy)
                logger.info("Ascii2D获取到结果：\n" + result)

                if selfsensor:
                    try:
                        thurs = await setuModerate(piccc, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            piccc = "data/colorfulAnimeCharacter/" + random.choice(
                                os.listdir("data/colorfulAnimeCharacter"))
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey不可用")
                '''b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                 message_chain=MessageChain(["Ascii2D获取到结果：\n" +result, Image(url=piccc)]))'''
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(["Ascii2D获取到结果：\n" + result]))
                dataGet.get(event.sender.id).append(b1)
            except:
                logger.error("Ascii2D未获取到结果")
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(
                                            ["Ascii2D搜图失败，无结果或访问次数过多，请稍后再试", Image(
                                                path="data/autoReply/imageReply/axaAaRaUaaafa7a.png")]))

                dataGet.get(event.sender.id).append(b1)

            # 使用IQDB
            try:
                result, piccc = await superSearch(url=img_url, proxies=proxy)
                logger.info("iqdb获取到结果：\n" + result)

                if selfsensor:
                    try:
                        thurs = await setuModerate(piccc, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            piccc = "data/colorfulAnimeCharacter/" + random.choice(
                                os.listdir("data/colorfulAnimeCharacter"))
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey不可用")
                '''b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(["iqdb获取到结果：\n" + result, Image(url=piccc)]))'''
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(["iqdb获取到结果：\n" + result]))
                dataGet.get(event.sender.id).append(b1)

            except:
                logger.error("iqdb未获取到结果")
                '''try:
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain([result, Image(
                                                path="data/autoReply/imageReply/axaAaRaUaaafa7a.png")]))
                except:
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(["iqdb搜图失败，无结果或访问次数过多，请稍后再试", Image(
                                                path="data/autoReply/imageReply/axaAaRaUaaafa7a.png")]))
                # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
                #dataGet.get(event.sender.id).append(b1)'''
            # 使用E-hentai
            '''try:
                result, piccc = await test2(url=img_url, proxies=proxy,cookies=cookies)
                logger.info("E-hentai获取到结果：" + result)
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(["E-hentai获取到结果：\n" +result, Image(url=piccc)]))
                dataGet.get(event.sender.id).append(b1)
                try:
                    pass
                    #await bot.send(event, (result, Image(url=piccc)))
                except:
                    await bot.send(event, result)
            except:
                logger.error("E-hentai未获取到结果")
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain(["E-hentai搜图失败，无结果或访问次数过多，请稍后再试", Image(
                                            path="data/autoReply/imageReply/axaAaRaUaaafa7a.png")]))
                # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
                dataGet.get(event.sender.id).append(b1)'''
            try:
                await bot.send(event, Forward(node_list=dataGet.get(event.sender.id)))

            except Exception as e:
                logger.error(e)
                await bot.send(event, "出错，请稍后再试")
            dataGet.pop(event.sender.id)
