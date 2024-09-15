# -*- coding: utf-8 -*-
import os
from typing import Dict

import asyncio
import datetime
import json
import random

from asyncio import sleep

import yaml
from fuzzywuzzy import process
from mirai import FriendMessage, GroupMessage, At, Plain,MessageChain,Startup
from mirai import Image, Voice
from mirai.models import ForwardMessageNode, Forward
from plugins.wReply.wReplyOpeator import addRep, loadAllDict, getRep, compare2messagechain

from plugins.wReply.MessageConvert import EventMessageConvert



async def mesChainConstructer(source):
    bottleConstruct = []
    if "text" in str(source) or "image" in str(source):
        for i in source:
            if "text" in i:
                bottleConstruct.append(Plain(i["text"]))
            elif "image" in i:
                bottleConstruct.append(Image(path=i["image"]))
        return bottleConstruct
    else:
        return json.loads(source)  # 对旧数据实现兼容


def main(bot,logger):
    logger.info("启动自定义词库")
    with open('config.json', 'r', encoding='utf-8') as f:
        configYaml = yaml.load(f.read(), Loader=yaml.FullLoader)
        master=configYaml.get("master")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    wReply=result.get("wReply")
    global publicDict
    publicDict=loadAllDict()
    #操作进程监听
    global operateProcess
    operateProcess={}
    global userdict
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        userdict = yaml.load(file, Loader=yaml.FullLoader)
    colorfulCharacterList = os.listdir("data/colorfulAnimeCharacter")
    global repeatData
    repeatData={333:{"times":0,"mes":"你好","simplemes":"你好"}}
    global repeatLock
    repeatLock={1111: datetime.datetime.now()} #复读冷却锁
    #开始添加
    @bot.on(GroupMessage)
    async def startAddRep(event: GroupMessage):
        global operateProcess,userdict
        if wReply.get("editPermission")!=0:   #权限限制，为0则为开放授权
            if str(event.sender.id) in userdict:
                if int(userdict.get(str(event.sender.id)).get('sts'))<wReply.get("editPermission"):
                    return
            else:
                return
        if str(event.message_chain)=="开始添加":
            await sleep(0.1)
            operateProcess[event.sender.id]={"status":"startadd","time":datetime.datetime.now(),"operateId":str(event.group.id)}
        elif str(event.message_chain).startswith("群词库添加") and event.sender.id==int(master):
            await sleep(0.1)
            operateProcess[event.sender.id]={"status":"startadd","time":datetime.datetime.now(),"operateId":str(event.message_chain).replace("群词库添加","")}
        elif str(event.message_chain)=="*开始添加":
            if wReply.get("golbalLexiconRequire")!=0:   #权限限制，为0则为开放授权
                if str(event.sender.id) in userdict:
                    if int(userdict.get(str(event.sender.id)).get('sts'))<wReply.get("golbalLexiconRequire"):
                        return
                else:
                    return
            await bot.send(event,"此操作将为所有群添加回复")
            await sleep(0.1)
            operateProcess[event.sender.id] = {"status": "startadd", "time": datetime.datetime.now(),"operateId":"publicLexicon"}
        else:
            return
        await bot.send(event,"请发送关键词")
    @bot.on(GroupMessage)
    async def RecordKey(event: GroupMessage):
        global operateProcess,publicDict
        if event.sender.id in operateProcess:
            if operateProcess[event.sender.id]["status"]=="startadd":
                await sleep(0.1)
                operateProcess[event.sender.id]["status"]="adding"
                operateProcess[event.sender.id]["time"]=datetime.datetime.now()
                #operateProcess[event.sender.id]["key"] = str(event.message_chain)
                operateProcess[event.sender.id]["key"]=event.message_chain.json()
                if operateProcess[event.sender.id]["operateId"] in publicDict:
                    r = await getRep(publicDict.get(operateProcess[event.sender.id]["operateId"]),event.message_chain.json(),wReply.get("threshold"),wReply.get("mode"),wReply.get("inMaxLength"),wReply.get("inWeighting"))
                    #if str(event.message_chain) in publicDict.get(operateProcess[event.sender.id]["operateId"]):
                        #operateProcess[event.sender.id]["value"]=publicDict.get(operateProcess[event.sender.id]["operateId"]).get(str(event.message_chain))
                    if r!=None:
                        operateProcess[event.sender.id]["value"] = r[1]
                        logger.info("已存在关键词")
                await bot.send(event,"请发送回复，发送 over 以退出添加")
    @bot.on(GroupMessage)
    async def addValue(event: GroupMessage):
        global operateProcess,publicDict
        if event.sender.id in operateProcess:
            if operateProcess[event.sender.id]["status"]=="adding":
                if str(event.message_chain)=="over":
                    logger.info("退出添加，开始保存用户添加的所有回复")
                    publicDict=await addRep(operateProcess[event.sender.id]["key"],operateProcess[event.sender.id]["value"],operateProcess[event.sender.id]["operateId"])
                    await bot.send(event,"退出回复添加")
                    operateProcess.pop(event.sender.id)
                    return
                await sleep(0.1)
                newMes = await EventMessageConvert(event.message_chain)
                if "value" in operateProcess[event.sender.id]:
                    operateProcess[event.sender.id]["value"].append(newMes)
                else:
                    operateProcess[event.sender.id]["value"]=[newMes]
                await bot.send(event,"已记录回复")
                operateProcess[event.sender.id]["time"] = datetime.datetime.now()  #不要忘记刷新时间

    # 查询关键词对应回复
    @bot.on(GroupMessage)
    async def queryValue(event: GroupMessage):
        global operateProcess,userdict
        if wReply.get("editPermission")!=0:
            if str(event.sender.id) in userdict:
                if int(userdict.get(str(event.sender.id)).get('sts'))<wReply.get("editPermission"):
                    return
            else:
                return
        if str(event.message_chain)=="查回复":
            await sleep(1)
            operateProcess[event.sender.id]={"status":"query","operateId":str(event.group.id),"time":datetime.datetime.now()}
        elif str(event.message_chain)=="*查回复":
            await sleep(1)
            operateProcess[event.sender.id]={"status":"query","operateId":"publicLexicon","time":datetime.datetime.now()}
        else:
            return
        logger.info("查询回复目标")
        await bot.send(event, "请发送要查询的目标")
    @bot.on(GroupMessage)
    async def sendQueryResults(event: GroupMessage):
        global operateProcess,publicDict
        if event.sender.id in operateProcess:
            if str(event.message_chain).endswith("查回复"):
                return
            if operateProcess[event.sender.id]["status"]=="query":
                r = await getRep(publicDict.get(operateProcess[event.sender.id]["operateId"]), str(event.message_chain.json()),wReply.get("threshold"),wReply.get("mode"),wReply.get("inMaxLength"),wReply.get("inWeighting"))
                b1=[]
                if r != None:
                    index=0
                    for i in r[1]:
                        mesc = await mesChainConstructer(i)
                        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([f"编号{index}👇"])))
                        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain(mesc)))
                        index+=1
                    await bot.send(event, Forward(node_list=b1))
                    await bot.send(event,f"发送 删除#编号 以删除指定回复\n发送 删除关键字 以删除全部回复")
                    operateProcess[event.sender.id]["status"] = "delete"
                    await sleep(0.1)
                    operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间
                    operateProcess[event.sender.id]["queryKey"] = r[0]
                else:
                    await bot.send(event,"无查询结果",True)
                    operateProcess.pop(event.sender.id)
                return
            if operateProcess[event.sender.id]["status"]=="delete":
                if str(event.message_chain).startswith("删除#"):
                    try:
                        index=int(str(event.message_chain).split("#")[1])
                        value=publicDict.get(operateProcess[event.sender.id]["operateId"]).get(operateProcess[event.sender.id]["queryKey"])
                        value.pop(index)
                        publicDict = await addRep(operateProcess[event.sender.id]["queryKey"],value,operateProcess[event.sender.id]["operateId"])
                        await bot.send(event,"已移除对应回复")
                        operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间
                    except:
                        logger.error("非法输入，索引必须是有效的数字")
                elif str(event.message_chain)=="删除关键字":
                    try:
                        publicDict[operateProcess[event.sender.id]["operateId"]].pop(operateProcess[event.sender.id]["queryKey"])
                        await bot.send(event,"已移除")
                        operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间
                        id=operateProcess[event.sender.id]["operateId"]
                        id = f"data/autoReply/lexicon/{id}.yaml"
                        with open(id, 'w', encoding="utf-8") as file:
                            yaml.dump(publicDict[operateProcess[event.sender.id]["operateId"]], file, allow_unicode=True)
                    except:
                        logger.error("非法输入，索引必须是有效的数字")

    @bot.on(GroupMessage)
    async def getReply(event: GroupMessage):
        global operateProcess, publicDict
        if event.sender.id in operateProcess:
            return
        if random.randint(0,100)>wReply.get("replyRate"):
            return
        if str(event.group.id) in publicDict:
            r=await getRep(publicDict.get(str(event.group.id)),str(event.message_chain.json()),wReply.get("threshold"),wReply.get("mode"),wReply.get("inMaxLength"),wReply.get("inWeighting"))
        else:
            r = await getRep(publicDict.get("publicLexicon"), str(event.message_chain.json()),wReply.get("threshold"),wReply.get("mode"),wReply.get("inMaxLength"),wReply.get("inWeighting"))
        if r != None:
            logger.info(f"词库匹配成功")
            if random.randint(0, 100) < wReply.get("colorfulCharacter"):
                logger.info("本次使用彩色小人替代匹配回复")
                c = random.choice(colorfulCharacterList)
                await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                return
            mesc=await mesChainConstructer(random.choice(r[1]))
            await bot.send(event, MessageChain(mesc))
    @bot.on(Startup)
    async def checkTimeOut(event: Startup):
        global operateProcess
        while True:
            operateProcess=await check_and_pop_expired_keys(operateProcess)
            await asyncio.sleep(30)
    async def check_and_pop_expired_keys(data):
        keys_to_pop = []
        now = datetime.datetime.now()
        minutes = datetime.timedelta(seconds=wReply.get("timeout"))
        for key, value in data.items():
            time_diff = now - value.get('time', now)  # 如果 'time' 不存在，则使用 now，避免错误
            if time_diff > minutes:
                keys_to_pop.append(key)

        for key in keys_to_pop:
            data.pop(key, None)
            logger.info(f"词库操作超时释出：{key}")
        return data

    @bot.on(Startup)
    async def upDate(event: Startup):
        while True:
            await sleep(60)
            global userdict
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                userdict = yaml.load(file, Loader=yaml.FullLoader)
    #用以实现复读
    @bot.on(GroupMessage)
    async def repeatFunc(event: GroupMessage):
        global repeatData,repeatLock
        if event.group.id in repeatData:
            if str(event.message_chain)==repeatData[event.group.id]["simplemes"]: #最新的消息链同记录的最后一个消息链相同
                score=await compare2messagechain(event.message_chain.json(),repeatData[event.group.id]["mes"])
                if score>90:
                    if repeatData[event.group.id]["times"]==2: #3次，进入复读
                        d=await mesChainConstructer(repeatData[event.group.id]["sefmeschain"])
                        await bot.send(event,MessageChain(d)) #复读一次
                        logger.info(f"复读一次{str(event.message_chain)}")
                        repeatData.pop(event.group.id)  # 终止此次复读任务
                        repeatLock[event.group.id]=datetime.datetime.now() #进入cd时间
                        logger.info(f"{event.group.id} 进入cd冷却60s")
                    else:
                        repeatData[event.group.id]["times"]=repeatData[event.group.id]["times"]+1 #加一次
                else:
                    repeatData.pop(event.group.id)  # 终止此次复读任务
            else:
                repeatData.pop(event.group.id) #终止此次复读任务
        else:
            if event.group.id in repeatLock and datetime.datetime.now()-repeatLock[event.group.id]<datetime.timedelta(60): #时间锁
                return
            repeatData[event.group.id]={"times":1,"mes":event.message_chain.json(),"simplemes":str(event.message_chain),"sefmeschain":await EventMessageConvert(event.message_chain)}

