# -*- coding:utf-8 -*-
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
    superUser = [int(configData.get('master')), ]
    for i in userdict.keys():
        data = userdict.get(i)
        times = int(str(data.get('sts')))
        if times > trustDays:
            superUser.append(str(i))
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    jmcomicSettings = controller.get("JMComic")
    @bot.on(GroupMessage)
    async def querycomic(event: GroupMessage):
        global superUser
        if str(event.message_chain).startswith("JM搜"):
            if jmcomicSettings.get("onlyTrustUser") and str(event.sender.id) not in superUser:
                await bot.send(event, "用户无权限",True)
                return
            # 分页查询，search_site就是禁漫网页上的【站内搜索】
            # 原先的执行方式将导致bot进程阻塞，任务添加到线程池，避免阻塞
            await bot.send(event, "在找了在找了，稍等一会哦(长时间不出就是被吞了)",True)
            try:
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    results = await loop.run_in_executor(executor, queryJM, querycomic)
            except Exception as e:
                logger.error(e)
                logger.exception("详细错误如下：")
            try:
                cmList = []
                for i in results:
                    cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",
                                                     message_chain=MessageChain([i[0], Image(path=i[1])])))
                await bot.send(event, Forward(node_list=cmList))
                await bot.send(event, "好了喵", True)
            except Exception as e:
                logger.error(e)
                await bot.send(event, "寄了喵", True)

    @bot.on(GroupMessage)
    async def download(event: GroupMessage):
        if str(event.message_chain).startswith("验车"):
            if jmcomicSettings.get("onlyTrustUser") and str(event.sender.id) not in superUser:
                await bot.send(event, "用户无权限",True)
                return
            try:
                comic_id = int(str(event.message_chain).replace("验车", ""))
            except:
                await bot.send(event, "无效输入 int，指令格式如下\n验车【车牌号】\n如：验车604142",True)
                return
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
            cmList = []
            logger.info(png_files)
            cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine", message_chain=MessageChain(f"车牌号：{comic_id} \n腾子吞图严重，bot仅提供本子部分页面预览。\n图片已经过处理，但不保证百分百不被吞。可能显示不出来")))
            for path in png_files:
                cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",
                                                 message_chain=MessageChain(Image(path=path))))
            await bot.send(event, Forward(node_list=cmList))
    @bot.on(GroupMessage)
    async def downloadAndToPdf(event: GroupMessage):
        if str(event.message_chain).startswith("JM下载"):
            logger.info("JM下载启动")
            try:
                comic_id = int(str(event.message_chain).replace("JM下载",""))
            except:
                await bot.send(event,"非法参数，指令示例 JM下载601279")
                return
            try:
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    r=await loop.run_in_executor(executor, downloadALLAndToPdf, comic_id, jmcomicSettings.get("savePath"))
                await bot.send(event,f"下载完成，车牌号：{comic_id} \n下载链接：{r}")
            except Exception as e:
                logger.error(e)
                await bot.send(event, "下载失败",True)


