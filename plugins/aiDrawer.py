# -*- coding: utf-8 -*-
import asyncio
from io import BytesIO

import httpx
import io

import base64
import requests
from PIL import Image

from plugins.RandomStr import random_str

async def SdDraw(prompt, negative_prompt,path="./output.png"):
    url = "http://166.0.199.118:17858"
    
    payload = {
        "denoising_strength": 0,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 15,
        "cfg_scale": 7,
        "width": 768,
        "height": 512,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "Euler a"
    }#不懂SD调参就不要改参数了，否则可能会导致服务器内存溢出，导致绘画失败。其中negative_prompt（负面tag）中的(nsfw:1.5),pussy,nipples,breasts,breast,sex防止出现r18图片
    async with httpx.AsyncClient(timeout=40) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    #我的建议是，直接返回base64，让它去审查
    return r['images'][0]
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    image.save(f'{path}')
        
    return path
async def draw(prompt,path= "./test.png"):
    url=f"https://api.lolimi.cn/API/AI/sd.php?msg={prompt}&mode=动漫"

    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        with open(path,"wb") as f:
            f.write(r.content)
        # print(path)
        return path
async def airedraw(prompt,url,path="./redraw.png"):
    url=f"https://api.lolimi.cn/API/AI/isd.php?msg={prompt}&img={url}&mode=动漫"
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        # print(path)
        return path
async def tiktokredraw(prompt,url,path="./rr.png"):
    url=f"https://oiapi.net/API/AiImage/?url={url}&word={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        # print(path)
        return path
async def draw1(prompt,path="./test.png"):
    url=f"https://api-collect.idcdun.com/v1/images/generations?prompt={prompt}&n=1&model=dall-e-3&size=1024x1024&n=4"
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        #url2=r.json().get("data")[0].get("url")
        paths=[]
        for i in r.json().get("data"):
            url2=i.get("url")
            async with httpx.AsyncClient(timeout=40) as client:
                r1 = await client.get(url2)
            path = "data/pictures/cache/" + random_str() + ".png"
            paths.append(path)
            with open(path, "wb") as f:
                f.write(r1.content)
            # print(path)
        return paths
async def draw3(prompt,path="./test.png"):
    url=f"https://api.alcex.cn/API/ai/novelai.php?tag={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r1 = await client.get(url)
    with open(path, "wb") as f:
        f.write(r1.content)
    # print(path)
    return path
async def draw4(prompt,path="./test.png"):
    url=f"http://txvo.cn/API/huihua/?msg={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r1 = await client.get(url)
    with open(path, "wb") as f:
        f.write(r1.content)
    # print(path)
    return path
async def draw5(prompt,path="./test.png"):
    url=f"https://ai.cloudroo.top/draw/?t={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r1 = await client.get(url)
    with open(path, "wb") as f:
        f.write(r1.content)
    return path
# 运行 Flask 应用
if __name__ == "__main__":
    asyncio.run(draw1("正在吃早饭的二次元少女"))
