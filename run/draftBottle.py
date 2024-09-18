import asyncio
import datetime
import json
import random
from mirai.models import ForwardMessageNode, Forward
import yaml
from mirai import FriendMessage, GroupMessage, At, Plain,MessageChain,Startup
from mirai import Image, Voice,At
from plugins.toolkits import random_str
from plugins.wReply.MessageConvert import EventMessageConvert


def main(bot,logger):
    with open('config.json', 'r', encoding='utf-8') as f:
        configdata = yaml.load(f.read(), Loader=yaml.FullLoader)
    master=configdata['master']
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    draftBottle=controller.get("漂流瓶").get("enable")
    pushcomments=controller.get("漂流瓶").get("pushcomments")
    if not draftBottle:
        logger.warning("未开启漂流瓶功能")
        return
    logger.info("漂流瓶 enabled")
    global sea, operateProcess
    operateProcess={}
    with open('data/text/draftBottleData.yaml', 'r', encoding='utf-8') as f:
        sea = yaml.load(f.read(), Loader=yaml.FullLoader)
    @bot.on(GroupMessage)
    async def startThrowBottle(event: GroupMessage):
        global sea, operateProcess
        if str(event.message_chain)=="扔瓶子" or (At(bot.qq) in event.message_chain and str(event.message_chain).replace(f"@{bot.qq}","")=="扔瓶子"):
            logger.info("扔瓶子 任务已加入队列")
            await bot.send(event,"请发送要扔出的内容。\n如发送违禁内容将被bot永久拉黑")
            operateProcess[event.sender.id]={"time":datetime.datetime.now(),"status":"throw"}
    @bot.on(GroupMessage)
    async def throwOperation(event: GroupMessage):
        global sea,operateProcess
        if event.sender.id in operateProcess and operateProcess[event.sender.id]["status"]=="throw":
            bootleid=int(random_str(6,'123456789'))
            while bootleid in sea:
                bootleid=int(random_str(6,'123456789'))
                logger.warning("漂流瓶随机id重复，重新获取")
            newMes = await EventMessageConvert(event.message_chain)
            sea[bootleid]={"bottle":newMes,"sender":{"发送者":event.sender.id,"昵称":event.sender.member_name}}
            operateProcess.pop(event.sender.id)
            with open("data/text/draftBottleData.yaml", 'w', encoding="utf-8") as file:
                yaml.dump(sea, file, allow_unicode=True)
            await bot.send(event,f"添加成功，瓶子id:{bootleid}")
    @bot.on(GroupMessage)
    async def getBottle(event: GroupMessage):
        global sea,operateProcess
        if str(event.message_chain)=="捡瓶子" or (At(bot.qq) in event.message_chain and str(event.message_chain).replace(f"@{bot.qq}","")=="捡瓶子"):
            btid=random.choice(list(sea.keys()))
            logger.info(f"捡瓶子 {btid}")
            b1=await constructFordMes(btid)
            await bot.send(event, Forward(node_list=b1))
            if event.sender.id not in operateProcess:
                operateProcess[event.sender.id]={}
            operateProcess[event.sender.id]["status"]="otherOperate"
            operateProcess[event.sender.id]["time"]=datetime.datetime.now()
            operateProcess[event.sender.id]["bottleid"]=btid
    @bot.on(GroupMessage)
    async def commentOrReport(event: GroupMessage):
        global sea,operateProcess
        if event.sender.id in operateProcess and operateProcess[event.sender.id]["status"]=="otherOperate":
            if str(event.message_chain)=="评论":
                logger.info("创建评论任务")
                await bot.send(event,"请发送评论")
                operateProcess[event.sender.id]["time"] = datetime.datetime.now()
                operateProcess[event.sender.id]["status"] = "comment"
            elif str(event.message_chain)=="举报瓶子":
                logger.info("漂流瓶举报....向master发送请求中")
                await bot.send(event,"已向管理员转达")
                b1=await constructFordMes(operateProcess[event.sender.id]["bottleid"])
                await bot.send_friend_message(master,Forward(node_list=b1))
                await bot.send_friend_message(master,f"来自 {event.sender.member_name}({event.sender.id})的举报，请检查上述漂流瓶是否存在违规内容")

    @bot.on(GroupMessage)
    async def addcomment(event: GroupMessage):
        global sea,operateProcess
        if event.sender.id in operateProcess and operateProcess[event.sender.id]["status"] == "comment":
            logger.info(f"{operateProcess[event.sender.id]['bottleid']} 增加 comment")
            bottle = sea[operateProcess[event.sender.id]["bottleid"]]
            newMes = await EventMessageConvert(event.message_chain)
            if "comments" not in bottle:
                bottle["comments"]={event.sender.id:newMes}
            else:
                bottle["comments"][event.sender.id] = newMes
            sea[operateProcess[event.sender.id]["bottleid"]] = bottle
            try:
                if pushcomments:
                    await bot.send_friend_message(bottle["sender"]["发送者"],f"您的漂流瓶{operateProcess[event.sender.id]['bottleid']}获得了一条评论\n来源:{event.sender.member_name}({event.sender.id}) ")
                    await bot.send_friend_message(bottle["sender"]["发送者"],json.loads(event.message_chain.json()))
                    b1=await constructFordMes(operateProcess[event.sender.id]["bottleid"])
                    await bot.send_friend_message(bottle["sender"]["发送者"], Forward(node_list=b1))
            except:
                logger.warning(f"无法向 瓶子所有者{bottle['sender']['发送者']} 推送评论")
            with open("data/text/draftBottleData.yaml", 'w', encoding="utf-8") as file:
                yaml.dump(sea, file, allow_unicode=True)
            await bot.send(event,f"添加成功，瓶子id:{operateProcess[event.sender.id]['bottleid']}")
            operateProcess.pop(event.sender.id)
    @bot.on(GroupMessage)
    async def query(event: GroupMessage):
        global sea,operateProcess
        if str(event.message_chain).startswith("查瓶子"):
            try:
                btid=int(str(event.message_chain).replace("查瓶子",""))
            except:
                logger.error("漂流瓶：不合法的查询值")
                return
            if btid in sea:
                logger.info(f"查询漂流瓶 {btid}")
                fomes=await constructFordMes(btid)
                await bot.send(event, Forward(node_list=fomes))
                if event.sender.id not in operateProcess:
                    operateProcess[event.sender.id]={}
                operateProcess[event.sender.id]["status"] = "otherOperate"
                operateProcess[event.sender.id]["time"] = datetime.datetime.now()
                operateProcess[event.sender.id]["bottleid"] = btid
            else:
                await bot.send(event,"没有找到目标",True)
        elif str(event.message_chain).startswith("删瓶子"):

            try:
                btid=int(str(event.message_chain).replace("删瓶子",""))
                logger.info(f"删除漂流瓶 {btid}")
            except:
                logger.error("漂流瓶：不合法的删除值")
                return
            if btid in sea:
                sea.pop(btid)
                await bot.send(event,"移除了指定目标",True)
                with open("data/text/draftBottleData.yaml", 'w', encoding="utf-8") as file:
                    yaml.dump(sea, file, allow_unicode=True)
            else:
                await bot.send(event,"没有找到目标",True)

    @bot.on(Startup)
    async def checkTimeOut(event: Startup):
        global operateProcess
        while True:
            operateProcess = await check_and_pop_expired_keys(operateProcess)
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
            logger.info(f"漂流瓶操作超时释出：{key}")
        return data
    async def constructFordMes(bid):
        global operateProcess,sea
        bottle = sea[bid]
        b1 = []
        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                     message_chain=MessageChain([f"编号:{bid}\n发送者:{bottle['sender']['昵称']} ({bottle['sender']['发送者']}) \n瓶子内容如下："])))

        def selfConstrucuer(source):
            bottleConstruct=[]
            if "time" in str(source):
                return json.loads(source)#对旧数据实现兼容
            else:
                for i in source:
                    if "text" in i:
                        bottleConstruct.append(Plain(i["text"]))
                    elif "image" in i:
                        bottleConstruct.append(Image(path=i["image"]))
                return bottleConstruct
                 
        
        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                     message_chain=MessageChain(selfConstrucuer(bottle["bottle"]))))

        if "comments" in bottle:
            for comment in bottle["comments"]:
                b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                             message_chain=MessageChain(f"评论者：{comment}")))
                b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                             message_chain=MessageChain(selfConstrucuer(bottle["comments"][comment]))))
        b1.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                     message_chain=MessageChain(
                                         "如有需要，请在3min内\n发送 评论 然后再发送你的评论。恶意评论将被拉黑。\n发送 举报瓶子 以举报当前漂流瓶 报假案会被拉黑")))
        return b1
