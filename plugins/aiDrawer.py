# -*- coding: utf-8 -*-
import json
import re
from http.cookies import SimpleCookie

import asyncio
import base64
import io

import httpx
import yaml
from PIL import Image

from plugins.toolkits import random_str,random_session_hash

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
modelscopeCookie = resulttr.get("modelscopeCookie")
if modelscopeCookie == "":
    modelscopeCookie = "cna=j117HdPDmkoCAXjC3hh/4rjk; ajs_anonymous_id=5aa505b4-8510-47b5-a1e3-6ead158f3375; t=27c49d517b916cf11d961fa3769794dd; uuid_tt_dd=11_99759509594-1710000225471-034528; log_Id_click=16; log_Id_pv=12; log_Id_view=277; xlly_s=1; csrf_session=MTcxMzgzODI5OHxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCNFkwRTFkbXAwV0VVME0wOUliakZwfHNEIp5sKWkjeJWKw1IphSS3e4R_7GyEFoKKuDQuivUs; csrf_token=TkLyvVj3to4G5Mn_chtw3OI8rRA%3D; _samesite_flag_=true; cookie2=11ccab40999fa9943d4003d08b6167a0; _tb_token_=555ee71fdee17; _gid=GA1.2.1037864555.1713838369; h_uid=2215351576043; _xsrf=2|f9186bd2|74ae7c9a48110f4a37f600b090d68deb|1713840596; csg=242c1dff; m_session_id=769d7c25-d715-4e3f-80de-02b9dbfef325; _gat_gtag_UA_156449732_1=1; _ga_R1FN4KJKJH=GS1.1.1713838368.22.1.1713841094.0.0.0; _ga=GA1.1.884310199.1697973032; tfstk=fE4KxBD09OXHPxSuRWsgUB8pSH5GXivUTzyBrU0oKGwtCSJHK7N3ebe0Ce4n-4Y8X8wideDotbQ8C7kBE3queYwEQ6OotW08WzexZUVIaNlgVbmIN7MQBYNmR0rnEvD-y7yAstbcoWPEz26cnZfu0a_qzY_oPpRUGhg5ntbgh_D3W4ZudTQmX5MZwX9IN8ts1AlkAYwSdc9sMjuSF8g56fGrgX9SFbgs5bGWtBHkOYL8Srdy07KF-tW4Wf6rhWQBrfUt9DHbOyLWPBhKvxNIBtEfyXi_a0UyaUn8OoyrGJ9CeYzT1yZbhOxndoh8iuFCRFg38WZjVr6yVWunpVaQDQT762H3ezewpOHb85aq5cbfM5aaKWzTZQ_Ss-D_TygRlsuKRvgt_zXwRYE_VymEzp6-UPF_RuIrsr4vHFpmHbxC61Ky4DGguGhnEBxD7Zhtn1xM43oi_fHc61Ky4DGZ6xfGo3-rjf5..; isg=BKKjOsZlMNqsZy8UH4-lXjE_8ygE86YNIkwdKew665XKv0I51IGvHCUz7_tDrx6l"


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
    # 随机session hash
    session_hash = random_session_hash(11)
    # 请求studio_token
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.modelscope.cn/api/v1/studios/token", headers={"cookie": modelscopeCookie})
        response_data = response.json()
        studio_token = response_data["Data"]["Token"]
    print("generated studio_token: "+studio_token)

    # 第一个请求的URL和参数
    queue_join_url = "https://s5k.cn/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/queue/join"
    queue_join_params = {
        "backend_url": "/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/",
        "sdk_version": "4.38.1",
        "t": "1724901517779",
        "studio_token": studio_token,
        "__theme":"light",
    }
    # 第二个请求的URL和headers
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "connection": "keep-alive",
        "content-type": "application/json",
        "cookie": "_ga=GA1.2.1599116772.1719823591; _ga_R1FN4KJKJH=GS1.1.1722428989.8.0.1722428989.0.0.0",
        "host": "s5k.cn",
        "referer": f"https://s5k.cn/inner/studio/gradio?backend_url=/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/&sdk_version=4.38.1&t=1724901517779&__theme=light&studio_token={studio_token}",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "x-studio-token": studio_token
    }
    data1={"data":[1024,1024,8,3.5,prompt,3413],"event_data":None,"fn_index":0,"trigger_id":18,"dataType":["slider","slider","slider","slider","textbox","number"],"session_hash":session_hash}


    # 发起第一个请求
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(queue_join_url, params=queue_join_params,json=data1)
        # print(f"POST request status code: {response.status_code}")
        # for header in response.headers:
        #     if header[0].lower() == 'set-cookie':
        #         cookie = SimpleCookie(header[1])
        #         for key, morsel in cookie.items():
        #             cookies[key] = morsel.value
        # response_data = response.json()
        # event_id = response_data['event_id']
        #print(event_id)

        queue_data_url=f"https://s5k.cn/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/queue/data?session_hash={session_hash}&studio_token={studio_token}"

        async with client.stream("GET", queue_data_url, headers=headers,timeout=60) as event_stream_response:
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

