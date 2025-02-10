# -*- coding: utf-8 -*-
import os
import random

import httpx
import yaml
from fuzzywuzzy import process
from mirai import GroupMessage, At
from mirai import Voice
from mirai.models import MusicShare

from plugins.cloudMusic import newCloudMusicDown, cccdddm


async def delete_msg_async(msg_id):
    url = "http://localhost:3000/delete_msg"
    payload = {
        "message_id": str(msg_id)
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ff'
    }
    async with httpx.AsyncClient(timeout=None,headers=headers) as client:
        response = await client.post(url, json=payload)
        #print(response.text)

def main(bot, logger):
    logger.warning("语音点歌 loaded")
    global musicTask
    musicTask = {}
    global musicTask_recall
    musicTask_recall = {}
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    downloadMusicUrl = controller.get("点歌").get("下载链接")
    musicToVoice = controller.get("点歌").get("musicToVoice")

    @bot.on(GroupMessage)
    async def dianzibofangqi(event: GroupMessage):
        if str(event.message_chain) == "开溜" or (
                At(bot.qq) in event.message_chain and "唱歌" in str(event.message_chain)):
            logger.info("电梓播放器，启动！")
            p = os.listdir("data/music/audio")
            purchase = random.choice(p)
            await bot.send(event, Voice(path="./data/music/audio/" + purchase))
            await bot.send(event, f"正在播放：{purchase}")

    @bot.on(GroupMessage)
    async def dianzibofangqidiange(event: GroupMessage):
        if str(event.message_chain).startswith("溜 ") or str(event.message_chain).startswith("唱 "):
            logger.info("电梓播放器，启动！")
            p = os.listdir("./data/music/audio")
            ha = process.extractBests(str(event.message_chain).replace("溜 ", "").replace("唱 ", ""), p, limit=3)
            logger.info(ha[0][0])
            p = "./data/music/audio/" + ha[0][0]
            await bot.send(event, Voice(path=p))

    @bot.on(GroupMessage)
    async def selectMusic(event: GroupMessage):
        global musicTask, musicTask_recall
        if str(event.message_chain).startswith("点歌 "):
            musicName = str(event.message_chain).replace("点歌 ", "")
            logger.info("点歌：" + musicName)
            if musicToVoice:
                ffs = await cccdddm(musicName)
                if ffs is None:
                    await bot.send(event, "连接出错，或无对应歌曲")
                else:
                    musicTask[event.sender.id] = ffs
                    musicL = ""
                    count1 = 1
                    for ib in ffs:
                        musicL += f"{count1} {ib[0]} {ib[2]}\n"
                        count1 += 1
                    recall_id= await bot.send(event, f"请发送对应歌曲的序号:\n{musicL}")
                    musicTask_recall[event.sender.id] = recall_id
            else:
                ffs = await cccdddm(musicName)
                if ffs is None:
                    await bot.send(event, "连接出错，或无对应歌曲")
                else:
                    musicTask[event.sender.id] = ffs
                    # print(ffs)
                    t = "请发送序号："
                    i = 1
                    for sf in ffs:
                        t += f"\n{i} {sf[0]}  |  {sf[2]}"
                        i += 1
                    recall_id=await bot.send(event, t)
                    musicTask_recall[event.sender.id] = recall_id
                    

    @bot.on(GroupMessage)
    async def select11Music(event: GroupMessage):
        global musicTask, musicTask_recall
        if event.sender.id in musicTask:
            try:
                try:
                    order = int(str(event.message_chain))
                except:
                    await bot.send(event, "点歌失败，请输入正确数字！")
                    try:
                        await delete_msg_async(musicTask_recall.get(event.sender.id))
                    except:
                        logger.info(f"无法正常撤回。请检查，recall_id：{recall_id}")
                    musicTask_recall.pop(event.sender.id)
                    musicTask.pop(event.sender.id)
                    return
                if order < 1:
                    order = 1
                musiclist = musicTask.get(event.sender.id)
                recall_id = musicTask_recall.get(event.sender.id)
                logger.info(f"获取歌曲：{musiclist[order - 1]}")
                musicTask.pop(event.sender.id)
                musicTask_recall.pop(event.sender.id)
                try:
                    await delete_msg_async(recall_id)
                except:
                    logger.info(f"无法正常撤回。请检查，recall_id：{recall_id}")
                recall_id = await bot.send(event, '正在获取ing，请稍后~')
                
                if musicToVoice:
                    p, MusicUrlDownLoad = await newCloudMusicDown(musiclist[order - 1][1], True)
                    if p is None:
                        await bot.send(event, '解析源失效了喵')
                        return
                    logger.info(f"已下载目标单曲：{p}")
                    await bot.send(event, Voice(path=p))
                else:
                    p, MusicUrlDownLoad =await newCloudMusicDown(musiclist[order - 1][1], True,True)
                    await bot.send(event, MusicShare(kind = "QQMusic",
                                     title = f'{musiclist[order - 1][0]}',
                                     summary = f'{musiclist[order - 1][0]}',
                                     jump_url = MusicUrlDownLoad,
                                     picture_url = "https://raw.githubusercontent.com/avilliai/imgBed/master/images/24202439348A04800FE5D98F76125113.png",
                                     music_url = MusicUrlDownLoad,
                                     brief = f'{musiclist[order - 1][0]}'))
                try:
                    await delete_msg_async(recall_id)
                except:
                    logger.info(f"无法正常撤回。请检查，recall_id：{recall_id}")
                if downloadMusicUrl:
                    await bot.send(event, f"下载链接(mp3)：{MusicUrlDownLoad}")

                

            except Exception as e:
                logger.error(e)
                try:
                    musicTask.pop(event.sender.id)
                except:
                    pass
                await bot.send(event,e)

