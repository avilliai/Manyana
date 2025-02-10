import os
import re
import base64

from io import BytesIO
from httpx import AsyncClient
from urllib.parse import quote
from PIL import Image as Image1

from mirai.models import ForwardMessageNode, Forward
from mirai import GroupMessage
from mirai import Image,MessageChain
from plugins.toolkits import random_str

def main(bot,logger):
    logger.info("角色识别功能启动完毕")
    global dataGet
    dataGet = {}
    
    @bot.on(GroupMessage)
    async def startYouridentify(event:GroupMessage):
        global dataGet
        if str(event.message_chain).startswith("#识别") and not event.message_chain.count(Image):
            dataGet[event.sender.id]={'model':"anime_model_lovelive"}
            if re.search(r"(?:gal|galgame|游戏)", str(event.message_chain), re.IGNORECASE):     # 匹配字符串，忽略大小写
                dataGet[event.sender.id]['model']="game_model_kirakira"
            await bot.send(event,"请发送要搜索的图片")
            

    @bot.on(GroupMessage)
    async def character_identify(event: GroupMessage):
        global dataGet
        if (str(event.message_chain).startswith("#识别") or event.sender.id in dataGet) and event.message_chain.count(Image):
            if event.sender.id not in dataGet:
                dataGet[event.sender.id]={'model':"anime_model_lovelive"}
                if re.search(r"(?:gal|galgame|游戏)", str(event.message_chain), re.IGNORECASE):     # 匹配字符串，忽略大小写
                    dataGet[event.sender.id]={'model':"game_model_kirakira"}

            logger.info("接收来自群："+str(event.group.id)+" 用户："+str(event.sender.id)+" 的识别指令")
            img_urls = event.message_chain.get(Image)
            async with AsyncClient(trust_env=False) as client:
                res = await client.get(img_urls[0].url)
            files = {"image": None}
            base_img = Image1.open(BytesIO(res.content)).convert("RGB")
            img_path ="data/pictures/cache/" + random_str() + ".png"       # 保存图片到本地
            base_img.save(img_path)
            files["image"] = open(img_path, "rb")

             # 发送请求
            ai_detect = "False"
            url = f"https://aiapiv2.animedb.cn/ai/api/detect?force_one=1&model={dataGet[event.sender.id]['model']}&ai_detect={ai_detect}"
            headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
                    }
            try:
                async with AsyncClient(trust_env=False) as client:
                    res = await client.post(url=url, headers=headers, data=None, files=files, timeout=30)
                    content = res.json()
                    # print(content)
                if content["code"] != 0:
                    await bot.send(event,f"出错啦~可能是图里角色太多了~\ncontent:{content}",True)
                    dataGet.pop(event.sender.id)
                    return
                data = content["data"]
                if len(data) == 0:
                    await bot.send(event,"没有识别到任何角色",True)
                    dataGet.pop(event.sender.id)
                    return
                
                st = f'共识别到{len(data)}个角色\n当前模型:{dataGet[event.sender.id]["model"]}\n更多模型请访问:https://ai.animedb.cn'
                dataGet[event.sender.id]['message']=[]
                b0 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain(st))
                dataGet.get(event.sender.id).get('message').append(b0)
                for item in data:
                    #框选出角色
                    width, height = base_img.size
                    box = item["box"]
                    box = (box[0] * width, box[1] * height, box[2] * width, box[3] * height)
                    img_bytes = BytesIO()
                    item_img = base_img.crop(box)
                    item_img.save(img_bytes, format="JPEG", quality=int(item["box"][4] * 100))   # 保存图片到内存

                    #构造消息
                    st1 = f"该角色可能为：\n\n"
                    for char in item['char'][0:3]:
                        st1 += (
                            f"{char['name']}\n"
                            f"出自作品：{char['cartoonname']}\n"
                            f"萌娘百科：zh.moegirl.org.cn/index.php?search={quote(char['name'])}\n"
                            f"bing搜索：www.bing.com/images/search?q={quote(char['name'])}\n\n")
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain([Image(base64 = base64.b64encode(img_bytes.getvalue())),st1]))
                    dataGet.get(event.sender.id).get('message').append(b1)
                    del img_bytes  # 释放内存

                logger.info("角色识别成功")
                await bot.send(event,Forward(node_list=dataGet.get(event.sender.id).get('message')))

            except Exception as e:
                logger.error(f"角色识别出错：{e}")
                await bot.send(event,f"出错啦,请稍后再试~",True)
            files['image'].close()    # 关闭图片
            dataGet.pop(event.sender.id)
