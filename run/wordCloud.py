# -*- coding:utf-8 -*-
import datetime
import os.path

from mirai import GroupMessage, Plain
from mirai import Image

from plugins.toolkits import random_str
from plugins.wordcloud import appendData, create_chinese_wordcloud_async, getMyAllText, getgroupText


def main(bot,logger):
    logger.info("词云功能启动")

    @bot.on(GroupMessage)
    async def addData(event: GroupMessage):
        try:
            text=event.message_chain.get(Plain)
            groupid=event.group.id
            userid=event.sender.id
            await appendData(str(text[0]),groupid,userid)
        except Exception as e:
            pass
    @bot.on(GroupMessage)
    async def wordCloud(event: GroupMessage):
        if str(event.message_chain)=="今日词云":
            if os.path.exists(f"data/text/wordcloudData/{event.group.id}/{datetime.date.today().strftime('%Y-%m-%d')}/{event.sender.id}.txt"):
                with open(f"data/text/wordcloudData/{event.group.id}/{datetime.date.today().strftime('%Y-%m-%d')}/{event.sender.id}.txt","r",encoding="utf-8") as f:
                    save_path=f"data/pictures/cache/{random_str()}.png"
                    print(save_path)
                    await create_chinese_wordcloud_async(f.read(),save_path)
                    await bot.send(event,Image(path=save_path),True)
            else:
                await bot.send(event,"你还没有足够的发言记录",True)
        elif str(event.message_chain)=="历史词云":
            logger.info(f"获取用户{event.sender.id} 历史词云")
            text=await getMyAllText(f"data/text/wordcloudData/{event.group.id}",event.sender.id)
            save_path = f"data/pictures/cache/{random_str()}.png"
            await create_chinese_wordcloud_async(text, save_path)
            await bot.send(event, Image(path=save_path), True)
        elif str(event.message_chain)=="本群今日词云":
            logger.info(f"获取群{event.group.id} 今日词云")
            if os.path.exists(f"data/text/wordcloudData/{event.group.id}/{datetime.date.today().strftime('%Y-%m-%d')}"):
                text=await getgroupText(event.group.id,"today")
                print(text)
                save_path = f"data/pictures/cache/{random_str()}.png"
                await create_chinese_wordcloud_async(text, save_path)
                await bot.send(event, Image(path=save_path), True)
            else:
                await bot.send(event,"没有本群记录呢")
        elif str(event.message_chain)=="本群历史词云":
            if os.path.exists(f"data/text/wordcloudData/{event.group.id}"):
                text=await getgroupText(event.group.id,"all")
                save_path = f"data/pictures/cache/{random_str()}.png"
                await create_chinese_wordcloud_async(text, save_path)
                await bot.send(event, Image(path=save_path), True)
            else:
                await bot.send(event,"没有本群记录呢")