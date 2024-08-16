# -*- coding: utf-8 -*-
import os
import random

import yaml
import httpx
from bs4 import BeautifulSoup
from fuzzywuzzy import process
from mirai import GroupMessage, At
from mirai import Voice
from mirai.models import MusicShare

from plugins.newsEveryDay import get_headers
from plugins.cloudMusic import newCloudMusicDown, cccdddm


def main(bot, logger):
    logger.warning("语音点歌 loaded")
    global musicTask
    musicTask = {}
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
        global musicTask
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
                    await bot.send(event, f"请发送对应歌曲的序号:\n{musicL}", True)
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
                    await bot.send(event, t, True)

    @bot.on(GroupMessage)
    async def select11Music(event: GroupMessage):
        global musicTask
        if event.sender.id in musicTask:
            try:
                if musicToVoice:
                    try:
                        order = int(str(event.message_chain))
                    except:
                        await bot.send(event, "点歌失败！不规范的操作\n请输入数字。")
                        musicTask.pop(event.sender.id)
                        return
                    if order < 1:
                        order = 1
                    musiclist = musicTask.get(event.sender.id)
                    logger.info(f"获取歌曲：{musiclist[order - 1]}")
                    musicTask.pop(event.sender.id)
                    if downloadMusicUrl:
                        p, MusicUrlDownLoad = await newCloudMusicDown(musiclist[order - 1][1], True)
                        await bot.send(event, f"下载链接(mp3)：{MusicUrlDownLoad}")
                    else:
                        p = await newCloudMusicDown(musiclist[order - 1][1])
                    logger.info(f"已下载目标单曲：{p}")
                    await bot.send(event, Voice(path=p))
                else:
                    ass = musicTask.get(event.sender.id)[int(str(event.message_chain))-1]
                    logger.info("获取歌曲：" + ass[0])
                    
                    client = httpx.Client(headers=get_headers())
                    url = f'https://music.163.com/song?id={ass[1]}'
                    response = client.get(url)
                    musicTask.pop(event.sender.id)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    imgurl=soup.find('img',class_='j-img')['data-src']
                    await bot.send(event, MusicShare(kind="QQMusic", title=ass[0],
                                                                      summary=ass[2],
                                                                      jump_url=f"https://y.music.163.com/m/song?id={ass[1]}&uct2=jkZ3LZNLyka9TmygfSgqeQ%3D%3D&dlt=0846&app_version=9.0.95",
                                                                      picture_url=imgurl,
                                                                      music_url=f"http://music.163.com/song/media/outer/url?id={ass[1]}",
                                                                      brief=ass[2]))

            except Exception as e:
                logger.error(e)
                try:
                    musicTask.pop(event.sender.id)
                except:
                    pass
                await bot.send(event,e)

