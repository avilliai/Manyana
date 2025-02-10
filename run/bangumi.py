# -*- coding:utf-8 -*-
import datetime
import re
from asyncio import sleep

from mirai import GroupMessage
from mirai import Image, MessageChain
from mirai.models import ForwardMessageNode, Forward

from plugins.bangumisearch import bangumisearch, banguimiList
from plugins.toolkits import screenshot_to_pdf_and_png


def main(bot,logger):
    global searchtask
    searchtask={}
    global switch
    switch=0
    logger.info("Bangumi功能已启动")
    @bot.on(GroupMessage)
    async def animerank(event: GroupMessage):
        if ("新番排行" in str(event.message_chain)) or ("新番top" in str(event.message_chain)):
            year=datetime.datetime.now().strftime("%Y")    # 默认当前年份，修一个问题
            month=datetime.datetime.now().strftime("%m")   # 默认当前月份
        elif ("番剧排行" in str(event.message_chain)) or ("番剧top" in str(event.message_chain))\
            or ("动画排行" in str(event.message_chain)) or ("动画top" in str(event.message_chain)):
            year = ""                                        # 默认空值,表示全部
            month = ""                                       # 默认空值,表示全部         
        else:
            return
        if "年" in str(event.message_chain):
            year = str(event.message_chain).split("年")[0]  # 获取年份参数
            year = re.sub(r'[^\d]', '', year)[-4::]
        if "月" in str(event.message_chain):    # 获取月份参数
            try:
                month = str(event.message_chain).split("年")[1].split("月")[0]  
            except:
                month = str(event.message_chain).split("月")[0]
            if len(month) < 2:
                month = "0" + month
        try:
            if "top" in str(event.message_chain):
                top = int(str(event.message_chain).split("top")[1])  # 获取top参数
            elif "排行" in str(event.message_chain):
                top = int(str(event.message_chain).split("排行")[1])
        except:
            top = 24

        try:
            finalT,finalC,isbottom=await banguimiList(year,month,top)
            title = year + "年" + month + "月 | Bangumi 番组计划\n"
            if year == "":
                title = "| Bangumi 番组计划\n"
            if month == "":
                title = title.replace("月","")
            bottom = "到底啦~"
            combined_list = []
            rank=1            
            print(len(finalT))
            times=len(finalT)//10
            if len(finalT)%10!=0:
                times+=1
                
            for i in range(times):
                combined_str = ""
                if i == 0:
                        combined_str += "title,"
                for j in range(10):  #10个一组发送消息
                    combined_str += f"Image(url=finalC[{rank-1}],cache=True),finalT[{rank-1}]"
                    rank += 1
                    if i*10+j+1 == len(finalT):
                        break
                    if j!= 9:
                        combined_str += ","
                if isbottom:
                    combined_str += ",bottom"
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                    message_chain=MessageChain(eval(combined_str)))
                combined_list.append(b1)

            logger.info("获取番剧排行成功")
            await bot.send(event, Forward(node_list=combined_list))
        except Exception as  e:
            logger.error(e)
            await bot.send(event,"获取番剧信息失败，请稍后再试")

    @bot.on(GroupMessage)
    async def bangumi_calendar(event: GroupMessage):               
        if str(event.message_chain)=="bangumi今日放送":
            url = "https://www.bangumi.app/calendar/today"
            path = "data/pictures/cache/today-"
        elif str(event.message_chain)=="bangumi周表":
            #url = "https://api.bgm.tv/calendar"
            url = "https://bgm.tv/calendar"
            path = "data/pictures/cache/week-"
        elif str(event.message_chain)== "bangumi热门":
            url = "https://www.bangumi.app/hot/anime"
            path = "data/pictures/cache/hot-"
        else:
            return
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        path = path+today+".png"   
        try:
            await screenshot_to_pdf_and_png(url,path,1080,3000)
            await bot.send(event,[f"{str(event.message_chain)} {today}：",Image(path=path)], True)  
        except Exception as  e:
            logger.error(e)   
            await bot.send(event,"获取bangumi信息失败，请稍后再试")

    @bot.on(GroupMessage)
    async def bangumi_search(event: GroupMessage):
        if "bangumi查询" in str(event.message_chain):
                #url="https://api.bgm.tv/search/subject/"+str(event.message_chain).split(" ")[1]
                cat="all"
                keywords = str(event.message_chain).replace(" ", "").split("查询")[1]
        elif "查询动画" in str(event.message_chain) or "查询番剧" in str(event.message_chain):
                cat=2
                keywords = str(event.message_chain).replace(" ", "").split("动画")[1]
        elif "查询书籍" in str(event.message_chain):
                cat=1
                keywords = str(event.message_chain).replace(" ", "").split("书籍")[1]
        elif "查询游戏" in str(event.message_chain):
                cat=4
                keywords = str(event.message_chain).replace(" ", "").split("游戏")[1]
        elif "查询音乐" in str(event.message_chain):
                cat=3
                keywords = str(event.message_chain).replace(" ", "").split("音乐")[1]
        elif "查询三次元" in str(event.message_chain):
                cat=6
                keywords = str(event.message_chain).replace(" ", "").split("三次元")[1]
        else:
            return
        logger.info("正在查询：" + keywords)

        url = f"https://bgm.tv/subject_search/{keywords}?cat={cat}"

        path = "data/pictures/cache/"+keywords+".png"
        global searchtask #变量提前，否则可能未定义
        try:
            r=await bangumisearch(url)
            str0 = f"{r[0]}\n请发送编号进入详情页，或发送退出退出查询"
            await screenshot_to_pdf_and_png(url,path,1080,1750)
            await bot.send(event,[str0,Image(path=path)],True)
            global switch

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
                resu=await bangumisearch(url)
                subjectlist=resu[1]
                crtlist=resu[2]
                order = int(str(event.message_chain))
                if str(event.message_chain).startswith("0") and order<=len(crtlist):
                    crt = crtlist[order-1].find("a")["href"]
                    url="https://bgm.tv"+crt
                    logger.info("正在获取"+crt+"详情")
                    path = f"data/pictures/cache/search-{keywords}-0{order}.png"
                    title=crtlist[order-1].find("a").string
                elif 1 <= order <= len(subjectlist):
                    subject = subjectlist[order-1].find("a")["href"]
                    url="https://bgm.tv"+subject
                    logger.info("正在获取"+subject+"详情")
                    path = f"data/pictures/cache/search-{keywords}-{order}.png"
                    title=subjectlist[order-1].find("a").string
                else:
                    await bot.send(event,"查询失败！不规范的操作")
                    searchtask.pop(event.sender.id)
                    return
                try:
                    logger.info("正在获取"+title+"详情")
                    await screenshot_to_pdf_and_png(url,path,1080,1750)
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
