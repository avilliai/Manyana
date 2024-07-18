# -*- coding:utf-8 -*-
import datetime
import json
import re
from asyncio import sleep
import httpx
import yaml
import requests  # 导入requests模块
from bs4 import BeautifulSoup   # 导入Beautiful Soup模块

from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models.events import BotInvitedJoinGroupRequestEvent, NewFriendRequestEvent, MemberJoinRequestEvent, \
    MemberHonorChangeEvent, MemberCardChangeEvent, BotMuteEvent, MemberSpecialTitleChangeEvent, BotJoinGroupEvent, \
    MemberJoinEvent, MemberMuteEvent, MemberUnmuteEvent, BotUnmuteEvent, BotLeaveEventKick, MemberLeaveEventKick, \
    MemberLeaveEventQuit
from plugins.newsEveryDay import get_headers
from plugins.webScreenShoot import webScreenShot,webScreenShoot
#bot,logger
def main(bot,logger):
    
    @bot.on(GroupMessage)
    async def animerank(event: GroupMessage):   # 定义函数，获取番剧排行
        if ("新番排行" in str(event.message_chain)) or ("新番top" in str(event.message_chain)):
            year=datetime.datetime.now().strftime("%Y")    # 默认当前年份
            month=datetime.datetime.now().strftime("%m")   # 默认当前月份
        elif ("番剧排行" in str(event.message_chain)) or ("番剧top" in str(event.message_chain))\
            or ("动画排行" in str(event.message_chain)) or ("动画top" in str(event.message_chain)):
            year=""                                        # 默认空值,表示全部
            month=""                                       # 默认空值,表示全部         
        else:
            return
        try:
            rank=1   # 排名
            page=1   # 页数
            top=24   # 显示上限（默认显示前24个即显示第一页）               
            try:
                if "年" in str(event.message_chain):
                    year=str(event.message_chain).split("年")[0][-1:-5]    # 获取年份参数
                    year=re.sub(r'[^\d]', '', year) 
                if "月" in str(event.message_chain):
                    month=str(event.message_chain).split("月")[0][-1:-3]   # 获取月份参数
                    month=re.sub(r'[^\d]', '', month)
                    if len(month)<2:     month="0"+month                   # 月份使用0补齐
                if "top" in str(event.message_chain):
                    top=int(str(event.message_chain).split("top")[1])      # 获取top参数
                elif "排行" in str(event.message_chain):
                    top=int(str(event.message_chain).split("排行")[1])
                page=top//24   # 计算页数
                if top%24!=0:
                    page+=1    # 向上取整
            except:
                pass
            logger.info("获取番剧排行")

            str0=year+"年"+month+"月 | Bangumi 番组计划\n"
            for i in range(1,page+1):
                url = f"https://bgm.tv/anime/browser/airtime/{year}-{month}?sort=rank&page={i}"   # 构造请求网址，page参数为第i页
                logger.info(f"正在获取番剧排行第{i}页")
                response = requests.get(url, headers=get_headers())
                soup = BeautifulSoup(response.content, "html.parser")             
                name_list = soup.find_all("h3")                                   # 获取番剧名称列表
                score_list = soup.find_all("small",class_="fade")                 # 获取番剧评分列表
                popularity_list = soup.find_all("span",class_="tip_j")            #获取番剧评分人数列表)
                logger.info("获取番剧排行成功")
                for j in range(len(score_list)):
                    try:
                        name_jp=name_list[j].find("small",class_="grey").string+"\n    "     # 获取番剧日文名称
                    except:
                        name_jp=""
                    name_ch=name_list[j].find("a",class_="l").string              # 获取番剧中文名称
                    score=score_list[j].string                                    # 获取番剧评分
                    popularity=popularity_list[j].string                          # 获取番剧评分人数
                    str0+="{:<3}".format(rank)
                    str0+=f"{name_jp}{name_ch}\n    {score}☆  {popularity}\n"   
                    if rank==top:                                                 # 达到显示上限
                        break
                    rank+=1
                if len(score_list)<top-(i-1)*24:                                  # 番剧数量少于显示上限
                    str0+="\n到底啦~"   
                    break
            await bot.send(event,str0)
        except Exception as  e:
            logger.error(e)
            await bot.send(event,"获取番剧信息失败，请稍后再试")   

    @bot.on(GroupMessage)
    async def bangumi_search(event: GroupMessage):                   # 定义函数，查询信息
        if "bangumi查询" in str(event.message_chain):
                #url="https://api.bgm.tv/search/subject/"+str(event.message_chain).split(" ")[1]
                cat="all";type="subject";sign="h3"
        elif "查询动画" in str(event.message_chain) or "查询番剧" in str(event.message_chain):
                cat=1;type="subject";sign="h3"
        elif "查询书籍" in str(event.message_chain):
                cat=2;type="subject";sign="h3"
        elif "查询游戏" in str(event.message_chain):
                cat=3;type="subject";sign="h3"
        elif "查询音乐" in str(event.message_chain):
                cat=4;type="subject";sign="h3"
        elif "查询三次元" in str(event.message_chain):
                cat=6;type="subject";sign="h3"
        elif "查询人物" in str(event.message_chain):
                cat="all";type="mono";sign="h2"
        elif "查询虚拟角色" in str(event.message_chain):
                cat="crt";type="mono";sign="h2"
        elif "查询现实人物" in str(event.message_chain):
                cat="prsn";type="mono";sign="h2"
        else:
            return
        #url="https://api.bgm.tv/search/subject/"+str(event.message_chain).split(" ")[1]
        keywards = str(event.message_chain).split(" ")[1]
        #url="https://api.bgm.tv/search/"+type+"?q="+keywards+"&cat="+str(cat)
        url = f"https://bgm.tv/{type}_search/{keywards}?cat={cat}"       
        path="data/pictures/bangumi/"+str(event.message_chain).split(" ")[1]+".png"
        try:
            response = requests.get(url, headers=get_headers())
            soup = BeautifulSoup(response.content, "html.parser")
            list = soup.find_all(sign)
            if len(list)==1:                          # 结果唯一时直接进入详情页
                url="https://bgm.tv"+list[0].find("a")["href"]
                await bot.send(event,f"查询结果：{list[0].find('a').string}")

        except:
             pass
        #等待5秒，防止请求过快
        await sleep(5)
        try:
            try:
                await webScreenShot(url,path,1080,1750)
            except:
                webScreenShoot(url,path,1080,1750)
        except Exception as  e:
            logger.error(e)   
            await bot.send(event,"查询失败，请稍后再试")       
            return
        await bot.send(event, Image(path=path), True)              
            
    @bot.on(GroupMessage)
    async def bangumi_calendar(event: GroupMessage):               
        if "bangumi今日放送" in str(event.message_chain):
            url = "https://www.bangumi.app/calendar/today"
            path = "data/pictures/bangumi/calendar/today-"
            width = 1080;height = 1800               
        elif "bangumi明日放送" in str(event.message_chain):
            url = "https://www.bangumi.app/calendar/tomorrow"
            path = "data/pictures/bangumi/calendar/tomorrow-"
            width = 1080;height = 1800
        elif "bangumi周表" in str(event.message_chain):
            #url = "https://api.bgm.tv/calendar"
            url = "https://bgm.tv/calendar"
            path = "data/pictures/bangumi/calender/week-"
            width = 1080;height = 3000  
        else:
            return
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        path = path+today+".png"   
        try:
            try:
                await webScreenShot(url,path,width,height)            # 截图方式1
            except:
                webScreenShoot(url,path,width,height)                 # 截图方式2
            await bot.send(event, Image(path=path), True)  
        except Exception as  e:
            logger.error(e)   
            await bot.send(event,"获取bangumi日历失败，请稍后再试")   
