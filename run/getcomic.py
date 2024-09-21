# -*- coding:utf-8 -*-
import os
import shutil

import asyncio
from concurrent.futures import ThreadPoolExecutor

import yaml
from mirai import GroupMessage, MessageChain, Image, FriendMessage
from mirai.models import ForwardMessageNode, Forward

from plugins.jmcomicDownload import queryJM, downloadComic, downloadALLAndToPdf


def main(bot, logger):
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    friendsAndGroups = result.get("加群和好友")
    trustDays = friendsAndGroups.get("trustDays")
    with open('config.json', 'r', encoding='utf-8') as f:
        configData = yaml.load(f.read(), Loader=yaml.FullLoader)
    global userdict
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        userdict = yaml.load(file, Loader=yaml.FullLoader)
    global superUser
    superUser = [str(configData.get('master')), ]
    for i in userdict.keys():
        data = userdict.get(i)
        times = int(str(data.get('sts')))
        if times > trustDays:
            superUser.append(str(i))
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    jmcomicSettings = controller.get("JMComic")
    URLSource=jmcomicSettings.get("URLSource")
    if not jmcomicSettings.get("enable"):
        logger.warning("jmcomic相关功能已关闭。")
        return
    global operating
    operating=[]
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = resulttr.get("proxy")
    @bot.on(GroupMessage)
    async def querycomic(event: GroupMessage):
        global superUser,operating
        if str(event.message_chain).startswith("JM搜"):
            aim = str(event.message_chain).replace("JM搜", "")
            if jmcomicSettings.get("onlyTrustUser") and str(event.sender.id) not in superUser:
                await bot.send(event, "用户无权限",True)
                return
            if aim in operating:
                await bot.send(event,"相关文件占用中，等会再发吧",True)
                return
            logger.info(f"JM搜索: {aim}")
            operating.append(aim)
            # 分页查询，search_site就是禁漫网页上的【站内搜索】
            # 原先的执行方式将导致bot进程阻塞，任务添加到线程池，避免阻塞
            await bot.send(event, "在找了在找了，稍等一会哦(长时间不出就是被吞了)",True)
            try:
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    results = await loop.run_in_executor(executor, queryJM,aim,5)
            except Exception as e:
                logger.error(e)
                logger.exception("详细错误如下：")
                operating.remove(aim)
            try:
                cmList = []
                cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine", message_chain=MessageChain(f" \n腾子吞图严重，bot仅提供本子部分页面预览。\n图片已经过处理，但不保证百分百不被吞。可能显示不出来")))
                for i in results:
                    cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain(i[0])))
                    cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain(Image(path=i[1]))))
                await bot.send(event, Forward(node_list=cmList))
                operating.remove(aim)
                #await bot.send(event, "好了喵", True)
                for i in results:
                    os.remove(i[1])
                logger.info("已清除预览缓存")
            except Exception as e:
                logger.error(e)
                await bot.send(event, "寄了喵", True)
                operating.remove(aim)

    @bot.on(GroupMessage)
    async def download(event: GroupMessage):
        if str(event.message_chain).startswith("验车"):
            global operating
            if jmcomicSettings.get("onlyTrustUser") and str(event.sender.id) not in superUser:
                await bot.send(event, "用户无权限",True)
                return
            try:
                comic_id = int(str(event.message_chain).replace("验车", ""))
            except:
                await bot.send(event, "无效输入 int，指令格式如下\n验车【车牌号】\n如：验车604142",True)
                return
            if comic_id in operating:
                await bot.send(event,"相关文件占用中，等会再试试吧")
                return
            operating.append(comic_id)
            logger.info(f"JM验车 {comic_id}")
            await bot.send(event, "下载中...稍等喵",True)
            try:
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    png_files = await loop.run_in_executor(executor, downloadComic, comic_id, 1,
                                                           jmcomicSettings.get("previewPages"))
            except Exception as e:
                logger.error(e)
                await bot.send(event, "下载失败",True)
                operating.remove(comic_id)
                return
            cmList = []
            logger.info(png_files)
            cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine", message_chain=MessageChain(f"车牌号：{comic_id} \n腾子吞图严重，bot仅提供本子部分页面预览。\n图片已经过处理，但不保证百分百不被吞。可能显示不出来")))
            shutil.rmtree(f"data/pictures/benzi/temp{comic_id}")
            logger.info("移除预览缓存")
            for path in png_files:
                cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",
                                                 message_chain=MessageChain(Image(path=path))))
            await bot.send(event, Forward(node_list=cmList))
            operating.remove(comic_id)
            for path in png_files:
                os.remove(path)
            logger.info("本子预览缓存已清除.....")
    @bot.on(GroupMessage)
    async def downloadAndToPdf(event: GroupMessage):
        if str(event.message_chain).startswith("JM下载"):
            global operating
            if jmcomicSettings.get("onlyTrustUser") and str(event.sender.id) not in superUser:
                await bot.send(event, "用户无权限",True)
                return
            try:
                comic_id = int(str(event.message_chain).replace("JM下载",""))
                logger.info(f"JM下载启动 aim: {comic_id}")
            except:
                await bot.send(event,"非法参数，指令示例 JM下载601279")
                return
            if comic_id in operating:
                await bot.send(event,"相关文件占用中，等会再试试吧",True)
                return
            operating.append(comic_id)
            try:
                await bot.send(event,"已启用线程,请等待下载完成，耗时可能较长。bot将以链接形式返回pdf文件",True)
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    r=await loop.run_in_executor(executor, downloadALLAndToPdf, comic_id, jmcomicSettings.get("savePath"),URLSource,proxy)
                logger.info(f"下载完成，车牌号：{comic_id} \n下载链接：{r} ")
                await bot.send(event,f"下载完成，车牌号：{comic_id} \n下载链接：{r}\n请复制到浏览器打开，为避免失效请尽快使用",True)
            except Exception as e:
                logger.error(e)
                await bot.send(event, "下载失败",True)
            finally:
                operating.remove(comic_id)
                shutil.rmtree(f"{jmcomicSettings.get('savePath')}/{comic_id}")
                os.remove(f"{jmcomicSettings.get('savePath')}/{comic_id}.pdf")
                logger.info("移除预览缓存")



