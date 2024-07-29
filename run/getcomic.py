# -*- coding:utf-8 -*-
import asyncio
import random
from concurrent.futures import ThreadPoolExecutor

import yaml
from mirai import GroupMessage,MessageChain,Image,FriendMessage
import os
import shutil
import random
import jmcomic
from mirai.models import ForwardMessageNode, Forward
from functools import partial

from plugins.jmcomicDownload import queryJM, downloadComic


def main(bot, logger):
    @bot.on(GroupMessage)
    async def querycomic(event: GroupMessage):
        if str(event.message_chain).startswith("JM搜"):
            querycomic = str(event.message_chain).replace("JM搜","")
            # 分页查询，search_site就是禁漫网页上的【站内搜索】
            # 原先的执行方式将导致bot进程阻塞，任务添加到线程池，避免阻塞
            await bot.send(event,"在找了在找了，稍等一会哦(长时间不出就是被吞了)")
            try:
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    results=await loop.run_in_executor(executor, queryJM, querycomic)
            except Exception as e:
                logger.error(e)
                logger.exception("详细错误如下：")
            if results!=None:
                cmList=[]
                for i in results:
                    cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain([i[0],Image(path=i[1])])))
                await bot.send(event, Forward(node_list=cmList))

    @bot.on(GroupMessage)
    async def download(event: GroupMessage):
        if str(event.message_chain).startswith("验车"):
            try:
                comic_id = int(str(event.message_chain).replace("验车",""))
            except:
                await bot.send(event,"无效输入 int")
                return
            await bot.send(event, "下载中...")
            try:
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    png_files=await loop.run_in_executor(executor, downloadComic, comic_id)
            except Exception as e:
                logger.error(e)
                await bot.send(event,"下载失败")
            cmList=[]
            logger.info(png_files)
            cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine", message_chain=MessageChain(
                "图片已经过处理，但不保证百分百不被吞。可能显示不出来")))
            for path in png_files:
                cmList.append(ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain(Image(path=path))))


            await bot.send(event, Forward(node_list=cmList))


   
