# -*- coding: utf-8 -*-
import json
import os
import datetime
import random
import time
import sys

import yaml

from mirai import Image as Im
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

import plugins

from PIL import ImageFont
from PIL import ImageDraw
from mirai import GroupMessage, At


from PIL import Image

from plugins.RandomStr import random_str
from plugins.imgDownload import dict_download_img
from plugins.weatherQuery import querys


def main(bot,api_KEY,master,config,logger):

    logger.info("签到部分启动完成")
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    global mainGroup
    mainGroup = int(config.get("mainGroup"))
    global userdict
    userdict = data
    logger.info("读取用户数据完成")
    global newUser
    newUser={}

    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        if '签到' ==str(event.message_chain):
            logger.info("接收来自："+event.sender.member_name+"("+str(event.sender.id)+") 的签到指令")
            if str(event.sender.id) in userdict.keys():
                data=userdict.get(str(event.sender.id))
                signOrNot = data.get('ok')
                time114514 = str(datetime.datetime.now().strftime('%Y-%m-%d'))
                if signOrNot!=time114514:
                    city = data.get('city')
                    startTime = data.get('st')
                    times = str(int(data.get('sts')) + 1)
                    if times=='14':
                        await bot.send(event,'词库自动授权完成,发送 开始添加 试试吧',True)
                    exp = str(int(data.get('exp')) + random.randint(1, 20))
                    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    id = data.get('id')
                    data['sts'] = times
                    data['exp'] = exp
                    data['ok'] = time114514
                    userdict[str(event.sender.id)] = data
                    logger.info("启动天气查询")
                    weather = await querys(city,api_KEY)
                    logger.info(weather)
                    logger.info("更新用户数据中")
                    with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(userdict, file, allow_unicode=True)
                    imgurl = get_user_image_url(event.sender.id)
                    logger.info("制作签到图片....")
                    path = await signPicMaker(imgurl, id, weather, nowTime, times, exp, startTime)
                    logger.info("完成，发送签到图片")
                    await bot.send(event, Im(path=path), True)
                else:
                    logger.info("签到过了，拒绝签到")
                    await bot.send(event,'不要重复签到！笨蛋！',True)
            else:
                logger.info("未注册用户"+str(event.sender.id)+"，提醒注册")
                await bot.send(event,'请完善用户信息\n发送 注册#城市名 以完善信息\n例如 注册#通辽',True)
                global newUser
                newUser[str(event.sender.id)]=0

    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        global newUser
        if str(event.sender.id) in newUser.keys():
            newUser.pop(str(event.sender.id))
            logger.info("用户+1："+str(event.sender.member_name)+" ("+str(event.sender.id)+")")
            time114514 = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                city = str(event.message_chain).split('#')[1]

                await bot.send(event, '正在验证城市......，')
                weather = await querys(city,api_KEY)
                await bot.send(event, '成功')
                logger.info("验证城市通过")
            except:
                await bot.send(event,'error，默认执行 注册#通辽 ,随后可发送 修改城市#城市名 进行地区修改')
                city='通辽'
                weather = await querys(city,api_KEY)
                logger.info("城市验证未通过，送进通辽当可汗子民")
            global userdict
            userdict[str(event.sender.id)] = {"city": city, "st": time, "sts": "1", "exp": "0",
                                              "id": "miav-"+random_str(6,'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'),'ok':time114514}
            data = userdict.get(str(event.sender.id))
            city = data.get('city')
            startTime = data.get('st')
            times = str(int(data.get('sts')) + 1)
            exp = str(int(data.get('exp')) + random.randint(1, 20))
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            id = data.get('id')
            data['sts'] = times
            data['exp'] = exp
            data['userName']=event.sender.member_name
            userdict[str(event.sender.id)] = data
            logger.info("更新用户数据中")
            with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(userdict, file, allow_unicode=True)

            imgurl = get_user_image_url(event.sender.id)
            logger.info("制作签到图片....")
            path=await signPicMaker(imgurl,id,weather,nowTime,times,exp,startTime)
            logger.info("完成，发送签到图片")
            await bot.send(event,Im(path=path),True)


    @bot.on(GroupMessage)
    async def accessGiver(event:GroupMessage):
        global userdict
        if str(event.message_chain).startswith("授权#") and (event.group.id==mainGroup or event.sender.id==master):
            try:
                if event.sender.id==master:
                    setN="99"
                else:
                    setN="15"

            except:
                return

            userId=str(event.message_chain).split("#")[1]
            if userId in userdict:
                data=userdict.get(userId)
                data["sts"]=setN
                userdict[userId]=data
            else:
                time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                userdict[userId] = {"city": "通辽", "st": time, "sts": setN, "exp": "0",
                                                  "id": "miav-"+random_str(), 'ok': time}
            logger.info("更新用户数据中")
            with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(userdict, file, allow_unicode=True)
            logger.info("授权"+userId+"完成")
            await bot.send(event,"授权完成,一分钟后数据将完成同步")
            await bot.send_friend_message(int(userId),"授权完成，解锁部分bot权限(一分钟后)")

    @bot.on(GroupMessage)
    async def changeCity(event: GroupMessage):
        if str(event.message_chain).startswith('修改城市#'):
            logger.info("接收城市修改请求")
            city=str(event.message_chain)[5:]
            try:

                data=userdict.get(str(event.sender.id))
                await bot.send(event, '正在验证城市......，')
                weather = await querys(city,api_KEY)
                data['city']=city
                data["id"]="miav-"+random_str(6,'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789')
                await bot.send(event, '成功')
                userdict[str(event.sender.id)] = data
                with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(userdict, file, allow_unicode=True)
            except:
                await bot.send(event,'没有对应的城市数据......，',True)
    async def userAvatarDownLoad(url):
        fileName = dict_download_img(url,dirc="data/pictures/avatars")
        logger.info("头像路径："+fileName)
        touxiang = Image.open(fileName)
        fad = touxiang.resize((450, 450), Image.BICUBIC)
        fad.save(fileName)
        return fileName
    async def signPicMaker(url,id,weather,nowTime,times,exp,startTime):
        fileName=await userAvatarDownLoad(url)
        # 制底图
        layer = Image.open(fileName)

        path="data/pictures/sign_backGround/"+random.choice(os.listdir("data/pictures/sign_backGround"))
        bg = Image.open(path)
        # merge = Image.blend(st, st2, 0.5)
        bg.paste(layer, (120, 147))
        fileName='data/pictures/cache/'+random_str()+".png"
        bg.save(fileName)
        imageFile = fileName
        # 导入数据

        tp = Image.open(imageFile)
        font = ImageFont.truetype('data/fonts/H-TTF-BuMing-B-2.ttf', 110)
        draw = ImageDraw.Draw(tp)
        font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', 115)
        draw.text((423, 743), id, (12, 0, 6), font=font)
        font = ImageFont.truetype('data/fonts/H-TTF-BuMing-B-2.ttf', 73)
        draw.text((2000, 716), weather, (12, 0, 6), font=font)
        draw.text((509, 1419), '当前exp:' + exp, (12, 0, 6), font=font)
        font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', 73)
        draw.text((509, 1090), nowTime.replace("-", "a").replace(":", "b"), (12, 0, 6), font=font)
        draw.text((509, 1243), times.replace("-", "a").replace(":", "b"), (12, 0, 6), font=font)
        draw.text((1395, 1188), startTime.replace("-", "a").replace(":", "b"), (12, 0, 6), font=font)
        fileName = 'data/pictures/cache/' + random_str() + ".png"
        tp.save(fileName)
        return fileName

    def get_user_image_url(qqid):
        return f'https://q4.qlogo.cn/g?b=qq&nk={qqid}&s=640'







