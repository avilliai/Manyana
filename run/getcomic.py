# -*- coding:utf-8 -*-
import asyncio
import os
import random
import shutil
from concurrent.futures import ThreadPoolExecutor

import httpx
import yaml
from mirai import GroupMessage, MessageChain, Image
from mirai.models import ForwardMessageNode, Forward

from plugins.jmcomicDownload import downloadComic, downloadALLAndToPdf, JM_search, JM_search_week, JM_search_comic_id


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
    async def addPermission(event: GroupMessage):
        if str(event.message_chain).startswith("授权#") and event.sender.id==int(configData.get('master')):
            global superUser
            try:
                superUser.append(int(str(event.message_chain).replace("授权#","")))
                superUser.append(str(event.message_chain).replace("授权#",""))
            except:
                pass
    @bot.on(GroupMessage)
    async def querycomic(event: GroupMessage):
        global superUser,operating
        if str(event.message_chain).startswith("jm搜") or str(event.message_chain).startswith("JM搜"):
            keyword = str(event.message_chain)
            index = keyword.find("搜")
            if index != -1:
                keyword = keyword[index + len("查询") :]
                if ':' in keyword or ' ' in keyword or '：' in keyword:
                    keyword = keyword[+1:]
                print(keyword)
                context=JM_search(keyword)
            aim = context
            if jmcomicSettings.get("onlyTrustUser") and str(event.sender.id) not in superUser:
                await bot.send(event, "用户无权限",True)
                return
            if aim in operating:
                await bot.send(event,"相关文件占用中，等会再发吧",True)
                return
            logger.info(f"JM搜索: {aim}")
            try:
                if context=="":
                    await bot.send(event, "好像没有找到你说的本子呢~~~")
                    return
                cmList = [
                    ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine", message_chain=MessageChain(context))]
                await bot.send(event, Forward(node_list=cmList))
            except Exception as e:
                logger.error(e)
                await bot.send(event, "寄了喵", True)
    @bot.on(GroupMessage)
    async def download(event: GroupMessage):
        if '本周jm' == str(event.message_chain) or '本周JM' == str(event.message_chain) or '今日jm' == str(event.message_chain) or '今日JM' == str(event.message_chain):
            context=JM_search_week()
            cmList = [ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",
                                         message_chain=MessageChain('本周的JM排行如下，请君过目\n')),
                      ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",
                                         message_chain=MessageChain(context))]
            await bot.send(event, Forward(node_list=cmList))



    
    @bot.on(GroupMessage)
    async def download(event: GroupMessage):
        if str(event.message_chain).startswith("验车") or str(event.message_chain)=="随机本子":
            global operating
            if jmcomicSettings.get("onlyTrustUser") and str(event.sender.id) not in superUser:
                await bot.send(event, "用户无权限",True)
                return
            try:
                if str(event.message_chain).startswith("验车"):
                    comic_id = int(str(event.message_chain).replace("验车", ""))
                else:
                    context=['正在随机ing，请稍等喵~~','正在翻找好看的本子喵~','嘿嘿，JM，启动！！！！','正在翻找JM.jpg','有色色！我来了','hero来了喵~~','了解~','全力色色ing~']
                    await bot.send(event, random.choice(context))
                    context= JM_search_comic_id()
                    comic_id = context[random.randint(1, len(context)) - 1]
            except Exception as e:
                logger.error(e)
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
                await bot.send(event,"已启用线程,请等待下载完成",True)
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    r=await loop.run_in_executor(executor, downloadALLAndToPdf, comic_id, jmcomicSettings.get("savePath"),URLSource,proxy)
                logger.info(f"下载完成，车牌号：{comic_id} \n下载链接：{r} ")
                if r:
                    await bot.send(event,f"下载完成，车牌号：{comic_id} \n下载链接：{r}\n请复制到浏览器打开，为避免失效请尽快使用",True)
            except Exception as e:
                logger.error(e)
                await bot.send(event, "下载失败",True)
            finally:
                try:
                    shutil.rmtree(f"{jmcomicSettings.get('savePath')}/{comic_id}")
                    if jmcomicSettings.get("sendFile"):
                        absolute_path = os.path.abspath(f"{jmcomicSettings.get('savePath')}/{comic_id}.pdf")
                        await sendFile(event,absolute_path,comic_id)
                    logger.info("移除预览缓存")
                    await bot.send(event,"下载完成了( >ρ< ”)",True)
                    if jmcomicSettings.get("autoClearPDF"):
                        await wait_and_delete_file(f"{jmcomicSettings.get('savePath')}/{comic_id}.pdf")

                except Exception as e: 
                    logger.error(e)
                finally:
                    operating.remove(comic_id)
                
    async def sendFile(event,path,comic_id):
        url="http://localhost:3000/upload_group_file"
        header = {
        "Authorization": "Bearer ff" 
        }
        data={
          "group_id": event.group.id,
          "file": path,
          "name": f"{comic_id}.pdf"
                }
        logger.info(data)
        async with httpx.AsyncClient(timeout=None,headers=header) as client:
            r = await client.post(url,json=data)
            print(r.json())
    async def wait_and_delete_file(file_path, interval=60):
        for _ in range(10):
            try:
                shutil.os.remove(file_path)
                logger.info(f"文件 {file_path} 已成功删除")
                return
            except PermissionError:
                logger.warning(f"文件 {file_path} 被占用，等待重试...")
                await asyncio.sleep(interval)
            except FileNotFoundError:
                logger.warning(f"文件 {file_path} 已不存在")
                return
            except Exception as e:
                logger.error(f"删除文件时出现错误: {e}")
                return

