# 此代码示例演示如何将 Markdoen 文件转换为 PDF 文档。
import asyncio
import os.path
from io import BytesIO

import httpx
import yaml
from PIL import Image


async def stageStrategy(aim):
    url = "https://arona.diyigemt.com/api/v2/image?name=" + aim
    path = "data/blueArchive/arona/" + aim + ".png"
    with open("data/blueArchive/hash.yaml", 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)

    async with httpx.AsyncClient(timeout=100) as client:  #100s超时
        r = await client.get(url)  #发起请求
        r = r.json()
        url2 = "https://arona.cdn.diyigemt.com/image" + r.get("data")[0].get("content")
        if os.path.exists(path):
            if str(result.get(path)) != r.get("data")[0].get("hash"):
                await aronaDownLoadImage(url2, path)
                return path
            else:
                return path
        else:
            await aronaDownLoadImage(url2, path)
            return path


async def aronaDownLoadImage(url, path):
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)


if __name__ == '__main__':
    print(asyncio.run(stageStrategy("11-2")))
