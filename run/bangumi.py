# -*- coding:utf-8 -*-
import datetime
import json
import re
from asyncio import sleep
import httpx
import yaml
import requests
from bs4 import BeautifulSoup

from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models.events import BotInvitedJoinGroupRequestEvent, NewFriendRequestEvent, MemberJoinRequestEvent, \
    MemberHonorChangeEvent, MemberCardChangeEvent, BotMuteEvent, MemberSpecialTitleChangeEvent, BotJoinGroupEvent, \
    MemberJoinEvent, MemberMuteEvent, MemberUnmuteEvent, BotUnmuteEvent, BotLeaveEventKick, MemberLeaveEventKick, \
    MemberLeaveEventQuit
from plugins.newsEveryDay import get_headers
from plugins.webScreenShoot import screenshot_to_pdf_and_png
from plugins.bangumisearch import bangumisearch

def main(bot,logger):
    global searchtask
    global switch
    searchtask={}
    switch=0
    logger.info("Bangumi功能已启动")
    @bot.on(GroupMessage)
    async def animerank(event: GroupMessage):
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
    async def bangumi_calendar(event: GroupMessage):               
        if str(event.message_chain)=="bangumi今日放送":
            url = "https://www.bangumi.app/calendar/today"
            path = "data/pictures/bangumi/calendar/today-"              
        elif str(event.message_chain)=="bangumi周表":
            #url = "https://api.bgm.tv/calendar"
            url = "https://bgm.tv/calendar"
            path = "data/pictures/bangumi/calendar/week-" 
        elif str(event.message_chain)=="bangumi热门":
            url = "https://www.bangumi.app/hot/anime"
            path = "data/pictures/bangumi/hot-"
        else:
            return
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        path = path+today+".png"   
        try:
            screenshot_to_pdf_and_png(url,path,1080,3000)                
            await bot.send(event,[f"{str(event.message_chain)} {today}：",Image(path=path)], True)  
        except Exception as  e:
            logger.error(e)   
            await bot.send(event,"获取bangumi信息失败，请稍后再试")

    @bot.on(GroupMessage)
    async def bangumi_search(event: GroupMessage):
        if "bangumi查询" in str(event.message_chain):
                #url="https://api.bgm.tv/search/subject/"+str(event.message_chain).split(" ")[1]
                cat="all"
        elif "查询动画" in str(event.message_chain) or "查询番剧" in str(event.message_chain):
                cat=2
        elif "查询书籍" in str(event.message_chain):
                cat=1
        elif "查询游戏" in str(event.message_chain):
                cat=4
        elif "查询音乐" in str(event.message_chain):
                cat=3
        elif "查询三次元" in str(event.message_chain):
                cat=6
        # elif "查询人物" in str(event.message_chain):
        #         cat="all";type="mono";sign="h2"
        # elif "查询虚拟角色" in str(event.message_chain):
        #         cat="crt";type="mono";sign="h2"
        # elif "查询现实人物" in str(event.message_chain):
        #         cat="prsn";type="mono";sign="h2"
        else:
            return
         
        keywords = str(event.message_chain).split(" ")[1]
        url = f"https://bgm.tv/subject_search/{keywords}?cat={cat}"
        logger.info("正在查询："+keywords)
        path = "data/pictures/bangumi/search/"+keywords+".png"
        try:
            str0 = f"{bangumisearch(url)[0]}\n请发送编号进入详情页，或发送退出退出查询"
            screenshot_to_pdf_and_png(url,path,1080,1750)
            await bot.send(event,[str0,Image(path=path)],True)
            global switch
            global searchtask
            searchtask[event.sender.id]=keywords,cat
            switch=1
        except Exception as  e:
            logger.error(e)   
            searchtask.pop(event.sender.id)
            await bot.send(event,"查询失败，请稍后再试")       

    @bot.on(GroupMessage)
    async def bangumi_search_detail(event: GroupMessage):
        global searchtask
        if event.sender.id in searchtask:
            try:
                if str(event.message_chain) == "退出":
                    searchtask.pop(event.sender.id)
                    await bot.send(event,"已退出查询")
                    return
                keywords,cat=searchtask[event.sender.id]
                url = f"https://bgm.tv/subject_search/{keywords}?cat={cat}"
                subjectlist=bangumisearch(url)[1]
                crtlist=bangumisearch(url)[2]
                order = int(str(event.message_chain))
                if str(event.message_chain).startswith("0") and order<=len(crtlist):
                    crt = crtlist[order-1].find("a")["href"]
                    url="https://bgm.tv"+crt
                    logger.info("正在获取"+crt+"详情")
                    path = f"data/pictures/bangumi/search-{keywords}-0{order}.png"
                    title=crtlist[order-1].find("a").string
                elif 1 <= order <= len(subjectlist):
                    subject = subjectlist[order-1].find("a")["href"]
                    url="https://bgm.tv"+subject
                    logger.info("正在获取"+subject+"详情")
                    path = f"data/pictures/bangumi/search-{keywords}-{order}.png"
                    title=subjectlist[order-1].find("a").string
                else:
                    await bot.send(event,"查询失败！不规范的操作")
                    searchtask.pop(event.sender.id)
                    return
                try:
                    logger.info("正在获取"+title+"详情")
                    screenshot_to_pdf_and_png(url,path,1080,1750)
                    await bot.send(event,["查询结果：",title,Image(path=path)], True)
                except Exception as  e:
                    logger.error(e)
                    await bot.send(event,"查询失败，请稍后再试")       
                searchtask.pop(event.sender.id)
            except Exception as  e:
                logger.error(e)
                searchtask.pop(event.sender.id)
                await bot.send(event,"查询失败！不规范的操作")       

    @bot.on(GroupMessage)
    async def bangumi_search_timeout(event: GroupMessage):
        global searchtask
        global switch
        if event.sender.id in searchtask:
            if switch:
                switch=0    #保证只发送一次超时提示
                await sleep(60*3)
                if event.sender.id in searchtask:   #检验查询是否结束
                    searchtask.pop(event.sender.id)
                    await bot.send(event,"查询超时，已自动退出",True)


        
  
                     
            
