# -*- coding: utf-8 -*-
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

from plugins.wReply.wReplyOpeator import addRep, loadAllDict, getRep


def main(bot,logger):
    logger.info("启动自定义词库")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    global publicDict
    publicDict=loadAllDict()
    #操作进程监听
    global operateProcess
    operateProcess={}
    timeout = datetime.timedelta(minutes=3)  # 3分钟没有操作则超时

    #开始添加
    @bot.on(GroupMessage)
    async def startAddRep(event: GroupMessage):
        global operateProcess
        if str(event.message_chain)=="开始添加":
            await sleep(0.1)
            operateProcess[event.sender.id]={"status":"startadd","time":datetime.datetime.now(),"operateId":str(event.group.id)}
        elif str(event.message_chain)=="*开始添加":
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
                operateProcess[event.sender.id]["key"]=str(event.message_chain)
                if operateProcess[event.sender.id]["operateId"] in publicDict:
                    if str(event.message_chain) in publicDict.get(operateProcess[event.sender.id]["operateId"]):
                        operateProcess[event.sender.id]["value"]=publicDict.get(operateProcess[event.sender.id]["operateId"]).get(str(event.message_chain))
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
                if "value" in operateProcess[event.sender.id]:
                    operateProcess[event.sender.id]["value"].append(event.message_chain.json())
                else:
                    operateProcess[event.sender.id]["value"]=[event.message_chain.json()]
                await bot.send(event,"已记录回复")
                operateProcess[event.sender.id]["time"] = datetime.datetime.now()  #不要忘记刷新时间

    # 查询关键词对应回复
    @bot.on(GroupMessage)
    async def queryValue(event: GroupMessage):
        global operateProcess
        if str(event.message_chain)=="查回复":
            operateProcess[event.sender.id]={"status":"query","operateId":str(event.group.id),"time":datetime.datetime.now()}
        elif str(event.message_chain)=="*查回复":
            operateProcess[event.sender.id]={"status":"query","operateId":"publicLexicon","time":datetime.datetime.now()}
        else:
            return
        logger.info("查询回复目标")
        await bot.send(event, "请发送要查询的目标")
    @bot.on(GroupMessage)
    async def sendQueryResults(event: GroupMessage):
        global operateProcess,publicDict
        if event.sender.id in operateProcess:
            if operateProcess[event.sender.id]["status"]=="query":
                r = await getRep(publicDict.get(operateProcess[event.sender.id]["operateId"]), str(event.message_chain))
                b1=[]
                if r != None:
                    index=0
                    for i in r[1]:
                        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([f"编号{index}👇"])))
                        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain(json.loads(i))))
                        index+=1
                    await bot.send(event, Forward(node_list=b1))
                    await bot.send(event,f"发送 删除#编号 以删除指定回复\n发送 删除关键字 以删除全部回复")
                    operateProcess[event.sender.id]["status"] = "delete"
                    operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间
                    operateProcess[event.sender.id]["queryKey"] = r[0]
            if operateProcess[event.sender.id]["status"]=="delete":
                if str(event.message_chain).startswith("删除#"):
                    index=int(str(event.message_chain).split("#")[1])
                    value=publicDict.get(operateProcess[event.sender.id]["operateId"]).get(operateProcess[event.sender.id]["queryKey"])
                    value.pop(index)
                    publicDict = await addRep(operateProcess[event.sender.id]["queryKey"],value,operateProcess[event.sender.id]["operateId"])
                    await bot.send(event,"已移除对应回复")
                    operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间

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
        if str(event.group.id) in publicDict:
            r=await getRep(publicDict.get(str(event.group.id)),str(event.message_chain))
            if r!=None:
                logger.info(f"匹配到关键词|{str(event.message_chain)} {r[0]}")
                await bot.send(event,json.loads(random.choice(r[1])))
    @bot.on(Startup)
    async def checkTimeOut(event: Startup):
        global operateProcess
        while True:
            operateProcess=await check_and_pop_expired_keys(operateProcess)
            await asyncio.sleep(30)
    async def check_and_pop_expired_keys(data):
        keys_to_pop = []
        now = datetime.datetime.now()
        minutes = datetime.timedelta(seconds=60)
        for key, value in data.items():
            time_diff = now - value.get('time', now)  # 如果 'time' 不存在，则使用 now，避免错误
            if time_diff > minutes:
                keys_to_pop.append(key)

        for key in keys_to_pop:
            data.pop(key, None)
            logger.info(f"词库操作超时释出：{key}")
        return data