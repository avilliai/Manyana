# -*- coding: utf-8 -*-
import datetime
import json
from asyncio import sleep

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import MusicShare
from mirai import Startup, Shutdown

from plugins.RandomStr import random_str


def main(bot,master,botName,logger):
    file = open('data/music/music.txt', 'r')
    js = file.read()
    global userdict
    userdict = json.loads(js)
    logger.info("点歌加载完成")

    file1 = open('data/music/groups.txt', 'r')
    js1 = file1.read()
    file.close()
    global groupSend
    groupSend = 0
    global severGroups
    global severGroupsa
    severGroupsa = json.loads(js1)
    severGroups = severGroupsa.keys()


    global bm
    bm=botName

    global sender
    sender={}
    global times
    times=0
    global ask
    ask=0
    global message
    message=''
    global ban
    ban = ['妈', '主人', '狗', '老公', '老婆', '爸', '奶', '爷', '党', '爹', '逼', '牛', '国', '批']
    @bot.on(FriendMessage)
    async def music1(event: FriendMessage):
        if str(event.message_chain)=="点歌":
            global sender
            global times

            temp={}
            temp["step"]=0
            sender[str(event.sender.id)]=temp


            await bot.send(event,"请依次发送留言和音乐链接哦.....")
            await bot.send_friend_message(int(master),"有新的点歌任务")

    @bot.on(FriendMessage)
    async def music2(event: FriendMessage):
        global sender
        global step
        global message
        if event.message_chain.count(MusicShare):
            logger.info("点歌链接收到")
        if (str(event.sender.id) in sender.keys()):
            logger.info("senderOk")
        try:
            if sender.get(str(event.sender.id)).get("step")==1:
                logger.info("step:ok")
        except:
            logger.info("接收私聊消息"+str(event.message_chain))
        else:
            logger.info(sender)
        if event.message_chain.count(MusicShare) and (str(event.sender.id) in sender.keys()) and sender.get(str(event.sender.id)).get("step")==1:
            await bot.send_friend_message(int(master),event.message_chain)
            share=event.message_chain.get(MusicShare)
            '''print(share)
            print(share[0].kind)
            print(share[0].title)
            print(share[0].type)
            print(share[0].brief)
            print(share[0].jump_url)
            print(share[0].music_url)
            print(share[0].picture_url)
            print(share[0].summary)'''
            logger.info("构建数据")
            valuea={}
            valuea["kind"]=share[0].kind
            valuea["title"]=share[0].title
            valuea["type"]=share[0].type
            valuea["brief"]=share[0].brief
            valuea["jump_url"]=share[0].jump_url
            valuea["music_url"]=share[0].music_url
            valuea["picture_url"]=share[0].picture_url
            valuea["summary"]=share[0].summary
            valuea["message"]=sender.get(str(event.sender.id)).get("message")
            valuea["user"]=str(event.sender.nickname)
            valuea["userid"]=str(event.sender.id)

            today = datetime.date.today()

            while (str(today) in userdict.keys()):
                today=today + datetime.timedelta(days=1)
            userdict[str(today)]=valuea
            newData = json.dumps(userdict)
            with open('data/music/music.txt', 'w') as fp:
                fp.write(newData)

            sender.pop(str(event.sender.id))
            await bot.send(event, "已经了解" + str(event.sender.nickname) + "的需求啦(/▽＼)")
            await bot.send(event, "成功，您的点歌已加入序列，将在" + str(today) + "播放")
            try:
                logger.info("点歌数据构建完成：\n日期:"+str(today)+"\n留言："+sender.get(str(event.sender.id)).get("message"))

                await bot.send_friend_message(int(master), "点歌数据构建完成：\n日期:" + str(today) + "\n留言：" + sender.get(
                    str(event.sender.id)).get("message") + "点歌人：" + str(event.sender.nickname) + str(event.sender.id))
            except:
                logger.error("点歌通知给master出错，请忽略")



    @bot.on(FriendMessage)
    async def music3(event: FriendMessage):
        global sender
        global step
        global message
        global ask
        adsf=0
        if str(event.sender.id) in sender.keys() and event.message_chain.count(MusicShare)==False and sender.get(str(event.sender.id)).get("step")==0 and str(event.message_chain)!="点歌":
            if len(event.message_chain)>150:
                await bot.send(event,"文本太长了，大概率会被腾讯吞的.....试着发短点的吧....")
            else:
                if event.sender.id!=1840094972:
                    for i in ban:
                        if i in str(event.message_chain):
                            await bot.send(event,"好像有不太适合的字在里面.....")
                            adsf=1
                if adsf==0:

                    sender[str(event.sender.id)]={"step":1,"message":str(event.message_chain)}
                    logger.info(sender)
                    await bot.send(event,"留言： "+str(event.message_chain))
                    await bot.send(event,"请发送音乐链接(推荐网易云)")



    @bot.on(FriendMessage)
    async def confim(event: FriendMessage):
        global ask
        global step
        if ask==1 and step==0:
            if str(event.message_chain)=="0":
                await bot.send(event,"请重新发送留言")
            elif str(event.message_chain)=="1":
                await bot.send(event, "记下来啦，接下来发送音乐链接吧......")
                ask=0
                step+=1
            else:
                await bot.send(event,"不合法数值\n发送 0 重新留言,发送 1 确认留言")



    global scheduler
    scheduler = AsyncIOScheduler()

    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器


    @bot.on(Shutdown)
    def stop_scheduler(_):
        scheduler.shutdown(True)  # 结束定时器

    @scheduler.scheduled_job(CronTrigger(hour=20, minute=40))
    async def timer():
        global bm
        temp = userdict.get(str(datetime.date.today()))
        temp["userid"] = "A" + userdict.get(str(datetime.date.today())).get("userid")
        userdict[str(datetime.date.today())] = temp
        newData = json.dumps(userdict)
        with open('data/music/music.txt', 'w') as fp:
            fp.write(newData)
        for i in severGroups:
            intTrans = int(i)

            await sleep(3)

            file = open('data/music/music.txt', 'r')
            js = file.read()

            try:
                music = json.loads(js).get(str(datetime.date.today()))
                logger.info(music)
                # out = random.choice(file)
                logger.info( '正在向群' + str(i) + '点歌')
                await bot.send_group_message(intTrans,MusicShare(kind=music.get("kind"),title=music.get("title"), summary=music.get("summary"), jump_url=music.get("jump_url"), picture_url=music.get("picture_url"), music_url=music.get("music_url"),  brief=music.get("brief")))
                await bot.send_group_message(intTrans,"晚间电台ヾ(≧▽≦*)o\n来自"+str(music.get("user")+"的点歌\n留言："+str(music.get("message"))+"\n随机码:"+random_str()))
                await bot.send_group_message(intTrans,"私聊"+bm+"发送 点歌 即可点歌\n群内发送 /回复+回复内容 即可向点歌人回复\n随机码:"+random_str())
            except:
                logger.error("指定群不存在或已退出")

    @bot.on(GroupMessage)
    async def reply(event:GroupMessage):
        global userdict
        if str(event.message_chain).startswith("/回复"):
            temp=int(userdict.get(str(datetime.date.today())).get("userid").replace('A',""))
            await bot.send_friend_message(temp,"您收到了一条点歌回复q(≧▽≦q)：\n"+str(event.message_chain)[3:])
            await bot.send(event,"已为您转达q(≧▽≦q)")
    @bot.on(GroupMessage)
    async def autoAdd(event: GroupMessage):
        global severGroupsa
        global severGroups
        if str(event.group.id) not in severGroupsa.keys():
            severGroupsa[str(event.group.id)] = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            severGroups = severGroupsa.keys()
            newData = json.dumps(severGroupsa)
            logger.info("新增群"+str(event.group.id))
            with open('data/music/groups.txt', 'w') as fp:
                fp.write(newData)
