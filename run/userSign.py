# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import time
import sys
from asyncio import sleep

import requests
import yaml

from mirai import Image as Im, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

import plugins

from PIL import ImageFont, ImageFilter
from PIL import ImageDraw
from mirai import GroupMessage, At


from PIL import Image

from plugins.RandomStr import random_str
from plugins.imgDownload import dict_download_img
from plugins.weatherQuery import querys
from run.aiReply import CListen

lucky = [
"——中吉——\n天上有云飘过的日子，天气令人十分舒畅。\n工作非常顺利，连午睡时也会想到好点子。\n突然发现，与老朋友还有其他的共同话题…\n——每一天，每一天都要积极开朗地度过——",
"——中吉——\n十年磨一剑，今朝示霜刃。\n恶运已销，身临否极泰来之时。\n苦练多年未能一显身手的才能，\n现今有了大展身手的极好机会。\n若是遇到阻碍之事，亦不必迷惘，\n大胆地拔剑，痛快地战斗一番吧。",
"——大吉——\n会起风的日子，无论干什么都会很顺利的一天。\n周围的人心情也非常愉快，绝对不会发生冲突，\n还可以吃到一直想吃，但没机会吃的美味佳肴。\n无论是工作，还是旅行，都一定会十分顺利吧。\n那么，应当在这样的好时辰里，一鼓作气前进…",
"——大吉——\n宝剑出匣来，无往不利。出匣之光，亦能照亮他人。\n今日能一箭射中空中的猎物，能一击命中守卫要害。\n若没有目标，不妨四处转转，说不定会有意外之喜。\n同时，也不要忘记和倒霉的同伴分享一下好运气哦。",
"——大吉——\n失而复得的一天。\n原本以为石沉大海的事情有了好的回应，\n原本分道扬镳的朋友或许可以再度和好，\n不经意间想起了原本已经忘记了的事情。\n世界上没有什么是永远无法挽回的，\n今天就是能够挽回失去事物的日子。",
"——大吉——\n浮云散尽月当空，逢此签者皆为上吉。\n明镜在心清如许，所求之事心想则成。\n合适顺心而为的一天，不管是想做的事情，\n还是想见的人，现在是行动起来的好时机。",
"——吉——\n明明没有什么特别的事情，却感到心情轻快的日子。\n在没注意过的角落可以找到本以为丢失已久的东西。\n食物比平时更加鲜美，路上的风景也令人眼前一亮。\n——这个世界上充满了新奇的美好事物——",
"——吉——\n枯木逢春，正当万物复苏之时。\n陷入困境时，能得到解决办法。\n举棋不定时，会有贵人来相助。\n可以整顿一番心情，清理一番家装，\n说不定能发现意外之财。",
"——吉——\n一如既往的一天。身体和心灵都适应了的日常。\n出现了能替代弄丢的东西的物品，令人很舒心。\n和常常遇见的人关系会变好，可能会成为朋友。\n——无论是多寻常的日子，都能成为宝贵的回忆——",
"——末吉——\n云遮月半边，雾起更迷离。\n抬头即是浮云遮月，低头则是浓雾漫漫。\n虽然一时前路迷惘，但也会有一切明了的时刻。\n现下不如趁此机会磨炼自我，等待拨云见皎月。",
"——末吉——\n空中的云层偏低，并且仍有堆积之势，\n不知何时雷雨会骤然从头顶倾盆而下。\n但是等雷雨过后，还会有彩虹在等着。\n宜循于旧，守于静，若妄为则难成之。",
"——末吉——\n平稳安详的一天。没有什么令人难过的事情会发生。\n适合和久未联系的朋友聊聊过去的事情，一同欢笑。\n吃东西的时候会尝到很久以前体验过的过去的味道。\n——要珍惜身边的人与事——",
"——末吉——\n气压稍微有点低，是会令人想到遥远的过去的日子。\n早已过往的年轻岁月，与再没联系过的故友的回忆，\n会让人感到一丝平淡的怀念，又稍微有一点点感伤。\n——偶尔怀念过去也很好。放松心情面对未来吧——",
"——凶——\n珍惜的东西可能会遗失，需要小心。\n如果身体有不适，一定要注意休息。\n在做出决定之前，一定要再三思考。",
"——凶——\n隐约感觉会下雨的一天。可能会遇到不顺心的事情。\n应该的褒奖迟迟没有到来，服务生也可能会上错菜。\n明明没什么大不了的事，却总感觉有些心烦的日子。\n——难免有这样的日子——",
"——大凶——\n内心空落落的一天。可能会陷入深深的无力感之中。\n很多事情都无法理清头绪，过于钻牛角尖则易生病。\n虽然一切皆陷于低潮谷底中，但也不必因此而气馁。\n若能撑过一时困境，他日必另有一番作为。"
]
def main(bot,api_KEY,master,config,logger):
    newLoop = asyncio.new_event_loop()
    listen = CListen(newLoop)
    listen.setDaemon(True)
    listen.start()
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
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    masterPermissionDays=result1.get("masterPermissionDays")
    userSelfPermissonDays=result1.get("userSelfPermissonDays")
    trustDays = result1.get("trustDays")
    with open('data/signs.yaml', 'r', encoding='utf-8') as f:
        signstoday = yaml.load(f.read(), Loader=yaml.FullLoader)
    global haveSign,tod
    tod=str(datetime.date.today())
    if tod in signstoday:
        haveSign=signstoday.get(tod)
    else:
        haveSign=[123]
        paddd={str(tod):haveSign}
        with open('data/signs.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(paddd, file, allow_unicode=True)
    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        global haveSign,tod
        if '签到' ==str(event.message_chain):
            logger.info("接收来自："+event.sender.member_name+"("+str(event.sender.id)+") 的签到指令")
            if str(event.sender.id) in userdict.keys():
                data=userdict.get(str(event.sender.id))
                signOrNot = data.get('ok')
                time114514 = str(datetime.datetime.now().strftime('%Y-%m-%d'))
                if signOrNot!=time114514 or event.sender.id==master:
                    city = data.get('city')
                    startTime = data.get('st')
                    times = str(int(data.get('sts')) + 1)
                    if times==trustDays:
                        await bot.send(event,'已对您开启邀请bot加群与私聊chatglm权限',True)
                    exp = str(int(data.get('exp')) + random.randint(1, 20))
                    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    id = data.get('id')
                    weather = await querys(city, api_KEY)
                    logger.info(weather)
                    imgurl = get_user_image_url(event.sender.id)
                    logger.info("制作签到图片....")
                    await bot.send(event,f"{event.sender.member_name}是今天第{len(haveSign)}个签到的，正在制作签到图片.....")
                    asyncio.run_coroutine_threadsafe(fuff(imgurl, id, weather, nowTime, times, exp, startTime,event),newLoop)

                    logger.info("完成，发送签到图片")
                    data['sts'] = times
                    data['exp'] = exp
                    data['ok'] = time114514
                    userdict[str(event.sender.id)] = data
                    logger.info("启动天气查询")
                    logger.info("更新用户数据中")
                    with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(userdict, file, allow_unicode=True)
                    haveSign.append(event.sender.id)
                    paddd = {str(tod): haveSign}
                    with open('data/signs.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(paddd, file, allow_unicode=True)
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
        global newUser,haveSign,tod
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
            imgurl = get_user_image_url(event.sender.id)
            logger.info("制作签到图片....")
            await bot.send(event, f"{event.sender.member_name}是今天第{len(haveSign)}个签到的，正在制作签到图片.....")
            asyncio.run_coroutine_threadsafe(fuff(imgurl, id, weather, nowTime, times, exp, startTime,event),newLoop)

            userdict[str(event.sender.id)] = data
            logger.info("更新用户数据中")
            with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(userdict, file, allow_unicode=True)
            haveSign.append(event.sender.id)
            paddd = {str(tod): haveSign}
            with open('data/signs.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(paddd, file, allow_unicode=True)
    async def fuff(imgurl, id, weather, nowTime, times, exp, startTime,event):
        path = await signPicMaker(imgurl, id, weather, nowTime, times, exp, startTime)
        logger.info("完成，发送签到图片")
        await bot.send(event, Im(path=path), True)
    @bot.on(Startup)
    async def upddddd(event: Startup):
        while True:
            await sleep(60)
            with open('data/signs.yaml', 'r', encoding='utf-8') as f:
                signstoday = yaml.load(f.read(), Loader=yaml.FullLoader)
            global haveSign,tod
            tod = str(datetime.date.today())
            if tod in signstoday:
                haveSign = signstoday.get(tod)
            else:
                haveSign = [123]
                paddd = {str(tod): haveSign}
                with open('data/signs.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(paddd, file, allow_unicode=True)

    @bot.on(GroupMessage)
    async def accessGiver(event:GroupMessage):
        global userdict
        if str(event.message_chain).startswith("授权#") and (event.group.id==mainGroup or event.sender.id==master):
            try:
                if event.sender.id==master:
                    setN=str(masterPermissionDays)
                    fsf=0
                else:
                    if str(event.sender.id)!=str(event.message_chain).split("#")[1]:
                        await bot.send(event,"不匹配的账号，请发送 授权#你自己的QQ")
                        return
                    setN=str(userSelfPermissonDays)
                    fsf=1

            except:
                return

            userId=str(event.message_chain).split("#")[1]
            if userId in userdict:
                data=userdict.get(userId)
                if "selfAdded" in data and fsf==1:
                    await bot.send(event,"拒绝授权，您已为自己授权过",True)
                    return
                data["sts"]=str(int(data.get("sts"))+int(setN))
                if fsf==1:
                    data["selfAdded"]="True"
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

            if event.sender.id==master:
                await bot.send_friend_message(int(userId),"授权完成,开放功能权限。")
            else:
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
    async def check_image_size():
        try:
            image_path = pic()
        except Exception as e:
            logger.error(e)
            image_path="data/pictures/new_sign_Image/9bFIzYz.png"
            return image_path
        size = os.path.getsize(image_path) / (1024 * 1024)
        while size > 6:
            logger.error("过大的图片，重新获取")
            image_path = pic()
            size = os.path.getsize(image_path) / (1024 * 1024)
            if image_path=="data/pictures/new_sign_Image/9bFIzYz.png":
                break
        return image_path
    
    async def signPicMaker(url,ids,weather,nowTime,times,exp,startTime):
        # Load the background image
        bg_path=await check_image_size()
        bg = Image.open(bg_path)

        # Apply blur to the entire background image
        blurred_bg = bg.filter(ImageFilter.GaussianBlur(7))
        margin = 50
        # 创建一个新的内部清晰部分图像，根据原始宽高比计算新尺寸
        # 首先计算缩放比例，确保宽度和高度都不会超过背景的一半减去边距
        scale_factor = min((bg.width // 1.6 - (margin)) / bg.width, (bg.height - (margin)) / bg.height)
        new_width = int(bg.width * scale_factor)
        new_height = int(bg.height * scale_factor)

        # 使用LANCZOS采样方法进行调整大小，并保持原有宽高比
        inner_clear = bg.resize((new_width, new_height), resample=Image.LANCZOS)

        # 计算内部图片的粘贴位置，确保它居中于背景的一边
        paste_x = (bg.width - new_width - int(bg.width * 0.05))
        paste_y = ((bg.height - new_height) // 2) - int(bg.height * 0.05)
        # 使用LANCZOS采样方法进行调整大小

        # 创建一个灰色的矩形填充区域
        gray_color = (169, 169, 169, 128)  # 灰色，128为半透明的alpha值
        draw = ImageDraw.Draw(blurred_bg, 'RGBA')
        left_fill_width = bg.width // 3  # 你可以调整这个宽度
        # 绘制一个半透明的灰色矩形
        draw.rectangle([(0, 0), (left_fill_width, bg.height)], fill=gray_color)

        # Prepare shadow effect
        shadow_width = 10  # Shadow width
        shadow_color = (0, 0, 0, 80)  # Shadow color and transparency
        # Create a shadow image that is larger than the inner clear part to accommodate the shadow
        shadow_image = Image.new('RGBA', (new_width + shadow_width * 2, new_height + shadow_width * 2), shadow_color)
        # Blur the shadow image to create the shadow effect
        shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(shadow_width / 2))

        # Calculate position to paste the shadow
        shadow_x = paste_x - shadow_width
        shadow_y = paste_y - shadow_width

        # Paste the shadow onto the blurred background
        # 使用阴影的透明度通道作为掩码
        blurred_bg.paste(shadow_blurred, (shadow_x, shadow_y), shadow_blurred.split()[3])

        # Paste the inner clear part onto the blurred background with the shadow
        # 如果inner_clear是RGBA模式，使用它的透明度通道作为掩码
        if inner_clear.mode == 'RGBA':
            mask = inner_clear.split()[3]
        else:
            mask = None
        blurred_bg.paste(inner_clear, (paste_x, paste_y), mask)
        # 接下来开始增加图片
        fileName =await userAvatarDownLoad(url)
        # 制底图
        layer = Image.open(fileName)
        layer = layer.resize((int(bg.width * 0.1), int(bg.width * 0.1)), resample=Image.LANCZOS)
        blurred_bg.paste(layer, (int(bg.width * 0.02), int(bg.width * 0.02)))
        tp = blurred_bg
        draw = ImageDraw.Draw(tp)
        wi = int(bg.width * 0.02)
        font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', int(bg.width*0.02))
        draw.text((wi, int(bg.height * 0.25)), (ids.replace("-", "a")), (12, 0, 6), font=font)
        font = ImageFont.truetype('data/fonts/H-TTF-BuMing-B-2.ttf', int(bg.width*0.015))
        draw.text((wi, int(bg.height * 0.35)), "天气："+weather, (12, 0, 6), font=font)
        draw.text((wi, int(bg.height * 0.45)), "当前时间："+nowTime, (12, 0, 6), font=font)
        draw.text((wi, int(bg.height * 0.55)), "签到次数："+times, (12, 0, 6), font=font)
        draw.text((wi, int(bg.height * 0.65)), "注册日："+startTime, (12, 0, 6), font=font)
        font = ImageFont.truetype('data/fonts/H-TTF-BuMing-B-2.ttf', int(bg.width * 0.013))
        draw.text((int(bg.width * 0.015), int(bg.height * 0.75)), random.choice(lucky), (12, 3, 6), font=font)
        # Save the final image
        final_image_path = "data/pictures/cache/"+random_str()+".png"
        blurred_bg.save(final_image_path)

        return final_image_path
    def pic():
        ranpath = random_str()
        try:
            url = "https://api.iw233.cn/api.php?sort=pc"
            # url+="tag=萝莉|少女&tag=白丝|黑丝"
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
                "Referer": "https://weibo.com/"}
            r = requests.get(url, headers=headers).content
            with open("data/pictures/new_sign_Image/" + ranpath + ".png", mode="wb") as f:
                f.write(r)  # 图片内容写入文件
            return "data/pictures/new_sign_Image/" + ranpath + ".png"
        except Exception as e:
            logger.error(e)
            logger.info("使用二号接口")
            try:
                url = 'https://api.yimian.xyz/img'
                params = {
                    'type': 'moe',
                    'size': '1920x1080'
                }
                res = requests.get(url, params=params)
                r = requests.get(res.url).content
                with open("data/pictures/new_sign_Image/" + ranpath + ".png", mode="wb") as f:
                    f.write(r)  # 图片内容写入文件
                return "data/pictures/new_sign_Image/" + ranpath + ".png"
            except Exception as e:
                logger.error(e)
                logger.error("二号接口失效，返回备用图片")
                image_path = "data/pictures/new_sign_Image/9bFIzYz.png"
                return image_path




    def get_user_image_url(qqid):
        return f'https://q4.qlogo.cn/g?b=qq&nk={qqid}&s=640'







