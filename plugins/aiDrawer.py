# -*- coding: utf-8 -*-
import json
import re
from http.cookies import SimpleCookie

import asyncio
import base64
import io

import httpx
from PIL import Image

from plugins.toolkits import random_str


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

async def fluxDrawer(prompt):
    # 第一个请求的URL和参数
    queue_join_url = "https://s5k.cn/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/queue/join"
    queue_join_params = {
        "backend_url": "/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/",
        "sdk_version": "4.38.1",
        "t": "1724901517779",
        "studio_token": "e43dec10-c460-4f6e-ad89-726dc518325a",
        "__theme":"light",
    }
    session_hash="me9nmffgnj"
    # 第二个请求的URL和headers

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "connection": "keep-alive",
        "content-type": "application/json",
        "cookie": "_ga=GA1.2.1599116772.1719823591; _ga_R1FN4KJKJH=GS1.1.1722428989.8.0.1722428989.0.0.0",
        "host": "s5k.cn",
        "referer": "https://s5k.cn/inner/studio/gradio?backend_url=/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/&sdk_version=4.38.1&t=1724901517779&__theme=light&studio_token=e43dec10-c460-4f6e-ad89-726dc518325a",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "x-studio-token": "e43dec10-c460-4f6e-ad89-726dc518325a"
    }
    data1={"data":[1024,1024,8,3.5,prompt,3413],"event_data":None,"fn_index":0,"trigger_id":18,"dataType":["slider","slider","slider","slider","textbox","number"],"session_hash":session_hash}

    cookies = {
        "_ga": "GA1.2.1599116772.1719823591",
        "_ga_R1FN4KJKJH": "GS1.1.1722428989.8.0.1722428989.0.0.0",
        "acw_tc": "276aedee17249273963305410e2ec4f647cc15bb887a0dcca6edb04ebdb533",
        "csrf_session": "MTcyNDkwMTY2NnxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCTWNGbHRVMWswT0hNM1pEZEViM1J0fM2kZW1v-5i7-uelxRFfnp1qw9uePrN8uPHFQRmeEhFq",
        "csrf_token": "ggzwEmJJ8rlf_2-hph7hoXQtecE%3D"
    }
    # 发起第一个请求
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(queue_join_url, params=queue_join_params,json=data1)
        # print(f"POST request status code: {response.status_code}")
        for header in response.headers:
            if header[0].lower() == 'set-cookie':
                cookie = SimpleCookie(header[1])
                for key, morsel in cookie.items():
                    cookies[key] = morsel.value
        response_data = response.json()
        event_id = response_data['event_id']
        #print(event_id)

        queue_data_url=f"https://s5k.cn/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/queue/data?session_hash={session_hash}&studio_token=54f0b89d-beb9-4d7c-9dc2-5ca64e960ce9"

        async with client.stream("GET", queue_data_url, headers=headers,cookies=cookies,timeout=60) as event_stream_response:
            async for line in event_stream_response.aiter_text():
                event = line.replace("data:", "").strip()
                if event:
                    event_data = json.loads(event)
                    print(event_data)
                    if "output" in event_data:
                        imgurl=event_data["output"]["data"][0]["url"]
                        print(imgurl)
                        return imgurl
# 运行 Flask 应用
if __name__ == "__main__":
    asyncio.run(fluxDrawer("prompt:[[[artist:onineko]]], [[[artist:namie]]],cute, symbol-shaped pupils,school uniform, serafuku, clover print, sailor shirt, pleated skirt, sailor collar,shy, holding skirt,, 1girl, 1girl solo, loli, cat girl, animal ear fluff, cat ears,mid shot, x hair ornament, ahoge,traditional media, faux traditional media, lineart, {loli}"))

