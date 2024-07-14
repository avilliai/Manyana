# -*- coding: utf-8 -*-
import re

import asyncio
import base64
import io

import httpx
from PIL import Image

from plugins.RandomStr import random_str


async def SdDraw(prompt, negative_prompt, path, sdurl="http://166.0.199.118:17858"):
    url = sdurl

    payload = {
        "denoising_strength": 0,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 15,
        "cfg_scale": 7,
        "width": 840,
        "height": 840,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "Euler a"
    }  #manba out
    async with httpx.AsyncClient(timeout=40) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    #我的建议是，直接返回base64，让它去审查
    #return r['images'][0]
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    #image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    #image.save(f'{path}')
    return path


async def draw2(prompt, path="./test.png"):
    url = f"https://api.lolimi.cn/API/AI/sd.php?msg={prompt}&mode=动漫"

    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        # print(path)
        return path


async def airedraw(prompt, url, path="./redraw.png"):
    url = f"https://api.lolimi.cn/API/AI/isd.php?msg={prompt}&img={url}&mode=动漫"
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        # print(path)
        return path


async def tiktokredraw(prompt, url, path="./rr.png"):
    url = f"https://oiapi.net/API/AiImage/?url={url}&word={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        # print(path)
        return path


async def draw1(prompt, path="./test.png"):
    url = f"https://api-collect.idcdun.com/v1/images/generations?prompt={prompt}&n=1&model=dall-e-3&size=1024x1024&n=4"
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        #url2=r.json().get("data")[0].get("url")
        paths = []
        for i in r.json().get("data"):
            url2 = i.get("url")
            async with httpx.AsyncClient(timeout=40) as client:
                r1 = await client.get(url2)
            path = "data/pictures/cache/" + random_str() + ".png"
            paths.append(path)
            with open(path, "wb") as f:
                f.write(r1.content)
            # print(path)
        return paths


async def draw3(prompt, path="./test.png"):
    url = f"https://api.alcex.cn/API/ai/novelai.php?tag={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r1 = await client.get(url)
    with open(path, "wb") as f:
        f.write(r1.content)
    # print(path)
    return path


async def draw4(prompt, path="./test.png"):
    url = f"http://txvo.cn/API/huihua/?msg={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r1 = await client.get(url)
    with open(path, "wb") as f:
        f.write(r1.content)
    # print(path)
    return path


async def draw5(prompt, path="./test.png"):
    url = f"https://ai.cloudroo.top/draw/?t={prompt}"
    async with httpx.AsyncClient(timeout=40) as client:
        r1 = await client.get(url)
    with open(path, "wb") as f:
        f.write(r1.content)
    return path


async def draw6(prompt, path="./test.png"):
    url = f"https://api.vps02.top/API/ai_draw.php?tag={prompt}&model=二次元-漫画暗黑风"
    async with httpx.AsyncClient(timeout=60) as client:
        r1 = await client.get(url)
        r1 = await client.get(r1.json().get("url"))
    with open(path, "wb") as f:
        f.write(r1.content)
    return path

async def modelScopeDrawer(prompt, negative_prompt):
    url = "https://s5k.cn/api/v1/studio/AI-ModelScope/stable-diffusion-3-medium/gradio/queue/join"
    params = {
        "backend_url": "/api/v1/studio/AI-ModelScope/stable-diffusion-3-medium/gradio/",
        "sdk_version": "4.31.3",
        "t": "1720966413219",
        "studio_token": "2aebd9a6-3f8e-4907-ba0e-1ac759249c24"
    }

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": "_gid=GA1.2.685814012.1720887454; _ga=GA1.2.1599116772.1719823591; _ga_R1FN4KJKJH=GS1.1.1720887453.2.1.1720888543.0.0.0",
        "Host": "s5k.cn",
        "Origin": "https://s5k.cn",
        "Referer": "https://s5k.cn/inner/studio/gradio?backend_url=/api/v1/studio/AI-ModelScope/stable-diffusion-3-medium/gradio/&sdk_version=4.31.3&t=1720966413219&studio_token=2aebd9a6-3f8e-4907-ba0e-1ac759249c24",
        "Sec-Ch-Ua": "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        "X-Studio-Token": "2aebd9a6-3f8e-4907-ba0e-1ac759249c24"
    }

    data = {
        "data": [
            prompt,
            negative_prompt,
            1587008566,
            True,
            1024,
            1024,
            5,
            28
        ],
        "event_data": None,
        "fn_index": 1,
        "trigger_id": 5,
        "dataType": ["textbox", "textbox", "slider", "checkbox", "slider", "slider", "slider", "slider"],
        "session_hash": "oxm1sjlvnr"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(url, json=data, params=params)
        #print(f"POST request status code: {response.status_code}")
        response_data =response.json()
        event_id = response_data['event_id']
        #print(f"Received event_id: {event_id}")

        # Now start listening to event stream
        event_stream_url = f"https://s5k.cn/api/v1/studio/AI-ModelScope/stable-diffusion-3-medium/gradio/queue/data?session_hash=oxm1sjlvnr&studio_token=2aebd9a6-3f8e-4907-ba0e-1ac759249c24"
        async with client.stream("GET", event_stream_url, headers=headers) as event_stream_response:
            async for line in event_stream_response.aiter_text():
                # Check if line contains "url"
                url_match = re.search(r'"url":"([^"]+)"', line)
                if url_match:
                    url = url_match.group(1)
                    async with httpx.AsyncClient(timeout=40) as client:
                        r1 = await client.get(url)
                    path = "data/pictures/cache/" + random_str() + ".png"
                    with open(path, "wb") as f:
                        f.write(r1.content)
                    #print(f"Received URL: {url}")
                    return path
                #print(line.strip())
# 运行 Flask 应用
if __name__ == "__main__":
    asyncio.run(modelScopeDrawer("a 2D girlish","nsfw"))

