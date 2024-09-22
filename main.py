# -*- coding:utf-8 -*-
from itertools import repeat
from time import sleep

import asyncio
import datetime

import os
import random
import shutil
import sys

from asyncio import sleep as sleep1, exceptions

#下面的两行是launcher启动必要设置，勿动。
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mirai.models import ForwardMessageNode, Forward
import yaml
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage, Shutdown,MessageChain

from plugins.toolkits import newLogger,random_str,get_system_info
from run import aiReply, voiceReply, nudgeReply, wikiHelper, imgSearch, extraParts, wReply, groupManager, \
    musicShare, LiveMonitor, aronaapi, groupGames, musicpick, scheduledTasks, appCard, aiDraw, starRail, bangumi, \
    draftBottle


# 为了实现黑名单和群开关功能，我们将继承webSocketAdapter类
class MyWebSocketAdapter(WebSocketAdapter):
    def __init__(self, verify_key, host, port, result):
        super().__init__(verify_key=verify_key, host=host, port=port)
        self.result = result
    async def _recv(self, sync_id: str = '-1', timeout: int = 600) -> dict:
        """接收并解析 websocket 数据。"""
        timer = range(timeout) if timeout > 0 else repeat(0)
        for _ in timer:
            if self._recv_dict[sync_id]:
                data = self._recv_dict[sync_id].popleft()
                #print(data)
                if data.get('code', 0) != 0:
                    pass
                    #raise exceptions.ApiError(data)
                try:
                    if "messageChain" in data:
                        if data["sender"]["id"] in self.result["banuser"] or data["sender"]["group"]["id"] in self.result["botoff"]:
                            pass
                        else:
                            return data
                    else:
                        return data
                except:
                    return data
                # 如果没有对应同步 ID 的数据，则等待 websocket 数据
                # 目前存在问题：如果 mah 发回的数据不含 sync_id，
                # 这里就会无限循环……
                # 所以还是限制次数好了。
            await asyncio.sleep(0.1)
        raise TimeoutError(
            f'[WebSocket] mirai-api-http 响应超时，可能是由于调用出错。同步 ID：{sync_id}。'
        )
if __name__ == '__main__':
    if not os.path.exists("data/pictures/benzi"):
        os.mkdir("data/pictures/benzi")
    with open('config.json', 'r', encoding='utf-8') as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)

    config = data
    qq = int(config.get('botQQ'))
    key = str(config.get("vertify_key"))
    port = int(config.get("port"))
    global autoSettings
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        autoSettings = yaml.load(f.read(), Loader=yaml.FullLoader)
    bot = Mirai(qq, adapter=MyWebSocketAdapter(
        verify_key=key, host='localhost', port=port,result=autoSettings
    ))
    botName = config.get('botName')
    master = int(config.get('master'))
    # 芝士logger
    logger = newLogger()

    # 读取api列表
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = result.get("proxy")
    berturl = result.get("bert_colab")
    moderate = result.get("moderate")
    nasa_api = result.get("nasa_api")
    chatglm = result.get("chatGLM")

    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        resulta = yaml.load(f.read(), Loader=yaml.FullLoader)
    pandora = resulta.get("chatGLM").get("model")
    voicegg = resulta.get("语音功能设置").get("voicegenerate")
    logger.info("读取到apiKey列表")
    #用以实现拉黑和解黑

    @bot.on(GroupMessage)
    async def blManipulate(event: GroupMessage):
        if event.sender.id==master:
            global autoSettings
            if str(event.message_chain).startswith("/bl remove ") or str(event.message_chain).startswith("解黑 "):
                try:
                    userId = int(str(event.message_chain).split(" ")[-1])
                    autoSettings["banuser"].remove(userId)
                    logger.info("成功移除黑名单用户" + str(userId))
                    await bot.send(event, "成功移除黑名单用户" + str(userId))
                except:
                    logger.error("移除失败，该用户不在黑名单中")
                    await bot.send(event, "移除失败，该用户不在黑名单中")
            elif str(event.message_chain).startswith("/bl add ") or str(event.message_chain).startswith("拉黑 "):
                try:
                    userId = int(str(event.message_chain).split(" ")[-1])
                    if userId in autoSettings["banuser"]:
                        await bot.send(event,"该用户已被拉黑")
                        return
                    autoSettings["banuser"].append(userId)
                    logger.info("成功添加黑名单用户" + str(userId))
                    await bot.send(event, "成功添加黑名单用户" + str(userId))
                except:
                    logger.error("添加失败，不规范的指令格式")
                    await bot.send(event, "添加失败，不规范的指令格式")
            elif str(event.message_chain).startswith("/bot off ") or str(event.message_chain).startswith("关闭群 "):
                userId = int(str(event.message_chain).split(" ")[-1])
                if userId in autoSettings["botoff"]:
                    await bot.send(event,"bot已在该群关闭")
                    return
                autoSettings["botoff"].append(userId)
                logger.info(f"成功关闭了对群{str(userId)}的服务")
                await bot.send(event, f"成功关闭了对群{str(userId)}的服务")
            elif str(event.message_chain).startswith("/bot on ") or str(event.message_chain).startswith("开启群 "):
                try:
                    userId = int(str(event.message_chain).split(" ")[-1])
                    autoSettings["botoff"].remove(userId)
                    logger.info(f"成功开启了对群{str(userId)}的服务")
                    await bot.send(event, f"成功开启了对群{str(userId)}的服务")
                except:
                    logger.error("添加失败，不规范的指令格式")
                    await bot.send(event, "添加失败，不规范的指令格式")
            with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(autoSettings, file, allow_unicode=True)


    @bot.on(FriendMessage)
    async def blManipulate(event: FriendMessage):
        if event.sender.id == master:
            global autoSettings
            if str(event.message_chain).startswith("/bl remove ") or str(event.message_chain).startswith("解黑 "):
                try:
                    userId = int(str(event.message_chain).split(" ")[-1])
                    autoSettings["banuser"].remove(userId)
                    logger.info("成功移除黑名单用户" + str(userId))
                    await bot.send(event, "成功移除黑名单用户" + str(userId))
                except:
                    logger.error("移除失败，该用户不在黑名单中")
                    await bot.send(event, "移除失败，该用户不在黑名单中")
            elif str(event.message_chain).startswith("/bl add ") or str(event.message_chain).startswith("拉黑 "):
                try:
                    userId = int(str(event.message_chain).split(" ")[-1])
                    if userId in autoSettings["banuser"]:
                        await bot.send(event, "该用户已被拉黑")
                        return
                    autoSettings["banuser"].append(userId)
                    logger.info("成功添加黑名单用户" + str(userId))
                    await bot.send(event, "成功添加黑名单用户" + str(userId))
                except:
                    logger.error("添加失败，不规范的指令格式")
                    await bot.send(event, "添加失败，不规范的指令格式")
            elif str(event.message_chain).startswith("/bot off ") or str(event.message_chain).startswith("关闭群 "):
                userId = int(str(event.message_chain).split(" ")[-1])
                if userId in autoSettings["botoff"]:
                    await bot.send(event, "bot已在该群关闭")
                    return
                autoSettings["botoff"].append(userId)
                logger.info(f"成功关闭了对群{str(userId)}的服务")
                await bot.send(event, f"成功关闭了对群{str(userId)}的服务")
            elif str(event.message_chain).startswith("/bot on ") or str(event.message_chain).startswith("开启群 "):
                try:
                    userId = int(str(event.message_chain).split(" ")[-1])
                    autoSettings["botoff"].remove(userId)
                    logger.info(f"成功开启了对群{str(userId)}的服务")
                    await bot.send(event, f"成功开启了对群{str(userId)}的服务")
                except:
                    logger.error("添加失败，不规范的指令格式")
                    await bot.send(event, "添加失败，不规范的指令格式")
            with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(autoSettings, file, allow_unicode=True)

    @bot.on(GroupMessage)
    async def systemiiiiii(event: GroupMessage):
        if str(event.message_chain) == ".system" and event.sender.id == master:
            infof = get_system_info()
            await bot.send(event, infof)


    @bot.on(FriendMessage)
    async def systemiiiiii1(event: FriendMessage):
        if str(event.message_chain) == ".system" and event.sender.id == master:
            infof = get_system_info()
            await bot.send(event, infof)


    global notice
    notice = 0

    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller= yaml.load(f.read(), Loader=yaml.FullLoader)
    FordMesmenu=controller.get("bot自身设置").get("FordMesMenu")
    @bot.on(GroupMessage)
    async def unlockNotice(event: GroupMessage):
        global notice
        if str(event.message_chain) == "notice" and event.sender.id == master:
            await bot.send(event, "请发送要推送的消息")
            notice = 1
        if str(event.message_chain).startswith("/sub") or str(event.message_chain).startswith("/unsub"):
            await bot.send(event, "该指令可能已经失效\n请发送@" + str(botName) + "帮助\n以查看菜单3/B站动态推送v2")


    @bot.on(GroupMessage)
    async def sendNotice(event: GroupMessage):
        global notice
        if notice == 1 and event.sender.id == master:
            notice = 0
            asf = await bot.group_list()
            await bot.send(event, "收到，正在推送......")
            # print(asf.data)
            for i in asf.data:
                # print(i.id, i.name)
                await sleep1(random.randint(2, 10))
                logger.info("向群：" + i.name + " 推送公告")
                try:
                    if event.message_chain.count(Image):
                        await bot.send_group_message(int(i.id), event.message_chain)
                    else:
                        try:
                            await bot.send_group_message(int(i.id), (
                                    event.message_chain + "\n==============\n随机码：" + random_str()))
                        except:
                            await bot.send_group_message(int(i.id), event.message_chain)
                except:
                    logger.error("无效的群：" + str(i))
                    continue


    # 菜单
    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        if ('帮助' in str(event.message_chain) or '菜单' in str(event.message_chain) or "功能" in str(
                event.message_chain)) and At(bot.qq) in event.message_chain:
            logger.info("获取菜单")
            cmList=[]

            s = [Image(path='data/fonts/help1.jpg'), Image(path='data/fonts/help2.jpg'),
                 Image(path='data/fonts/help3.jpg'),Image(path="data/fonts/help4.jpg")]

            try:
                if not FordMesmenu:
                    raise Exception #你说得对，我实在懒得加判断了
                for i in s:
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(i))
                    cmList.append(b1)
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain('这是' + botName + '的功能列表\nヾ(≧▽≦*)o\n发送 pet 以查看制图功能列表\npetpet功能由https://github.com/Dituon/petpet提供'))
                cmList.append(b1)
                await bot.send(event, Forward(node_list=cmList))
            except Exception as e:
                for i in s:
                    await bot.send(event,i)
                await bot.send(event,'这是' + botName + '的功能列表\nヾ(≧▽≦*)o\n发送 pet 以查看制图功能列表\npetpet功能由https://github.com/Dituon/petpet提供')
    @bot.on(Startup)
    async def clearCache(event: Startup):

        logger.info("执行清理缓存操作")
        aimdir=["data/pictures/avatars","data/pictures/cache","data/pictures/new_sign_Image","data/voices"]
        for ib in aimdir:
            ls1 = os.listdir(ib)
            for i in ls1:
                try:
                    if i.endswith(".py"):
                        continue
                    if i.endswith("zYz.png"):
                        continue
                    os.remove(f"{ib}/" + i)
                except:
                    continue
        logger.info("清理缓存完成")
        logger.info("请定期执行launcher.exe的更新功能以获取最新版Manyana")

        asf = await bot.group_list()
        #print(asf.data)
        logger.info('已读取服务群聊:' + str(len(asf.data)) + '个')

        with open('data/userData.yaml', 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        global userdict
        userdict = data
        try:
            userCount = userdict.keys()
            logger.info('已读取有记录用户:' + str(len(userCount)) + '个')
            if os.path.exists("./temp"):
                shutil.copyfile('data/userData.yaml', 'temp/userData_back.yaml')
                shutil.copyfile('data/chatGLMData.yaml', 'temp/chatGLMData_back.yaml')
            else:
                os.mkdir("./temp")
                shutil.copyfile('data/userData.yaml', 'temp/userData_back.yaml')
                shutil.copyfile('data/chatGLMData.yaml', 'temp/chatGLMData_back.yaml')
            logger.info("已备份用户数据文件至temp文件夹下")
        except Exception as e:
            logger.error(e)
            logger.error("用户数据文件出错，自动使用备用文件替换")
            shutil.copyfile('temp/userData_back.yaml', 'data/userData.yaml')
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            userdict = data

        # 修改为你bot的名字
        logger.info('botName:' + botName + '     |     master:' + str(master))
        time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            await bot.send_friend_message(master, "本项目源码及启动器一键整合包完全免费，如果你是通过付费渠道获得的，那么恭喜你，你被骗了！")
            await bot.send_friend_message(master, time1 + '\n已读取服务群聊:' + str(len(asf.data)) + '个')
            await bot.send_friend_message(master, time1 + '\n已读取有记录用户:' + str(len(userCount)) + '个')
            await bot.send_friend_message(master, time1 + '\n功能已加载完毕，欢迎使用')
            await sleep1(10)
            await bot.send_friend_message(master, Image(path="data/fonts/master.jpg"))
        except Exception as e:
            logger.error(e)

    logger.info("当前语音合成模式：" + voicegg)


    def startVer():
        file_object = open("data/fonts/mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)


    @bot.on(Shutdown)
    async def efff(event: Shutdown):
        raise SystemExit()


    # current_dir = os.path.dirname(os.path.abspath(__file__))
    voiceReply.main(bot, master, logger)  # 语音生成

    aiReply.main(bot, master, logger)  # poe-api
    imgSearch.main(bot, result.get("sauceno-api"), result.get("proxy"), logger)
    try:
        from run import getcomic
        getcomic.main(bot,logger)
    except:
        logger.error("jmcomic功能无法启用，请使用更新脚本/更新bot代码 补全依赖")
        sleep(3)
    try:
        from run import youtube
        youtube.main(bot,logger,proxy)
    except:
        logger.warning("youtube功能无法启用(测试功能，无需在意)")
        sleep(3)
    nudgeReply.main(bot, master, logger, berturl, proxy)  # 戳一戳
    extraParts.main(bot, logger)  # 额外小功能
    wReply.main(bot,logger)
    wikiHelper.main(bot, logger)
    groupManager.main(bot, config, moderate, logger)
    musicShare.main(bot, master, botName, logger)
    LiveMonitor.main(bot,  logger)
    aronaapi.main(bot, logger)
    try:
        scheduledTasks.main(bot, logger)
    except Exception as e:
        logger.error(e)
        logger.error("致命错误！定时功能无法启用，请检查设备时区")
    try:
        from run import wordCloud
        wordCloud.main(bot, logger)
    except Exception as e:
        logger.error(e)
        logger.error("词云功能无法启用，请使用更新代码-补全依赖")
    groupGames.main(bot, logger)
    musicpick.main(bot, logger)
    appCard.main(bot, logger)
    aiDraw.main(bot, logger)
    starRail.main(bot, logger)
    bangumi.main(bot,logger)
    draftBottle.main(bot,logger) #芝士漂流瓶

    #gemini_ai.main(bot,logger,master)
    startVer()
    bot.run(asgi_server=None)
