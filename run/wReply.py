# -*- coding: utf-8 -*-
import asyncio
import datetime
import json
import os
import random
from asyncio import sleep

import yaml
from mirai import GroupMessage, Plain, MessageChain, Startup
from mirai import Image
from mirai.models import ForwardMessageNode, Forward

from plugins.wReply.MessageConvert import EventMessageConvert
from plugins.wReply.wReplyOpeator import addRep, loadAllDict, getRep, compare2messagechain


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


def main(bot, logger):
    class Main:
        def __init__(self):
            logger.info("启动自定义词库")
            with open('config.json', 'r', encoding='utf-8') as f:
                configYaml = yaml.load(f.read(), Loader=yaml.FullLoader)
                self.master = configYaml.get("master")
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            self.wReply = result.get("wReply")
            self.publicDict = loadAllDict()
            # 操作进程监听
            self.operateProcess = {}
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                self.userdict = yaml.load(file, Loader=yaml.FullLoader)
            self.colorfulCharacterList = os.listdir("data/colorfulAnimeCharacter")
            self.repeatData = {333: {"times": 0, "mes": "你好", "simplemes": "你好"}}
            self.repeatLock = {1111: datetime.datetime.now()}  # 复读冷却锁

            # 开始添加

        @bot.on(GroupMessage)
        async def startAddRep(self, event: GroupMessage):

            if self.wReply.get("editPermission") != 0:  # 权限限制，为0则为开放授权
                if str(event.sender.id) in self.userdict:
                    if int(self.userdict.get(str(event.sender.id)).get('sts')) < self.wReply.get("editPermission"):
                        return
                else:
                    return
            if str(event.message_chain) == "开始添加":
                await sleep(0.1)
                self.operateProcess[event.sender.id] = {"status": "startadd", "time": datetime.datetime.now(),
                                                   "operateId": str(event.group.id)}
            elif str(event.message_chain).startswith("群词库添加") and event.sender.id == int(self.master):
                await sleep(0.1)
                self.operateProcess[event.sender.id] = {"status": "startadd", "time": datetime.datetime.now(),
                                                   "operateId": str(event.message_chain).replace("群词库添加", "")}
            elif str(event.message_chain) == "*开始添加":
                if self.wReply.get("golbalLexiconRequire") != 0:  # 权限限制，为0则为开放授权
                    if str(event.sender.id) in self.userdict:
                        if int(self.userdict.get(str(event.sender.id)).get('sts')) < self.wReply.get("golbalLexiconRequire"):
                            return
                    else:
                        return
                await bot.send(event, "此操作将为所有群添加回复")
                await sleep(0.1)
                self.operateProcess[event.sender.id] = {"status": "startadd", "time": datetime.datetime.now(),
                                                   "operateId": "publicLexicon"}
            else:
                return
            await bot.send(event, "请发送关键词")

        @bot.on(GroupMessage)
        async def RecordKey(self, event: GroupMessage):

            if event.sender.id in self.operateProcess:
                if self.operateProcess[event.sender.id]["status"] == "startadd":
                    await sleep(0.1)
                    self.operateProcess[event.sender.id]["status"] = "adding"
                    self.operateProcess[event.sender.id]["time"] = datetime.datetime.now()
                    # operateProcess[event.sender.id]["key"] = str(event.message_chain)
                    self.operateProcess[event.sender.id]["key"] = event.message_chain.json()
                    if self.operateProcess[event.sender.id]["operateId"] in self.publicDict:
                        r = await getRep(self.publicDict.get(self.operateProcess[event.sender.id]["operateId"]),
                                         event.message_chain.json(), self.wReply.get("threshold"), self.wReply.get("mode"),
                                         self.wReply.get("inMaxLength"), self.wReply.get("inWeighting"))
                        # if str(event.message_chain) in publicDict.get(operateProcess[event.sender.id]["operateId"]):
                        # operateProcess[event.sender.id]["value"]=publicDict.get(operateProcess[event.sender.id]["operateId"]).get(str(event.message_chain))
                        if r is not None:
                            self.operateProcess[event.sender.id]["value"] = r[1]
                            logger.info("已存在关键词")
                    await bot.send(event, "请发送回复，发送 over 以退出添加")

        @bot.on(GroupMessage)
        async def addValue(self, event: GroupMessage):
            if event.sender.id in self.operateProcess:
                if self.operateProcess[event.sender.id]["status"] == "adding":
                    if str(event.message_chain) == "over":
                        logger.info("退出添加，开始保存用户添加的所有回复")
                        self.publicDict = await addRep(self.operateProcess[event.sender.id]["key"],
                                                  self.operateProcess[event.sender.id]["value"],
                                                  self.operateProcess[event.sender.id]["operateId"])
                        await bot.send(event, "退出回复添加")
                        self.operateProcess.pop(event.sender.id)
                        return
                    await sleep(0.1)
                    newMes = await EventMessageConvert(event.message_chain)
                    if "value" in self.operateProcess[event.sender.id]:
                        self.operateProcess[event.sender.id]["value"].append(newMes)
                    else:
                        self.operateProcess[event.sender.id]["value"] = [newMes]
                    await bot.send(event, "已记录回复")
                    self.operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间

        # 查询关键词对应回复
        @bot.on(GroupMessage)
        async def queryValue(self, event: GroupMessage):
            if self.wReply.get("editPermission") != 0:
                if str(event.sender.id) in self.userdict:
                    if int(self.userdict.get(str(event.sender.id)).get('sts')) < self.wReply.get("editPermission"):
                        return
                else:
                    return
            if str(event.message_chain) == "查回复":
                await sleep(1)
                self.operateProcess[event.sender.id] = {"status": "query", "operateId": str(event.group.id),
                                                   "time": datetime.datetime.now()}
            elif str(event.message_chain) == "*查回复":
                await sleep(1)
                self.operateProcess[event.sender.id] = {"status": "query", "operateId": "publicLexicon",
                                                   "time": datetime.datetime.now()}
            else:
                return
            logger.info("查询回复目标")
            await bot.send(event, "请发送要查询的目标")

        @bot.on(GroupMessage)
        async def sendQueryResults(self, event: GroupMessage):
            if event.sender.id in self.operateProcess:
                if str(event.message_chain).endswith("查回复"):
                    return
                if self.operateProcess[event.sender.id]["status"] == "query":
                    r = await getRep(self.publicDict.get(self.operateProcess[event.sender.id]["operateId"]),
                                     str(event.message_chain.json()), self.wReply.get("threshold"), self.wReply.get("mode"),
                                     self.wReply.get("inMaxLength"), self.wReply.get("inWeighting"))
                    b1 = []
                    if r is not None:
                        index = 0
                        for i in r[1]:
                            mesc = await mesChainConstructer(i)
                            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                         message_chain=MessageChain([f"编号{index}👇"])))
                            b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                         message_chain=MessageChain(mesc)))
                            index += 1
                        await bot.send(event, Forward(node_list=b1))
                        await bot.send(event, f"发送 删除#编号 以删除指定回复\n发送 删除关键字 以删除全部回复")
                        self.operateProcess[event.sender.id]["status"] = "delete"
                        await sleep(0.1)
                        self.operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间
                        self.operateProcess[event.sender.id]["queryKey"] = r[0]
                    else:
                        await bot.send(event, "无查询结果", True)
                        self.operateProcess.pop(event.sender.id)
                    return
                if self.operateProcess[event.sender.id]["status"] == "delete":
                    if str(event.message_chain).startswith("删除#"):
                        try:
                            index = int(str(event.message_chain).split("#")[1])
                            value = self.publicDict.get(self.operateProcess[event.sender.id]["operateId"]).get(
                                self.operateProcess[event.sender.id]["queryKey"])
                            value.pop(index)
                            self.publicDict = await addRep(self.operateProcess[event.sender.id]["queryKey"], value,
                                                      self.operateProcess[event.sender.id]["operateId"])
                            await bot.send(event, "已移除对应回复")
                            self.operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间
                        except:
                            logger.error("非法输入，索引必须是有效的数字")
                    elif str(event.message_chain) == "删除关键字":
                        try:
                            self.publicDict[self.operateProcess[event.sender.id]["operateId"]].pop(
                                self.operateProcess[event.sender.id]["queryKey"])
                            await bot.send(event, "已移除")
                            self.operateProcess[event.sender.id]["time"] = datetime.datetime.now()  # 不要忘记刷新时间
                            id = self.operateProcess[event.sender.id]["operateId"]
                            id = f"data/autoReply/lexicon/{id}.yaml"
                            with open(id, 'w', encoding="utf-8") as file:
                                yaml.dump(self.publicDict[self.operateProcess[event.sender.id]["operateId"]], file,
                                          allow_unicode=True)
                        except:
                            logger.error("非法输入，索引必须是有效的数字")

        @bot.on(GroupMessage)
        async def getReply(self, event: GroupMessage):

            if event.sender.id in self.operateProcess:
                return
            if random.randint(0, 100) > self.wReply.get("replyRate"):
                return
            if str(event.group.id) in self.publicDict:
                r = await getRep(self.publicDict.get(str(event.group.id)), str(event.message_chain.json()),
                                 self.wReply.get("threshold"), self.wReply.get("mode"), self.wReply.get("inMaxLength"),
                                 self.wReply.get("inWeighting"))
            else:
                r = await getRep(self.publicDict.get("publicLexicon"), str(event.message_chain.json()),
                                 self.wReply.get("threshold"),
                                 self.wReply.get("mode"), self.wReply.get("inMaxLength"), self.wReply.get("inWeighting"))
            if r is not None:
                logger.info(f"词库匹配成功")
                if random.randint(0, 100) < self.wReply.get("colorfulCharacter"):
                    logger.info("本次使用彩色小人替代匹配回复")
                    c = random.choice(self.colorfulCharacterList)
                    await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                    return
                mesc = await mesChainConstructer(random.choice(r[1]))
                await bot.send(event, MessageChain(mesc))

        @bot.on(Startup)
        async def checkTimeOut(self, event: Startup):
            while True:
                self.operateProcess = await self.check_and_pop_expired_keys(self.operateProcess)
                await asyncio.sleep(30)

        async def check_and_pop_expired_keys(self, data):
            keys_to_pop = []
            now = datetime.datetime.now()
            minutes = datetime.timedelta(seconds=self.wReply.get("timeout"))
            for key, value in data.items():
                time_diff = now - value.get('time', now)  # 如果 'time' 不存在，则使用 now，避免错误
                if time_diff > minutes:
                    keys_to_pop.append(key)

            for key in keys_to_pop:
                data.pop(key, None)
                logger.info(f"词库操作超时释出：{key}")
            return data

        @bot.on(Startup)
        async def upDate(self, event: Startup):
            while True:
                await sleep(60)
                with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                    self.userdict = yaml.load(file, Loader=yaml.FullLoader)

        # 用以实现复读
        @bot.on(GroupMessage)
        async def repeatFunc(self, event: GroupMessage):

            if event.group.id in self.repeatData:
                if str(event.message_chain) == self.repeatData[event.group.id]["simplemes"]:  # 最新的消息链同记录的最后一个消息链相同
                    score = await compare2messagechain(event.message_chain.json(),
                                                       self.repeatData[event.group.id]["mes"])
                    if score > 90:
                        if self.repeatData[event.group.id]["times"] == 2:  # 3次，进入复读
                            d = await mesChainConstructer(self.repeatData[event.group.id]["sefmeschain"])
                            await bot.send(event, MessageChain(d))  # 复读一次
                            logger.info(f"复读一次{str(event.message_chain)}")
                            self.repeatData.pop(event.group.id)  # 终止此次复读任务
                            self.repeatLock[event.group.id] = datetime.datetime.now()  # 进入cd时间
                            logger.info(f"{event.group.id} 进入cd冷却60s")
                        else:
                            self.repeatData[event.group.id]["times"] = self.repeatData[event.group.id][
                                                                           "times"] + 1  # 加一次
                    else:
                        try:
                            self.repeatData.pop(event.group.id)  # 终止此次复读任务
                        except:
                            pass  # 不知道为啥报错，先catch，等有空分析。
                else:
                    self.repeatData.pop(event.group.id)  # 终止此次复读任务
            else:
                if event.group.id in self.repeatLock and datetime.datetime.now() - self.repeatLock[
                    event.group.id] < datetime.timedelta(60):  # 时间锁
                    return
                try:
                    self.repeatData[event.group.id] = {"times": 1, "mes": event.message_chain.json(),
                                                       "simplemes": str(event.message_chain),
                                                       "sefmeschain": await EventMessageConvert(event.message_chain,
                                                                                                True)}
                except:
                    pass
    return Main()
