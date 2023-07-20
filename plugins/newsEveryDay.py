import datetime
import os.path

import httpx
import asyncio
from PIL import Image
from io import BytesIO

async def news():
    url="https://api.emoao.com/api/60s"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    path="data/pictures/cache/"+time+"news.png"
    if os.path.exists(path):
        return path
    else:
        data={"type":"json"}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url,params=data)
            url=r.json().get("data").get("image")
            #print(r.json().get("data").get("image")) # 从二进制数据创建图片对象
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            return path


if __name__ == '__main__':
    asyncio.run(news())
