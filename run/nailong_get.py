import random
import httpx
import json
import base64
import asyncio
from concurrent.futures import ThreadPoolExecutor
import yaml
from mirai import GroupMessage
from mirai import Image

from plugins.toolkits import delete_msg
from plugins.nailong11.nailong import main as nailong_main
from plugins.doro.doro import main as doro_main
import asyncio
import base64
import json
import random
from concurrent.futures import ThreadPoolExecutor

import httpx
import yaml
from mirai import GroupMessage
from mirai import Image

from plugins.doro.doro import main as doro_main
from plugins.nailong11.nailong import main as nailong_main
from plugins.toolkits import delete_msg


def main(bot, logger):
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    sets = controller.get("检测")
    chehui1 = sets.get("奶龙撤回")
    mute1=sets.get("奶龙禁言")
    attack1=sets.get("骂奶龙")
    chehui2 = sets.get("doro撤回")
    if_nailong = sets.get("奶龙检测")
    if_doro = sets.get("doro检测")
    mute2=sets.get("doro禁言")
    attack2=sets.get("骂doro")
    async def get_group_member_info(group_id: int, user_id: int):
        url = "http://localhost:3000/get_group_member_info"
        payload = {
            "group_id": group_id,
            "user_id": user_id
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ff',
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

    async def is_group_admin(group_id: int, user_id: int) -> bool:
        try:
            member_info = await get_group_member_info(group_id, user_id)
            role = member_info.get('data', {}).get('role', '')
            return role == 'admin' or role == 'owner'
        except Exception as e:
            print(f"An error occurred while checking admin status: {e}")
            return False
    
    async def url_to_base64(url):
        async with httpx.AsyncClient(timeout=9000) as client:
            response = await client.get(url)
            if response.status_code == 200:
                image_bytes = response.content
                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                return encoded_string
            else:
                raise Exception(f"Failed to retrieve image: {response.status_code}")
    if if_nailong:
        @bot.on(GroupMessage)
        async def get_pic(event: GroupMessage):
            if not event.message_chain.count(Image):
                return
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            b64_in = await url_to_base64(img_url)
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as executor:
                check = await loop.run_in_executor(executor, nailong_main, b64_in)
            if check == 1:
                if chehui1:
                    #is_group_admin1 = await is_group_admin(event.group.id, bot.qq)
                    try:
                        msg = event.json()
                        event_dict = json.loads(msg)
                        Source_id = next((element['id'] for element in event_dict['message_chain']
                                        if element.get('type') == 'Source'), None)
                        await delete_msg(Source_id)
                        await bot.send(event, random.choice(attack1),True)
                        if mute1:
                            await bot.mute(target=event.sender.group.id, member_id=event.sender.id,
                                   time=100)
                    except:
                        await bot.send(event, random.choice(attack1),True)
                else:
                    await bot.send(event, random.choice(attack1),True)
    
    if if_doro:
        @bot.on(GroupMessage)
        async def get_pic1(event: GroupMessage):
            if not event.message_chain.count(Image):
                return
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            b64_in = await url_to_base64(img_url)
            loop = asyncio.get_running_loop()
            #线程池
            with ThreadPoolExecutor() as executor:
                check = await loop.run_in_executor(executor, doro_main, b64_in)
            if check == 1:
                if chehui2:
                    #is_group_admin1 = await is_group_admin(event.group.id, bot.qq)
                    try:
                        msg = event.json()
                        event_dict = json.loads(msg)
                        Source_id = next((element['id'] for element in event_dict['message_chain']
                                        if element.get('type') == 'Source'), None)
                        await delete_msg(Source_id)
                        await bot.send(event, random.choice(attack2),True)
                        if mute2:
                            await bot.mute(target=event.sender.group.id, member_id=event.sender.id,
                                   time=100)
                    except:
                        await bot.send(event, random.choice(attack2),True)
                else:
                    await bot.send(event, random.choice(attack2),True)
