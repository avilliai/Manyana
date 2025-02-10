# -*- coding: utf-8 -*-
import asyncio
import datetime
import json
import os
import random
import re

import yaml
from mirai.models import ForwardMessageNode, Forward

from plugins.extraParts import get_game_image, sort_yaml, manage_group_status

_task = None
from mirai import GroupMessage, Image, Startup, Shutdown,MessageChain
import requests


def main(bot, logger):
    with open('config.json', 'r', encoding='utf-8') as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)
    config = data
    botName = str(config.get('botName'))
    master = int(config.get('master'))
    mainGroup = int(config.get("mainGroup"))
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controllerResult = yaml.load(f.read(), Loader=yaml.FullLoader)
    wifePrefix = controllerResult.get("图片相关").get("wifePrefix")
    filepath = 'data/pictures/wife_you_want_img'
    directory_img_check = 'data/pictures/wife_you_want_img/today_wife'
    try:
        files_img_check = os.listdir(directory_img_check)
        files_img_check = [f for f in files_img_check if os.path.isfile(os.path.join(directory_img_check, f))]
        logger.info("今日老婆列表读取完毕")
    except Exception:
        files_img_check=None
        logger.info("今日老婆本地数据为空，尝试使用网络图片")

    @bot.on(GroupMessage)#透群友合集
    async def today_wife(event: GroupMessage):
        if str(event.message_chain).startswith("今"):
            if ('今日' in str(event.message_chain) or '今天' in str(event.message_chain) or '今日' in str(event.message_chain)) and '老婆' in str(event.message_chain):
                logger.info("今日老婆开启！")
                file_path_check = 'data/pictures/wife_you_want_img'
                if not os.path.exists(file_path_check):
                    os.makedirs(file_path_check)
                if '张' in str(event.message_chain) or '个' in str(event.message_chain) or '位' in str(
                        event.message_chain):
                    cmList = []
                    context = str(event.message_chain)
                    name_id_number = re.search(r'\d+', context)
                    if name_id_number:
                        number = int(name_id_number.group())
                        if number > 5:
                            await bot.send(event, '数量过多，渣男！！！！')
                        else:
                            if files_img_check is None:
                                for i in range(number):
                                    headers = {'Referer': 'https://weibo.com/'}
                                    response = requests.get(f'https://api.iw233.cn/api.php?sort=top', headers=headers)
                                    with open(f'data/pictures/wife_you_want_img/today_wife_{i}.jpg', 'wb') as file:
                                        file.write(response.content)
                                    img_path = f'data/pictures/wife_you_want_img/today_wife_{i}.jpg'
                                    logger.info(f"获取到老婆图片地址{img_path}")
                                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                            message_chain=MessageChain(Image(path=img_path)))
                                    cmList.append(b1)
                                await bot.send(event, Forward(node_list=cmList))
                            else:
                                count_number = len(files_img_check)
                                for i in range(number):
                                    rnum1 = random.randint(0, count_number - 1)
                                    img_rnum = files_img_check[rnum1]
                                    img_path = os.path.join(directory_img_check, img_rnum)
                                    logger.info(f"获取到老婆图片地址{img_path}")
                                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                            message_chain=MessageChain(Image(path=img_path)))
                                    cmList.append(b1)
                                await bot.send(event, Forward(node_list=cmList))
                else:
                    if files_img_check is None:
                        headers = {'Referer': 'https://weibo.com/'}
                        response = requests.get(f'https://api.iw233.cn/api.php?sort=top', headers=headers)
                        with open('data/pictures/wife_you_want_img/today_wife.jpg', 'wb') as file:
                            file.write(response.content)
                        img_path = 'data/pictures/wife_you_want_img/today_wife.jpg'
                    else:
                        count_number = len(files_img_check)
                        rnum1 = random.randint(0, count_number - 1)
                        img_rnum = files_img_check[rnum1]
                        img_path = os.path.join(directory_img_check, img_rnum)

                    logger.info(f"获取到老婆图片地址{img_path}")
                    s = [Image(path=img_path)]
                    await bot.send(event, s)

    @bot.on(GroupMessage)#透群友合集
    async def wife_you_want(event: GroupMessage):
        if f'{wifePrefix}' in str(event.message_chain):#前置触发词
            target_id_aim = None
        #if '/' in str(event.message_chain):#前置触发词
            flag_persona = 0
            flag_aim = 0
            if '透群主' in str(event.message_chain):
                flag_persona=1
                check='OWNER'
                target_group = int(event.group.id)
                #from_id = int(event.sender.id)
                if manage_group_status(f"{target_group}_owner"):
                    #print('群主记录本地存在，尝试读取')
                    target_id_aim=manage_group_status(f"{target_group}_owner")
                    flag_aim = 1
                else:
                    flag_aim = 0
                pass
            elif '透管理' in str(event.message_chain):
                flag_persona = 2
                check = 'ADMINISTRATOR'
                pass
            elif '透群友' in str(event.message_chain):
                flag_persona = 3
                pass
            elif '娶群友' in str(event.message_chain):
                flag_persona = 4
                from_id = int(event.sender.id)
                if manage_group_status(from_id) :
                    target_group = int(event.group.id)
                    target_id_aim=manage_group_status(from_id)
                    flag_aim = 1
                else:
                    flag_aim = 0
                pass
            elif '离婚' in str(event.message_chain):
                from_id = int(event.sender.id)
                if manage_group_status(from_id):
                    manage_group_status(from_id,False)
                    manage_group_status(f'{from_id}_name', False)
                    await bot.send(event, '离婚啦，您现在是单身贵族咯~')
            else:
                flag_persona=0

            if flag_persona == 3 or flag_persona == 4:
                context=str(event.message_chain)
                name_id_number=re.search(r'\d+', context)
                if name_id_number:
                    if flag_aim == 1:
                        await bot.send(event, '渣男！吃着碗里的想着锅里的！', True)
                        flag_persona = 0
                        flag_aim = 0
                    else:
                        number = int(name_id_number.group())
                        target_id_aim=number
                        #print(target_id_aim)
                        rnum1 = random.randint(1, 10)
                        if rnum1 > 3:
                            #await bot.send(event, '不许瑟瑟！！！！', True)
                            target_group = int(event.group.id)
                            group_member_check = await bot.get_group_member(target_group, target_id_aim)
                            #print(group_member_check)
                            if group_member_check:
                                flag_aim=1
                    #print(rnum1)
                    #print(flag_aim)



                rnum0 = random.randint(1, 10)
                if rnum0 == 1:
                    await bot.send(event, '不许瑟瑟！！！！')
                    flag_persona = 0

            if flag_persona != 0:
                logger.info("透群友任务开启")

                friendlist = []
                target_name = None
                target_id = None
                target_img = None
                # target_nikenamne=None
                from_name = str(event.sender.member_name)
                from_id = int(event.sender.id)
                #flag_aim = 0
                target_group = int(event.group.id)


                if flag_aim == 1 :
                    target_id=target_id_aim
                else:
                    friendlist_get = await bot.member_list(target_group)
                    data = friendlist_get.json()
                    data = json.loads(data)
                    #print(data)
                    data_count = len(data["data"])
                    if flag_persona==2 or flag_persona==3 or flag_persona==4:
                        if data_count > 500:
                            await bot.send(event, '抱歉，群聊人数过多，bot服务压力过大，仅开放/透群主功能，谢谢')
                            return
                    data_check_number=0
                    for i in range(data_count):
                        data_test=None
                        data_check = data['data'][i]['permission']
                        #print(data_check)
                        if flag_persona == 1 or flag_persona == 2:
                            if data_check == check:
                                data_test = data['data'][i]['id']
                        elif flag_persona == 3 or flag_persona == 4:
                            data_test = data['data'][i]['id']
                        if data_test is not None:
                            friendlist.append(data_test)
                        if flag_persona == 1:
                            if data_check == 'OWNER':
                                data_check_number=1
                            if data_check_number==1:
                                break
                    number_target = len(friendlist)
                    target_number = random.randint(1, number_target)
                    target_id = friendlist[target_number - 1]
                if flag_aim == 0 and flag_persona == 1:
                    manage_group_status(f"{target_group}_owner",target_id)
                #print(target_id)
                logger.info(f'群：{target_group}，透群友目标：{target_id}')
                group_member_check = await bot.get_group_member(target_group, target_id)
                #print(group_member_check)
                # target_id = extract_between_symbols(str(group_member_check), 'id=', ' member')
                if manage_group_status(f'{from_id}_name') and flag_persona == 4:
                    target_name=manage_group_status(f'{from_id}_name')
                else:
                    group_member_check = group_member_check.json()
                    group_member_check = json.loads(group_member_check)
                    target_name=group_member_check['member_name']
                    #target_name = extract_between_symbols(str(group_member_check), 'member_name=', ' permission')
                if flag_persona == 4:
                    if manage_group_status(from_id):
                        flag_aim = 0
                    else:
                        manage_group_status(from_id, target_id)
                        manage_group_status(f'{from_id}_name', target_name)

                # 下面是获取对应人员头像的代码
                target_img_url = f"https://q1.qlogo.cn/g?b=qq&nk={target_id}&s=640"  # QQ头像 URL 格式
                try:
                    target_img_path = get_game_image(target_img_url, filepath, target_id)
                except Exception:
                    await bot.send(event, '(˃ ⌑ ˂ഃ )诶呀——腾子请求限制，请再试一次吧')
                    return
                from_name=str(from_name)
                target_name = str(target_name)
                target_times=manage_group_status(f'{target_name} ({target_id})',True,target_group=target_group,file_name='wife_you_want_week_check_target.yaml')
                from_times=manage_group_status(f'{from_name} ({from_id})',True,target_group=target_group,file_name='wife_you_want_week_check_from.yaml')

            if flag_persona == 1:
                if manage_group_status(f'{target_id}_ower_time'):
                    times = int(manage_group_status(f'{target_id}_ower_time'))
                    times += 1
                    manage_group_status(f'{target_id}_ower_time', times)
                else:
                    times = 1
                    manage_group_status(f'{target_id}_ower_time', 1)
                await bot.send_group_message(event.sender.group.id,
                                             [f'@{from_name} 恭喜你涩到群主！！！！',
                                              Image(path=target_img_path),
                                              f'群主【{target_name}】今天这是第{times}次被透了呢'])
            if flag_persona == 2:
                await bot.send_group_message(event.sender.group.id,
                                             [f'@{from_name} 恭喜你涩到管理！！！！',
                                              Image(path=target_img_path),
                                              f'【{target_name}】 ({target_id})哒！'])
            if flag_persona == 3:
                if flag_aim == 1:
                    await bot.send_group_message(event.sender.group.id,
                                                 [f'@{from_name} 恭喜你涩到了群友！！！！',
                                                  Image(path=target_img_path),
                                                  f'【{target_name}】 ({target_id})哒！'])
                else:
                    await bot.send_group_message(event.sender.group.id,
                                                 [f'@{from_name} 今天你的色色对象是',
                                                  Image(path=target_img_path),
                                                  f'【{target_name}】 ({target_id})哒！'])
            if flag_persona == 4:
                if flag_aim == 1:
                    await bot.send_group_message(event.sender.group.id,
                                                 [f'@{from_name} 恭喜你娶到了群友！！！！',
                                                  Image(path=target_img_path),
                                                  f'【{target_name}】 ({target_id})哒！'])
                else:
                    await bot.send_group_message(event.sender.group.id,
                                                 [f'@{from_name} 今天你的结婚对象是',
                                                  Image(path=target_img_path),
                                                  f'【{target_name}】 ({target_id})哒！'])

            if '记录' in str(event.message_chain) and (
                    '色色' in str(event.message_chain) or '瑟瑟' in str(event.message_chain) or '涩涩' in str(
                    event.message_chain)):
                target_group = int(event.group.id)
                cmList = []
                if '本周' in str(event.message_chain) or '每周' in str(event.message_chain) or '星期' in str(event.message_chain):
                    logger.info(f'本周色色记录启动！')
                    type_context='以下是本周色色记录：'
                    target_context,target_king = sort_yaml('wife_you_want_week_check_target.yaml',target_group,'week')
                    from_context,from_king = sort_yaml('wife_you_want_week_check_from.yaml',target_group,'week')
                elif '本月' in str(event.message_chain) or '月份' in str(event.message_chain) or '月' in str(event.message_chain):
                    logger.info(f'本周色色记录启动！')
                    type_context = '以下是本月色色记录：'
                    target_context,target_king = sort_yaml('wife_you_want_week_check_target.yaml',target_group,'moon')
                    from_context,from_king = sort_yaml('wife_you_want_week_check_from.yaml',target_group,'moon')
                else:
                    logger.info(f'本日色色记录启动！')
                    type_context = '以下是本日色色记录：'
                    target_context,target_king = sort_yaml('wife_you_want_week_check_target.yaml',target_group)
                    from_context,from_king = sort_yaml('wife_you_want_week_check_from.yaml',target_group)
                if '没有任何一位' in target_context or '没有任何一位' in from_context:
                    await bot.send(event, f'{target_context}')
                else:
                    target_king_name, inside_with_parens = target_king.split(" (")
                    target_king_id = inside_with_parens.rstrip(")")  # 去除右括号
                    from_king_name, inside_with_parens = from_king.split(" (")
                    from_king_id = inside_with_parens.rstrip(")")  # 去除右括号
                    target_img_url = f"https://q1.qlogo.cn/g?b=qq&nk={target_king_id}&s=640"  # QQ头像 URL 格式
                    from_img_url = f"https://q1.qlogo.cn/g?b=qq&nk={from_king_id}&s=640"
                    target_img_path = get_game_image(target_img_url, filepath, target_king_id)
                    from_img_path = get_game_image(from_img_url, filepath, from_king_id)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(str(type_context)))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain([f'被群友透最多的人诞生了！！',
                                                          Image(path=target_img_path),
                                                          f'是【{target_king_name}】 ({target_king_id})哦~']))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(f'群友被透的次数如下哦：\n{target_context}'))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain([f'群最涩色魔，透群友大王出现了！',
                                                          Image(path=from_img_path),
                                                          f'【{from_king_name}】 ({from_king_id})的说~~']))
                    cmList.append(b1)
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(f'群友透别人的次数如下哦：\n{from_context}'))
                    cmList.append(b1)
                    await bot.send(event, Forward(node_list=cmList))


    @bot.on(Startup)#部分文件指定删除，用以实现循环
    async def start_scheduler(_):
        async def timer():
            today_finished = False  # 设置变量标识今天是会否完成任务，防止重复发送
            while True:

                await asyncio.sleep(1)
                now = datetime.datetime.now()
                today = datetime.datetime.today()
                weekday = today.weekday()
                month = datetime.datetime.now().month
                day = datetime.datetime.now().day
                if now.hour == 00 and now.minute == 00 and not today_finished:  # 每天早上 7:30 发送早安
                    file_path_check="data/pictures/wife_you_want_img/wife_you_want.yaml"
                    if os.path.exists(file_path_check):
                        os.remove(file_path_check)

                    file_path="data/pictures/wife_you_want_img/wife_you_want_week_check_target.yaml"
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            users_data = yaml.safe_load(file) or {}
                            type='day'
                            users_data[type] = {}
                        if int(weekday) == 0:
                            type = 'week'
                            users_data[type] = {}
                        if int(day) == 1:
                            type = 'moon'
                            users_data[type] = {}
                        with open(file_path, 'w') as file:
                            yaml.safe_dump(users_data, file)
                    file_path="data/pictures/wife_you_want_img/wife_you_want_week_check_from.yaml"
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            users_data = yaml.safe_load(file) or {}
                            type='day'
                            users_data[type] = {}
                        if int(weekday) == 0:
                            type = 'week'
                            users_data[type] = {}
                        if int(day) == 1:
                            type = 'moon'
                            users_data[type] = {}
                        with open(file_path, 'w') as file:
                            yaml.safe_dump(users_data, file)
                    print('娶群友事件已重置')
                    today_finished = True
                if now.hour == 00 and now.minute == 1:
                    today_finished = False  # 早上 7:31，重置今天是否完成任务的标识

        global _task
        _task = asyncio.create_task(timer())

    @bot.on(Shutdown)
    async def stop_scheduler(_):
        # 退出时停止定时任务
        if _task and not _task.done():
            _task.cancel()






        
      