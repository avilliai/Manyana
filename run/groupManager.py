# -*- coding:utf-8 -*-
import datetime
import json
import os.path
import random
import re
import shutil
import urllib
from asyncio import sleep

import httpx
import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models.events import BotInvitedJoinGroupRequestEvent, NewFriendRequestEvent, MemberJoinRequestEvent, \
    MemberHonorChangeEvent, MemberCardChangeEvent, BotMuteEvent, MemberSpecialTitleChangeEvent, BotJoinGroupEvent, \
    MemberJoinEvent

from plugins.setuModerate import setuModerate
from plugins.vitsGenerate import voiceGenerate
from plugins.wReply.superDict import importDict


def main(bot,config,moderateKey,logger):
    # 读取设置
    global moderateK
    moderateK=moderateKey
    logger.info("读取群管设置")
    with open('config/welcome.yaml', 'r', encoding='utf-8') as f:
        welcome = yaml.load(f.read(), Loader=yaml.FullLoader)
    memberJoinWelcome=welcome.get("memberJoin")
    sendTemp = welcome.get("sendTemp")
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    global ModerateApiKeys
    ModerateApiKeys=result.get("moderate").get('apiKeys')
    global mainGroup
    mainGroup=int(config.get("mainGroup"))
    global banWords
    banWords=result.get("moderate").get("banWords")
    #读取用户数据
    logger.info("读取用户数据")
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    global userdict
    userdict = data
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    GroupSensor = result1.get("GroupSensor")
    autoallowFriend=result1.get("autoallowFriend")
    global qiandaoT
    qiandaoT=result1.get("signTimes")

    helpUser=result1.get("chatGLM").get("helpUser")

    global superUser
    superUser = []
    for i in userdict.keys():
        data = userdict.get(i)
        times = int(str(data.get('sts')))
        if times > 98:
            superUser.append(str(i))


    global blackList
    blackList= result.get("banUser")
    global blGroups
    blGroups= result.get("banGroups")


    global blackListID
    blackListID=[]

    global master
    master=int(config.get('master'))
    botName=config.get("botName")

    moderate=result.get("moderate")

    global threshold
    threshold=moderate.get("threshold")


    global severGroups
    severGroups=moderate.get("groups")
    global banTime
    banTime=moderate.get("banTime")

    @bot.on(BotInvitedJoinGroupRequestEvent)
    async def checkAllowGroup(event: BotInvitedJoinGroupRequestEvent):
        logger.info("接收来自 " + str(event.from_id) + " 的加群邀请")
        if GroupSensor == True:
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                result23 = yaml.load(f.read(), Loader=yaml.FullLoader)
            youquan = result23.get("trustGroups")
            if event.group_id in youquan:
                logger.info("同意")
                al = '同意'
                sdf = "请先向目标群群员确认是否愿意接受bot加群"
                await bot.send_friend_message(event.from_id, sdf)
                await bot.send_friend_message(event.from_id, "40秒后自动同意")
                await sleep(40)
                await bot.allow(event)
            else:
                logger.info("拒绝")
                al = "拒绝"
                await bot.send_friend_message(event.from_id, "该群无授权，请联系master" + str(master))
        else:
            if str(event.from_id) in userdict.keys():
                if int(userdict.get(str(event.from_id)).get("sts")) > qiandaoT:
                    if event.group_id in blGroups:
                        await bot.send_friend_message(event.from_id, "该群在黑名单内.\n解除拉黑请前往本bot用户群" + str(
                            mainGroup) + "在群内发送\n/blgroup remove 群号")
                        return
                    logger.info("同意")
                    al = '同意'
                    sdf = "请先向目标群群员确认是否愿意接受bot加群"
                    await bot.send_friend_message(event.from_id, sdf)
                    await bot.send_friend_message(event.from_id, "40秒后自动同意")
                    await sleep(40)
                    await bot.allow(event)
                else:
                    logger.info("签到天数不够，拒绝")
                    al = '拒绝'
                    await bot.send_friend_message(event.from_id, "群内签到天数不够呢，再签到(群内)几天再来试试吧。\n也可前往用户群" + str(
                        mainGroup) + " 获取授权\n在该群内发送:\n授权#你的QQ")
            else:
                logger.info("非用户，拒绝")
                al = '拒绝'
                await bot.send_friend_message(event.from_id, "无用户签到记录，请在任意bot共同群聊内发送 签到 达到三天以上\n也可前往用户群" + str(
                    mainGroup) + " 获取授权\n在该群内发送:\n授权#你的QQ")
        await bot.send_friend_message(master, '有新的加群申请\n来自：' + str(event.from_id) + '\n目标群：' + str(
            event.group_id) + '\n昵称：' + event.nick + '\n状态：' + al)
    @bot.on(MemberJoinEvent)
    async def MemberJoinHelper(event:MemberJoinEvent):
        if random.choice(memberJoinWelcome)==1:
            return
        await bot.send_group_message(event.member.group.id,(At(event.member.id),random.choice(memberJoinWelcome).replace("botName",botName).replace(r"\n","\n")))
        try:
            await bot.send_temp_message(event.member.id,random.choice(sendTemp).replace("botName",botName).replace(r"\n","\n"))
        except:
            try:
                await bot.send_friend_message(event.member.id,random.choice(sendTemp).replace("botName",botName).replace(r"\n","\n"))
            except:

                logger.error("向新入群成员"+str(event.member.id)+"发送消息失败")

    @bot.on(BotJoinGroupEvent)
    async def botJoin(event:BotJoinGroupEvent):
        await bot.send_group_message(event.group.id,"已加入服务群聊....")
        await bot.send_group_message(event.group.id,"发送 @bot 帮助 以获取功能列表\n项目地址：https://github.com/avilliai/Manyana\n喜欢bot的话可以给个star哦(≧∇≦)ﾉ")
        if helpUser:
            await bot.send_group_message(event.group.id, ("近期支持了ChatGLM，更智能的ai聊天。\n您可以自行设置apiKey，随后可在本群启用\n(注册送的18大概够用半年)\n==============\n1、注册并登录https://open.bigmodel.cn/overview\n2、点击图2中内容，复制完整apiKey.\n3、在群内或者私聊发送\n设置密钥#apiKey\n\n(群内发送则全群可用，私聊发送则仅个人使用)",Image(path="data/fonts/1.jpg"),Image(path="data/fonts/2.jpg")))
        path="../data/autoReply/voiceReply/joinGroup.wav"
        ok=os.path.exists(path)
        if ok:
            await bot.send_group_message(event.group.id,Voice(path=path[3:]))
        else:
            data={'text':"[JA]みなさん、こんにちは、私はこのグループのメンバーになりました、将来もっとアドバイスしてください![JA]","out":path}
            await voiceGenerate(data)
            await bot.send_group_message(event.group.id,Voice(path=path[3:]))
        #await bot.send_group_message(event.group.id,"发送 帮助 获取功能列表哦")



    @bot.on(Startup)
    async def updateData(event: Startup):
        while True:
            await sleep(60)
            # 读取用户数据
            logger.info("更新数据")
            global moderateK
            moderateK = moderateKey
            #logger.info("读取群管设置")
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)

            global ModerateApiKeys
            ModerateApiKeys = result.get("moderate").get('apiKeys')
            global mainGroup
            mainGroup = int(config.get("mainGroup"))
            global banWords
            banWords = result.get("moderate").get("banWords")
            # 读取用户数据
            #logger.info("读取用户数据")
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            global userdict
            userdict = data
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
            global qiandaoT
            qiandaoT = result1.get("signTimes")

            global superUser
            superUser = []
            for i in userdict.keys():
                data = userdict.get(i)
                times = int(str(data.get('sts')))
                if times > 98:
                    superUser.append(str(i))

            global blackList
            blackList = result.get("banUser")
            global blGroups
            blGroups = result.get("banGroups")

            global blackListID
            blackListID = []

            global master
            master = int(config.get('master'))

            moderate = result.get("moderate")

            global threshold
            threshold = moderate.get("threshold")

            global severGroups
            severGroups = moderate.get("groups")
            global banTime
            banTime = moderate.get("banTime")



    @bot.on(NewFriendRequestEvent)
    async def allowStranger(event: NewFriendRequestEvent):
        logger.info("新的好友申请，来自"+str(event.from_id))
        if str(event.from_id) in userdict.keys() or event.group_id==mainGroup or autoallowFriend==True:
            logger.info("有用户记录，同意")
            al='同意'
            await bot.allow(event)
            await sleep(5)
            await bot.send_friend_message(event.from_id,"你好ヾ(≧▽≦*)o，bot项目地址：https://github.com/avilliai/Manyana\n觉得还不错的话可以点个star哦")
            await bot.send_friend_message(event.from_id, "群内发送 @bot 帮助 获取功能列表")
            await bot.send_friend_message(event.from_id,"本bot用户群"+str(mainGroup))
            if helpUser:
                await bot.send_friend_message(event.from_id,("近期支持了ChatGLM，更智能的ai聊天。\n您可以自行设置apiKey\n(注册送的18大概够用半年)\n==============\n1、注册并登录https://open.bigmodel.cn/overview\n2、点击图2中内容，复制完整apiKey.\n3、在群内或者私聊发送\n设置密钥#apiKey\n\n(群内发送则全群可用，私聊发送则仅个人使用)",Image(path="data/fonts/1.jpg"),Image(path="data/fonts/2.jpg")))

        else:
            logger.info("无用户记录，拒绝")
            al='拒绝'
        await bot.send_friend_message(master,'有新的好友申请\n来自：'+str(event.from_id)+'\n来自群：'+str(event.group_id)+'\n昵称：'+event.nick+'\n状态：'+al)



    @bot.on(MemberJoinRequestEvent)
    async def allowStrangerInvite(event: MemberJoinRequestEvent):
        logger.info("有新群员加群申请")
        if event.from_id in blackList:
            await bot.send_group_message(event.group_id,"有新的入群请求，存在bot黑名单记录")
        else:
            await bot.send_group_message(event.group_id,'有新的入群请求.....管理员快去看看吧\nQQ：'+str(event.from_id)+'\n昵称：'+event.nick+'\nextra:：'+event.message)

    @bot.on(MemberSpecialTitleChangeEvent)
    async def honorChange(event: MemberSpecialTitleChangeEvent):
        logger.info("群员称号改变")
        await bot.send_group_message(event.member.group.id, str(event.member.member_name) + '获得了称号：' + str(event.current))

    @bot.on(MemberCardChangeEvent)
    async def nameChange(event: MemberCardChangeEvent):
        if len(event.current) > 0:
            logger.info("群员昵称改变")
            if event.origin=="" or event.origin==None:
                return
            else:
                await bot.send_group_message(event.member.group.id,
                                             event.origin + ' 的昵称改成了 ' + event.current + ' \n警惕新型皮套诈骗')


    @bot.on(BotMuteEvent)
    async def BanAndBlackList(event: BotMuteEvent):
        logger.info("bot被禁言，操作者"+str(event.operator.id))
        global blackList
        global blGroups
        if event.operator.group.id in blGroups:
            logger.info("已有黑名单群" + str(event.operator.group.id))
        else:
            blGroups.append(event.operator.group.id)

        if event.operator.id in blackList:
            logger.info("已有黑名单用户" + str(event.operator.id))
        else:
            blackList.append(event.operator.id)

        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
        result["banUser"]=blackList
        result["banGroups"]=blGroups
        with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(result, file, allow_unicode=True)
        await bot.send_friend_message(master,'bot在群:\n'+str(event.operator.group.name)+str(event.operator.group.id)+'\n被禁言'+str(event.duration_seconds)+'秒\n操作者id：'+str(event.operator.id)+'\nname:('+str(event.operator.member_name)+')\n已退群并增加不良记录')
        await bot.quit(event.operator.group.id)
        logger.info("已退出群 "+str(event.operator.group.id)+" 并拉黑")

    @bot.on(FriendMessage)
    async def quiteG(event:FriendMessage):
        if str(event.message_chain).startswith("退群#") and str(event.sender.id)==str(master):
            dataG=str(event.message_chain).split("#")[1]
            try:
                await bot.quit(int(dataG))
                logger.info("退出："+str(dataG))
                await bot.send_friend_message(int(master),"已退出: "+str(dataG))
            except:
                logger.warning("不正确的群号")

    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        global banWords
        if str(event.group.id) in banWords.keys():
            group=str(event.sender.group.id)
            try:
                banw=banWords.get(group)

                for i in banw:
                    if i in str(event.message_chain) and i!="":
                        id = event.message_chain.message_id
                        logger.info("获取到违禁词列表" + str(banw))
                        try:
                            await bot.recall(id)
                            logger.info("撤回违禁消息"+str(event.message_chain))
                            await bot.send(event,"检测到违禁词"+i+"，撤回")
                        except:
                            logger.error("关键词撤回失败！")
                        try:
                            await bot.mute(target=event.sender.group.id, member_id=event.sender.id, time=banTime)
                            await bot.send(event, "检测到违禁词" + i + "，禁言")
                        except:
                            logger.error("禁言失败，权限可能过低")

            except:
                pass
    @bot.on(GroupMessage)
    async def checkBanWords(event:GroupMessage):
        global banWords
        if At(bot.qq) in event.message_chain and "违禁词" in str(event.message_chain) and "查" in str(event.message_chain):
            group = str(event.sender.group.id)
            banw = str(banWords.get(group)).replace(",",",\n")
            await bot.send(event,"本群违禁词列表如下：\n"+banw)

    @bot.on(GroupMessage)
    async def addBanWord(event:GroupMessage):
        global banWords
        if (str(event.sender.permission)!="Permission.Member" or str(event.sender.id)==str(master)) and "添加违禁词" in str(event.message_chain):
            msg = "".join(map(str, event.message_chain[Plain]))
            # 匹配指令
            m = re.match(r'^添加违禁词\s*(.*)\s*$', msg.strip())
            if m:
                aimWord = m.group(1)
                if str(event.sender.group.id) in banWords:
                    banw=banWords.get(str(event.sender.group.id))
                    banw.append(aimWord)
                    banWords[str(event.sender.group.id)]=[aimWord]
                else:
                    banWords[str(event.sender.group.id)]=[aimWord]
                with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                    result = yaml.load(f.read(), Loader=yaml.FullLoader)
                moderate=result.get("moderate")

                moderate["banWords"]=banWords
                result["moderate"]=moderate
                with open('config/autoSettings.yaml', 'w',encoding="utf-8") as file:
                    yaml.dump(result, file, allow_unicode=True)
                await bot.send(event,"已添加违禁词："+aimWord)
    @bot.on(GroupMessage)
    async def removeBanWord(event:GroupMessage):
        global banWords
        if (str(event.sender.permission) != "Permission.Member" or str(event.sender.id) == str(
                master)) and "删除违禁词" in str(event.message_chain):
            msg = "".join(map(str, event.message_chain[Plain]))
            # 匹配指令
            m = re.match(r'^删除违禁词\s*(.*)\s*$', msg.strip())
            if m:
                aimWord = m.group(1)
                try:
                    newData=banWords.get(str(event.sender.group.id)).remove(aimWord)
                    banWords[str(event.sender.group.id)]==newData
                    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                        result = yaml.load(f.read(), Loader=yaml.FullLoader)
                    moderate = result.get("moderate")
                    moderate["banWords"] = banWords
                    result["moderate"] = moderate
                    with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(result, file, allow_unicode=True)

                    await bot.send(event,"已移除违禁词："+aimWord)
                except:
                    await bot.send(event, "没有已添加的违禁词：" + aimWord)

    @bot.on(GroupMessage)
    async def geturla(event:GroupMessage):
        global severGroups
        if str(event.group.id) in ModerateApiKeys:
            if (str(event.group.permission)!=str('Permission.Member')) and event.message_chain.count(Image) and str(event.group.id) in severGroups :
                lst_img = event.message_chain.get(Image)
                try:
                    moderateK=ModerateApiKeys.get(str(event.group.id))
                except:
                    logger.warning(str(event.group.id) + " 开启色图审核失败，未配置apiKey或apiKey已失效")
                    await bot.send(event, "调用失败，公共apiKey已耗尽本月使用限额或本群配置apiKey已失效")
                    await bot.send(event,
                                   "请在https://www.moderatecontent.com/注册并获取apiKey(不要用QQ邮箱)\n随后群内发送如下指令\n设置审核密钥[apiKey]\n以开启本群审核功能\n例如\n设置审核密钥207b10178c64089dvzv90ebfcd7f865d97a")
                    return
                for i in lst_img:
                    url=i.url
                    logger.info("图片审核:url:" + url+" key:"+moderateK)
                    try:
                        rate=await setuModerate(url,moderateK)
                    except:
                        logger.error("涩图审核失败，可能是图片太大，也可能是(小概率)api-key达到本月调用次数限制，尝试注册新账号更新新的api-key以解决")
                        return
                    logger.info("图片审核:结果:" + str(rate))
                    threshold=severGroups.get(str(event.group.id))
                    if int(rate)>threshold:
                        await bot.send(event, "检测到图片违规\npredictions-adult:" + str(rate))
                        try:
                            await bot.recall(event.message_chain.message_id)
                        except:
                            logger.error("撤回图片失败")
                        try:
                            await bot.mute(target=event.sender.group.id, member_id=event.sender.id, time=banTime)
                        except:
                            logger.error("禁言失败，权限可能过低")
                        return
    @bot.on(GroupMessage)
    async def geturla(event:GroupMessage):
        global severGroups
        if  event.message_chain.count(Image)==1 and "ping" in str(event.message_chain):
            lst_img = event.message_chain.get(Image)
            url = lst_img[0].url
            logger.info("图片审核:url:" + url)

            try:
                rate = await setuModerate(url, moderateK)
            except:
                logger.error("涩图审核失败，可能是图片太大，也可能是(小概率)api-key达到本月调用次数限制，尝试注册新账号更新新的api-key以解决")
                await bot.send(event,"涩图审核失败，可能是图片太大，也可能是公共api-key达到本月调用次数限制，尝试为本群配置单独的api-key以解决")
                await bot.send(event,"1、请在https://www.moderatecontent.com/注册并获取apiKey(不要用QQ邮箱)\n2、随后群内发送\n设置审核密钥[apiKey]\n以开启本群审核功能\n3、例如\n设置审核密钥207b10178c64089dvzv90ebfcd7f865d97a")

                return
            logger.info("图片审核:结果:" + str(rate))
            await bot.send(event, "图片检测结果：\npredictions-adult:" + str(rate))

    @bot.on(GroupMessage)
    async def addKeys(event: GroupMessage):
        global severGroups
        global ModerateApiKeys
        if "设置审核密钥" in str(event.message_chain):
            a = str(event.message_chain).split("设置审核密钥")[1]
            if event.sender.id==int(master):
                a=moderateK

            logger.info("测试密钥:" + a)

            try:
                url='https://www.moderatecontent.com/img/sample_anime_2.jpg'
                logger.info("图片审核:url:" + url + " key:" + moderateK)
                rate = await setuModerate(url, a)
            except:
                logger.error("无效的apiKey或图片太大")
                await bot.send(event, "涩图审核失败，可能是图片太大，也可能是api-key无效\n尝试注册新账号https://www.moderatecontent.com/获取新的api-key以解决\n指令：设置审核密钥[apiKey]\n示例如下：\n设置审核密钥2f4tga2tarafa4hjohljghvbngnf58")
                return
            logger.info("图片审核:结果:" + str(rate))
            ModerateApiKeys[str(event.group.id)]=a
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            result["moderate"]["apiKeys"]=ModerateApiKeys
            with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(result, file, allow_unicode=True)
            await bot.send(event, "设置apiKey成功")
    @bot.on(GroupMessage)
    async def setConfiga(event:GroupMessage):
        global threshold
        global severGroups
        if 1==1:
            if str(event.message_chain).startswith("/阈值") and (str(event.sender.permission)!="Permission.Member" or event.sender.id==master) :
                if str(event.group.id) in ModerateApiKeys:
                    temp=int(str(event.message_chain)[3:])
                    if temp>100 or temp<0:
                        await bot.send(event,"设置阈值不合法")
                    else:
                        try:
                            threshold=temp
                            severGroups[str(event.group.id)] = temp
                            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                                result = yaml.load(f.read(), Loader=yaml.FullLoader)
                            moderate = result.get("moderate")
                            moderate["groups"] = severGroups
                            result["moderate"] = moderate
                            with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                                yaml.dump(result, file, allow_unicode=True)

                            await bot.send(event,"成功修改撤回阈值为"+str(temp))
                        except:
                            await bot.send(event,"阈值设置出错，请进入config.json中手动设置threshold值")
                else:
                    logger.warning(str(event.group.id)+" 开启色图审核失败，未配置apiKey")
                    await bot.send(event,"公共apiKey达到每月调用次数限制，本群未配置apiKey,无法开启此功能")
                    await bot.send(event,"1、请在https://www.moderatecontent.com/注册并获取apiKey(不要用QQ邮箱)\n2、随后群内发送\n设置审核密钥[apiKey]\n以开启本群审核功能\n3、例如\n设置审核密钥207b10178c64089dvzv90ebfcd7f865d97a")

        if (str(event.sender.permission)!="Permission.Member"  or event.sender.id==master )and str(event.message_chain)=="/moderate":
            if str(event.group.id) in ModerateApiKeys:
                if str(event.group.id) in severGroups:
                    logger.info("群:"+str(event.group.id)+" 关闭了审核")
                    severGroups.pop(str(event.group.id))
                    await bot.send(event,"关闭审核")
                else:
                    logger.info("群:" + str(event.group.id) + " 开启了审核")
                    severGroups[str(event.group.id)]=40
                    await bot.send(event,"开启审核")
                with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                    result = yaml.load(f.read(), Loader=yaml.FullLoader)
                moderate = result.get("moderate")
                moderate["groups"] = severGroups
                result["moderate"] = moderate
                with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(result, file, allow_unicode=True)
                await bot.send(event, "ok")
            else:
                logger.warning(str(event.group.id) + " 开启色图审核失败，未配置apiKey")
                await bot.send(event, "公共apiKey达到每月调用次数限制")
                await bot.send(event,"开启色图审核失败，未配置本群apiKey")
                await bot.send(event,"1、请在https://www.moderatecontent.com/注册并获取apiKey(不要用QQ邮箱)\n2、随后群内发送\n设置审核密钥[apiKey]\n以开启本群审核功能\n3、例如\n设置审核密钥207b10178c64089dvzv90ebfcd7f865d97a")

    @bot.on(GroupMessage)
    async def exitBadGroup(event:GroupMessage):
        ls=["你妈","傻逼","艹逼","你妈","死你","垃圾","nm","狗东西","废物","低能"]
        if At(bot.qq) in event.message_chain:
            for i in ls:
                if i in str(event.message_chain):
                    try:
                        await bot.mute(target=event.sender.group.id, member_id=event.sender.id, time=banTime)
                        return
                    except:
                        logger.error("禁言失败，权限可能过低")
                        logger.warn("遭到："+str(event.sender.id)+" 的辱骂")
                        await bot.send_friend_message(master,"遭到："+str(event.sender.id)+" 的辱骂\n群号："+str(event.group.id)+"\n内容："+str(event.message_chain)+"\n可使用 退群#群号 操作bot退出该群")
                        #await bot.quit(event.group.id)
                        global blackList
                        global blGroups
                        if event.group.id in blGroups:
                            logger.info("已有黑名单群"+str(event.sender.group))
                        else:
                            blGroups.append(event.group.id)

                        if event.sender.id in blackList:
                            logger.info("已有黑名单用户"+str(event.sender.id))
                        else:
                            blackList.append(event.sender.id)

                        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                            result = yaml.load(f.read(), Loader=yaml.FullLoader)
                        result["banUser"] = blackList
                        result["banGroups"] = blGroups
                        with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(result, file, allow_unicode=True)
                        return

    @bot.on(GroupMessage)
    async def removeBl(event: GroupMessage):
        global superUser
        if event.sender.id == master or event.sender.id in superUser:
            global blackList
            if str(event.message_chain).startswith("/bl add ") or str(event.message_chain).startswith("添加黑名单用户 "):
                groupId = int(str(event.message_chain).split(" ")[-1])
                if groupId not in blackList:
                    blackList.append(groupId)
                    logger.info("成功添加黑名单用户" + str(groupId))
                    await bot.send(event, "成功添加黑名单用户" + str(groupId))

                    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                        result = yaml.load(f.read(), Loader=yaml.FullLoader)
                    logger.info("当前黑名单"+str(blackList))
                    result["banUser"] = blackList
                    with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(result, file, allow_unicode=True)

                else:
                    await bot.send(event,"该用户已被拉黑")
    @bot.on(GroupMessage)
    async def removeBl(event:GroupMessage):
        if event.sender.id == master or event.sender.id in superUser or event.group.id==mainGroup:
            global blackList
            global blGroups
            if str(event.message_chain).startswith("/blgroup remove ") or str(event.message_chain).startswith("移除黑名单群 "):
                try:
                    groupId=int(str(event.message_chain).split(" ")[-1])
                    blGroups.remove(groupId)
                    logger.info("成功移除黑名单群"+str(groupId))
                    await bot.send(event,"成功移除黑名单群"+str(groupId))
                    logger.info("当前黑名单群"+str(blGroups))

                    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                        result11 = yaml.load(f.read(), Loader=yaml.FullLoader)
                    result11["banGroups"] = blGroups
                    with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(result11, file, allow_unicode=True)
                    return
                except:
                    logger.error("移除失败，该群不在黑名单中")
                    await bot.send(event,"移除失败，该群不在黑名单中")
            if str(event.message_chain).startswith("/bl remove ") or str(event.message_chain).startswith(" 移除黑名单用户"):
                try:
                    groupId=int(str(event.message_chain).split(" ")[-1])
                    blackList.remove(groupId)
                    logger.info("成功移除黑名单用户"+str(groupId))
                    await bot.send(event,"成功移除黑名单用户"+str(groupId))
                    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                        result = yaml.load(f.read(), Loader=yaml.FullLoader)
                    result["banUser"] = blackList
                    with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(result, file, allow_unicode=True)
                    return
                except:
                    logger.error("移除失败，该用户不在黑名单中")
                    await bot.send(event,"移除失败，该用户不在黑名单中")

