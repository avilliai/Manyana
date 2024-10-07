import asyncio
import json
import httpx
import requests
import os
from mirai.models import ForwardMessageNode, Forward
import datetime
from mirai import GroupMessage, At, Plain,  Mirai, WebSocketAdapter, GroupMessage, Image, At,MessageChain
def Get_Access_Token(): #获取指定Access_Token
    #with httpx.AsyncClient() as client:
        response = httpx.post(f"https://www.ymgal.games/oauth/token?grant_type=client_credentials&client_id=ymgal&client_secret=luna0327&scope=public") #请求的url
        if response.status_code:
            #result = response.json()
            data = response.json()
        access_token = data["access_token"]
        return access_token
def Get_Access_Token_json(access_token,url,params): #在获得公共Access_Token后，访问对应的api获取对应数据
    #with httpx.AsyncClient() as client:
        headers = {
            'Accept': 'application/json;charset=utf-8',
            'Authorization': f'Bearer {access_token}',
            'version': '1'
        }
        response = httpx.get(url, headers=headers,params=params)
        if response.status_code:
            data = response.json()
        return data
def flag_check(flag):#划定需要使用的方式
    if flag ==1:
        url='https://www.ymgal.games/open/archive/search-game'
        #print('精确游戏查询，flag=1')
        return url
    if flag ==2:
        url='https://www.ymgal.games/open/archive/search-game'
        #print('搜索游戏列表，flag=2')
        return url
    if flag ==3:
        url='https://www.ymgal.games/open/archive'
        #print('gid 查询单个游戏的详情，flag=3')
        return url
    if flag ==4:
        url='https://www.ymgal.games/open/archive'
        #print('orgId 查询机构详情，flag=4')
        return url
    if flag ==5:
        url='https://www.ymgal.games/open/archive'
        #print('cid 查询角色详情，flag=5')
        return url
    if flag ==6:
        url='https://www.ymgal.games/open/archive/game'
        #print('orgId 查询机构下的游戏，flag=6')
        return url
    if flag ==7:
        url='https://www.ymgal.games/open/archive/game'
        #print('查询日期区间内发行的游戏，flag=7')
        return url
    if flag ==8:
        url='https://www.ymgal.games/open/archive/random-game'
        #print('随机游戏，flag=8')
        return url
def params_check(flag,keyword=None,releaseStartDate=None,releaseEndDate=None):#确定不同方式下的请求头以及内容
    if flag ==1:
        params = {
            "mode": "accurate",
            "keyword": f"{keyword}",
            "similarity": "70"
        }
        return params
    if flag ==2:
        params = {
            "mode": "list",
            "keyword": f"{keyword}",
            "pageNum": "1",
            "pageSize": "20"
        }
        return params
    if flag ==3:
        params = {
            "gid": f"{keyword}"
        }
        return params
    if flag ==4:
        params = {
            "orgId": f"{keyword}"
        }
        return params
    if flag ==5:
        params = {
            "cid": f"{keyword}"
        }
        return params
    if flag ==6:
        params = {
            "orgId": f"{keyword}"
        }
        return params
    if flag ==7:
        params = {
            "releaseStartDate": f"{releaseStartDate}",
            "releaseEndDate": f"{releaseEndDate}"
        }
        return params
    if flag ==8:
        params = {
            "num": "1"
        }
        return params
def get_game_image(url,filepath):#将图片下载到本地
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    response = requests.get(url,)
    if response.status_code == 200:
        filename = url.split('/')[-1]
        #print(filename)
        img_path = os.path.join(filepath, filename)
        #print(img_path)
        with open(img_path, 'wb') as f:
            f.write(response.content)
        print("图片已下载并保存为 {}".format(img_path))
        return img_path
    else:
        print(f"下载失败")
        return None
def remove_game_image(file_path):#图片删除函数
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"文件 '{file_path}' 已删除。")
    else:
        print(f"文件 '{file_path}' 不存在。")
def context_assemble(json_check):#简单来说就是解析json，然后造文本
    context=''
    if 'gid' in json_check:#这里是为了当遇到本月新作这类多个gal时减少负担，在非多个中用不到
        if 'name' in json_check:
            name = json_check['name']
            context += f"{name}|"
        if 'chineseName' in json_check:
            chineseName = json_check['chineseName']
            context += f"{chineseName}"
        context += f"\n"
        if 'gid' in json_check:
            gid = json_check['gid']
            context += f"gid:{gid}|"
        if 'haveChinese' in json_check:
            haveChinese = json_check['haveChinese']
            context += f"是否汉化：{haveChinese}|"
        if 'releaseDate' in json_check:
            releaseDate = json_check['releaseDate']
            context += f"发售日期：{releaseDate}|"
        if 'state' in json_check:
            state = json_check['state']
            context += f"state：{state}|"
        if 'mainName' in json_check:
            mainName = json_check['mainName']
            context += f"mainName：{mainName}|"
        if 'freeze' in json_check:
            freeze = json_check['freeze']
            context += f"标识状态：{freeze}|"
        return context
        pass
    else:
        if 'org' in json_check['data']:#由data内容确定json中对应字块所在位置
            state_check='org'
        elif 'game' in json_check['data']:
            state_check='game'
        elif 'character' in json_check['data']:
            state_check='character'
        else:
            pass
        if 'org' in json_check['data'] or 'game' in json_check['data'] or 'character' in json_check['data']:
            if 'name' in json_check['data'][state_check]:
                name = json_check['data'][state_check]['name']
                context += f"{name}|"
            if 'chineseName' in json_check['data'][state_check]:
                chineseName = json_check['data'][state_check]['chineseName']
                context += f"{chineseName}"
            context += f"\n"
            if 'restricted' in json_check['data'][state_check]:
                restricted = json_check['data'][state_check]['restricted']
                context += f"限制级：{restricted}|"
            if 'state' in json_check['data'][state_check]:
                state = json_check['data'][state_check]['state']
                context += f"状态：{state}|"
            if 'developerId' in json_check['data'][state_check]:
                developerId = json_check['data'][state_check]['developerId']
                developer_name = developers_check(developerId)
                if developer_name:
                    context += f"开发商：{developer_name}|"
            if 'country' in json_check['data'][state_check]:
                country_check = json_check['data'][state_check]['country']
                if country_check:
                    context += f"所属：{country_check}|"
            if 'releaseDate' in json_check['data'][state_check]:
                releaseDate = json_check['data'][state_check]['releaseDate']
                context += f"发布时间：{releaseDate}|"
            if 'introduction' in json_check['data'][state_check]:
                introduction = json_check['data'][state_check]['introduction']
                context += f"\n简介：{introduction}\n"
            context += f"\n"
            if 'developerId' in json_check['data'][state_check]:
                developerId = json_check['data'][state_check]['developerId']
                context += f"游戏品牌机构orgId：{developerId}\n"
            if 'orgId' in json_check['data'][state_check]:
                orgId_check = json_check['data'][state_check]['orgId']
                context += f"游戏品牌机构orgId：{orgId_check}\n"
            if 'haveChinese' in json_check['data'][state_check]:
                haveChinese = json_check['data'][state_check]['haveChinese']
                context += f"是否有中文：{haveChinese}\n"
            if 'gid' in json_check['data'][state_check]:
                gid = json_check['data'][state_check]['gid']
                context += f"游戏档案gid：{gid}\n"
            if 'website' in json_check["data"][state_check]:
                context += f"相关网址：\n"
                website_count = len(json_check["data"][state_check]["website"])
                for i in range(website_count):
                    if "title" in json_check['data'][state_check]['website'][i]:
                        link=json_check['data'][state_check]['website'][i]['link']
                        title = json_check['data'][state_check]['website'][i]['title']
                        context += f"{title}：{link}\n"
                        if "pid" in json_check['data'][state_check]['website'][i]:
                            pid = json_check['data'][state_check]['website'][i]['pid']
                            context += f"，PID：{pid}\n"
                    else:
                        continue
            if 'characters' in json_check["data"][state_check]:
                context += f"\n游戏角色：\n"
                characters_count = len(json_check["data"][state_check]["characters"])
                for i in range(characters_count):
                    if "cid" in json_check['data'][state_check]['characters'][i]:
                        cid = json_check['data'][state_check]['characters'][i]['cid']
                        if "cvId" in json_check['data'][state_check]['characters'][i]:
                            cvId = json_check['data'][state_check]['characters'][i]['cvId']
                        characterPosition = json_check['data'][state_check]['characters'][i]['characterPosition']
                        if int(characterPosition) == 1:
                            characterPosition_check='男'
                        elif int(characterPosition) == 2:
                            characterPosition_check='女'
                        elif int(characterPosition) == 3:
                            characterPosition_check='扶她'
                        else:
                            characterPosition_check = '未知'

                        character_name = character_check(cid)
                        if character_name:
                            #context += f"开发商：{developer_name}|"
                            context += f"角色：{character_name}，cid：{cid}，CVid：{cvId}，性别：{characterPosition_check}\n"

                pass
            if 'staff' in json_check["data"][state_check]:
                context += f"\n"
                context += f"Staff职员表：\n"
                staff_count = len(json_check["data"][state_check]["staff"])
                for i in range(staff_count):
                    if "sid" in json_check['data'][state_check]['staff'][i]:
                        empName=json_check['data'][state_check]['staff'][i]['empName']
                        jobName = json_check['data'][state_check]['staff'][i]['jobName']
                        context += f"{jobName}：{empName}："
                        if "pid" in json_check['data'][state_check]['staff'][i]:
                            pid = json_check['data'][state_check]['staff'][i]['pid']
                            context += f"，PID：{pid}\n"
                    else:
                        continue



            if 'publishTime' in json_check['data'][state_check]:
                publishTime = json_check['data'][state_check]['publishTime']


    return context
def developers_check(keyword):#在它的gal查询api返回中没有对应开发商以及角色，所以另写一个函数用以替换原本的数字
    name=None
    flag = 4
    keyword = str(keyword)
    url = flag_check(flag)
    params = params_check(flag, keyword)
    access_token = Get_Access_Token()
    json_check = Get_Access_Token_json(access_token, url, params)
    #print(json_check)
    name = json_check['data']['org']['name']
    if 'chineseName' in json_check['data']['org']:
        name=json_check['data']['org']['chineseName']
    #print(name)
    return name
def character_check(keyword):#此函数同上
    name = None
    flag = 5
    keyword = str(keyword)
    url = flag_check(flag)
    params = params_check(flag, keyword)
    access_token = Get_Access_Token()
    json_check = Get_Access_Token_json(access_token, url, params)
    #print(json_check)
    name = json_check['data']['character']['name']
    # print(name)
    return name


def main(bot, logger):
    @bot.on(GroupMessage)
    async def galgame(event: GroupMessage):
        #暂定标记状态flag：
        # flag：1，精确游戏查询
        # flag：2，游戏列表查询
        # flag：3，gid 查询单个游戏的详情
        # flag：4，orgId 查询机构详情
        # flag：5，cid 查询角色详情
        # flag：6，orgId 查询机构下的游戏
        # flag：7，查询日期区间内发行的游戏
        # flag：8，随机游戏
        flag =0#状态标志
        flag_check_test=0#用以判断最后消息发送状态的标志位
        keyword='10270'#不用管，会被正常覆盖的
        keyword=str(keyword)
        filepath='manshuo_data'#图片存储位置，可以修改成任意需要的位置
        cmList = []
        if "gal" in str(event.message_chain) or "Gal" in str(event.message_chain):#确定flag状态

            access_token = Get_Access_Token()
            if "查询" in str(event.message_chain):
                keyword = str(event.message_chain)
                index = keyword.find("查询")
                if index != -1:
                    keyword = keyword[index + len("查询") :]
                    if ':' in keyword or ' ' in keyword or '：' in keyword:
                        keyword = keyword[+1:]
                        pass
                flag = 2
                if "机构" in str(event.message_chain):
                    flag = 4
                    if "游戏" in str(event.message_chain):
                        flag = 6
                        flag_check_test = 3
                elif "id" in str(event.message_chain):
                    flag = 3
                if "角色" in str(event.message_chain):
                    flag = 5
                logger.info(f'access_token：{access_token}，flag:{flag}，gal查询目标：{keyword}')
        if "新作" in str(event.message_chain) and At(bot.qq) in event.message_chain:#确定flag状态

            flag=7
            month = datetime.datetime.now().date().month
            year = datetime.datetime.now().date().year
            day = datetime.datetime.now().date().day
            if "本日" in str(event.message_chain):
                flag_check_test=3
                date = datetime.date(year, month, day)
                logger.info(f'本日新作查询')
            elif "本月" in str(event.message_chain):
                date = datetime.date(year, month - 1, day)
                flag_check_test = 3
                logger.info(f'本月新作查询')
        if "galgame推荐" == str(event.message_chain) or "Galgame推荐" == str(event.message_chain) or ("随机" in str(event.message_chain) and ("gal" in str(event.message_chain) or "Gal" in str(event.message_chain))):#确定flag状态
            flag = 8
            flag_check_test = 3
            logger.info(f'有玩gal的下头男，galgame推荐开启，张数：1')

        if flag ==2:#以flag状态执行对应的功能
            print('进行gal列表查询')
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = Get_Access_Token()
            json_check = Get_Access_Token_json(access_token, url, params)
            state=json_check['success']
            #print(state)
            if state == True:
                total = json_check["data"]["total"]
                #print(total)
                #print(json_check)
                if total > 1:
                    gal_namelist = ''
                    total=int(total)
                    if total >10:
                        total = 10
                    for i in range(total):
                        data = json_check['data']['result'][i]
                        #print(data)
                        name_check = data["name"]
                        if name_check:
                            if "chineseName" in json_check['data']['result'][i]:
                                name_check = data["chineseName"]
                        gal_namelist += f"{name_check} \n"
                    #print(f'存在多个匹配对象，请精确您的查询目标:\n{gal_namelist}')
                    context=f'存在多个匹配对象，请精确您的查询目标:\n{gal_namelist}'
                    flag_check_test = 1
                elif total == 1:
                    flag = 1
                    data = json_check['data']['result'][0]
                    #print(data)
                    name_check = data["name"]
                    if name_check:
                        if "chineseName" in json_check['data']['result'][0]:
                            name_check = data["chineseName"]
                    #data = json_check['data']['result'][i]
                    keyword=name_check
                    #print(keyword)
            if flag ==1:
                print('进行gal精确查询')
                url = flag_check(flag)
                params = params_check(flag, keyword)
                json_check = Get_Access_Token_json(access_token, url, params)
                #print(json_check)
                state = json_check['success']
                if state == True:
                    context=context_assemble(json_check)
                    mainImg_state = json_check["data"]["game"]["mainImg"]
                    img_path = get_game_image(mainImg_state, filepath)
                    #print(context)
                    pass
            else:
                pass

        if flag ==3:#以flag状态执行对应的功能
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = Get_Access_Token()
            json_check = Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state == True:
                context = context_assemble(json_check)
                #print(context)
                mainImg_state = json_check["data"]["game"]["mainImg"]
                img_path = get_game_image(mainImg_state, filepath)

        if flag ==4:#以flag状态执行对应的功能
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = Get_Access_Token()
            json_check = Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state == True:
                context = context_assemble(json_check)
                #print(context)
                if 'mainImg' in json_check["data"]["org"]:
                    mainImg_state = json_check["data"]["org"]["mainImg"]
                    img_path = get_game_image(mainImg_state, filepath)
                else:
                    state = False

        if flag ==5:#以flag状态执行对应的功能
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = Get_Access_Token()
            json_check = Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state == True:
                context = context_assemble(json_check)
                #print(context)
                mainImg_state = json_check["data"]["character"]["mainImg"]
                img_path = get_game_image(mainImg_state, filepath)

        if flag ==6:#以flag状态执行对应的功能
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = Get_Access_Token()
            json_check = Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state == True:
                data_count = len(json_check["data"])
                if int(data_count) ==0:
                    state = False
                for i in range(data_count):
                    data = json_check['data'][i]
                    context = context_assemble(data)
                    #print(context)
                    mainImg_state = data["mainImg"]
                    img_path = get_game_image(mainImg_state, filepath)
                    s = [Image(path=img_path)]
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(s))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(str(context)))
                    cmList.append(b1)
                #print(context)

        if flag ==7:#以flag状态执行对应的功能
            url = flag_check(flag)
            keyword=True
            #now = datetime.datetime.now()
            now = datetime.datetime.now().date()
            #print(date)
            releaseStartDate = date
            releaseEndDate = now
            params = params_check(flag, keyword,releaseStartDate,releaseEndDate)
            access_token = Get_Access_Token()
            json_check = Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state == True:
                data_count = len(json_check["data"])
                if int(data_count) ==0:
                    state = False
                for i in range(data_count):
                    data = json_check['data'][i]
                    context = context_assemble(data)
                    #print(context)
                    mainImg_state = data["mainImg"]
                    img_path = get_game_image(mainImg_state, filepath)
                    s = [Image(path=img_path)]
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(s))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(str(context)))
                    cmList.append(b1)
                #print(context)

        if flag ==8:#以flag状态执行对应的功能
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = Get_Access_Token()
            json_check = Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                    message_chain=MessageChain('今天的gal推荐，请君过目：'))
            cmList.append(b1)
            if state == True:
                data_count = len(json_check["data"])
                for i in range(data_count):
                    data = json_check['data'][i]
                    context = context_assemble(data)
                    #print(context)
                    mainImg_state = 'https://store.ymgal.games/'+data["mainImg"]
                    #print(mainImg_state)
                    img_path = get_game_image(mainImg_state, filepath)
                    s = [Image(path=img_path)]
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(s))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(str(context)))
                    cmList.append(b1)
                #print(context)


        if flag != 0:#之前的代码中并没有发送消息的函数，将发送消息集中在此处理（
            if state == True:#成功获取后才会发送消息记录
                if flag_check_test == 0:
                    logger.info(f'进入文件发送ing')
                    s = [Image(path=img_path)]
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(s))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(str(context)))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(
                                                '当前菜单：\n1，gal查询\n2，gid_gal单个游戏详情查询\n3，orgId_gal机构详情查询\n4，cid_gal游戏角色详情查询\n5，orgId_gal机构下的游戏查询\n6，本月新作，本日新作（单此一项请艾特bot食用\n7，galgame推荐'))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(
                                                '该功能由YMGalgame API实现，支持一下谢谢喵\n本功能由“漫朔”开发\n部分功能还在完善，欢迎催更'))
                    cmList.append(b1)
                    await bot.send(event, Forward(node_list=cmList))
                    pass
                elif flag_check_test == 1:#详情见flag=1时的context，此处是多个匹配项存在
                    await bot.send(event, f'{context}')
                elif flag_check_test == 3:#此处是多个gal项目存在，进行一并发送
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(
                                                '当前菜单：\n1，gal查询\n2，gid_gal单个游戏详情查询\n3，orgId_gal机构详情查询\n4，cid_gal游戏角色详情查询\n5，orgId_gal机构下的游戏查询\n6，本月新作，本日新作（单此一项请艾特bot食用\n7，galgame推荐'))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(
                                                '该功能由YMGalgame API实现，支持一下谢谢喵\n本功能由“漫朔”开发\n部分功能还在完善，欢迎催更'))
                    cmList.append(b1)
                    await bot.send(event, Forward(node_list=cmList))
                    pass
            else:
                await bot.send(event, f'好像暂时找不到你说的gal或公司欸~')







