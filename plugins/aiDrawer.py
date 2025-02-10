# -*- coding: utf-8 -*-
import asyncio
import base64
import io
import json
import logging
import zipfile

logger = logging.getLogger(__name__)

import httpx
import yaml
from PIL import Image
import random
from plugins.setuModerate import pic_audit_standalone

from plugins.toolkits import random_str,random_session_hash

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
modelscopeCookie = resulttr.get("modelscopeCookie")
proxy = resulttr.get("proxy")
nai_key = resulttr.get("nai_key")
if modelscopeCookie == "":
    modelscopeCookie = "cna=j117HdPDmkoCAXjC3hh/4rjk; ajs_anonymous_id=5aa505b4-8510-47b5-a1e3-6ead158f3375; t=27c49d517b916cf11d961fa3769794dd; uuid_tt_dd=11_99759509594-1710000225471-034528; log_Id_click=16; log_Id_pv=12; log_Id_view=277; xlly_s=1; csrf_session=MTcxMzgzODI5OHxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCNFkwRTFkbXAwV0VVME0wOUliakZwfHNEIp5sKWkjeJWKw1IphSS3e4R_7GyEFoKKuDQuivUs; csrf_token=TkLyvVj3to4G5Mn_chtw3OI8rRA%3D; _samesite_flag_=true; cookie2=11ccab40999fa9943d4003d08b6167a0; _tb_token_=555ee71fdee17; _gid=GA1.2.1037864555.1713838369; h_uid=2215351576043; _xsrf=2|f9186bd2|74ae7c9a48110f4a37f600b090d68deb|1713840596; csg=242c1dff; m_session_id=769d7c25-d715-4e3f-80de-02b9dbfef325; _gat_gtag_UA_156449732_1=1; _ga_R1FN4KJKJH=GS1.1.1713838368.22.1.1713841094.0.0.0; _ga=GA1.1.884310199.1697973032; tfstk=fE4KxBD09OXHPxSuRWsgUB8pSH5GXivUTzyBrU0oKGwtCSJHK7N3ebe0Ce4n-4Y8X8wideDotbQ8C7kBE3queYwEQ6OotW08WzexZUVIaNlgVbmIN7MQBYNmR0rnEvD-y7yAstbcoWPEz26cnZfu0a_qzY_oPpRUGhg5ntbgh_D3W4ZudTQmX5MZwX9IN8ts1AlkAYwSdc9sMjuSF8g56fGrgX9SFbgs5bGWtBHkOYL8Srdy07KF-tW4Wf6rhWQBrfUt9DHbOyLWPBhKvxNIBtEfyXi_a0UyaUn8OoyrGJ9CeYzT1yZbhOxndoh8iuFCRFg38WZjVr6yVWunpVaQDQT762H3ezewpOHb85aq5cbfM5aaKWzTZQ_Ss-D_TygRlsuKRvgt_zXwRYE_VymEzp6-UPF_RuIrsr4vHFpmHbxC61Ky4DGguGhnEBxD7Zhtn1xM43oi_fHc61Ky4DGZ6xfGo3-rjf5..; isg=BKKjOsZlMNqsZy8UH4-lXjE_8ygE86YNIkwdKew665XKv0I51IGvHCUz7_tDrx6l"


with open('config/controller.yaml', 'r', encoding='utf-8') as f:
    controller = yaml.load(f.read(), Loader=yaml.FullLoader)
aiDrawController = controller.get("ai绘画")
negative_prompt = aiDrawController.get("negative_prompt")
positive_prompt = aiDrawController.get("positive_prompt")
no_nsfw_group = [int(group_id) for group_id in aiDrawController.get("no_nsfw_groups", []) if str(group_id).isdigit()]
ckpt = aiDrawController.get("sd默认启动模型")

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
sd1 = result.get("sd审核和反推api")

sd_user_args = {}
async def get_results(url,proxy=None):
    if proxy is not None:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    try:
        async with httpx.AsyncClient(proxies=proxies,timeout=100) as client:
            response = await client.get(url)
    except:
        return []
    if response:
        paths=[]
        d=response.json()["data"]
        for i in d:
            try:
                url=i["url"]
                async with httpx.AsyncClient(proxies=proxies,timeout=100) as client:
                    response = await client.get(url)
                p=f"data/pictures/cache/{random_str(10)}.png"
                with open(p,"wb") as f:
                    f.write(response.content)
                paths.append(p)
            except:
                continue
        return paths
    else:
        return []
async def ideo_gram(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/ideogram/generate-image?prompt={prompt}"
    return await get_results(url,proxy)

async def bing_dalle3(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/dall-e-3/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def flux_speed(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/flux-speed/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def recraft_v3(prompt,proxy=None):
    url=f"https://apiserver.alcex.cn/recraft-v3/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def flux_ultra(prompt,proxy=None):
    url=f"https://apiserver.alcex.cn/flux-pro.ultra/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def SdDraw(prompt, negative_prompt, path, sdurl,groupid):
    url = sdurl

    payload = {
        "denoising_strength": 0.5,
        "enable_hr": 'false',
        "hr_scale": 1.5,
        "hr_second_pass_steps" : 15,
        "hr_upscaler" : 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": 960,
        "height": 1536,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "DPM++ 2M Karras",
        "sampler_name": 'DPM++ 2M',
        "scheduler": 'Karras',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
            },
        "override_settings_restore_afterwards": False,
    }  #manba out
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    #我的建议是，直接返回base64，让它去审查
    b64 = r['images'][0]
    if groupid in no_nsfw_group:                                   # 推荐用kaggle部署sd，防止占线（kaggle搜spawnerqwq）
        check = await pic_audit_standalone(b64, return_none=True,url = sd1)  # 这里如果是使用我（spawnerqwq）的kaggle云端脚本部署的sd，参数可以写(b64,return_none=True,url)
        if check:                                                  # 注意自己装的wd14打标插件没用，官方插件有bug，我在kaggle部署的插件是修改过的
            return False                                           # 注意这里的url是sdurl，如果你在不是sd的画图模块也想开审核，注意把那个url的参数填sdurl
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    #image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    #image.save(f'{path}')
    return path

async def SdDraw1(prompt, negative_prompt, path, sdurl,groupid):
    url = sdurl

    payload = {
        "denoising_strength": 0.5,
        "enable_hr": 'false',
        "hr_scale": 1.5,
        "hr_second_pass_steps" : 15,
        "hr_upscaler" : 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": 1536,
        "height": 960,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "DPM++ 2M Karras",
        "sampler_name": 'DPM++ 2M',
        "scheduler": 'Karras',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
            },
        "override_settings_restore_afterwards": False,
    }  #manba out
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    #我的建议是，直接返回base64，让它去审查
    #return r['images'][0]
    b64 = r['images'][0]
    if groupid in no_nsfw_group:
        check = await pic_audit_standalone(b64, return_none=True,url = sd1)
        if check:
            return False
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    #image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    #image.save(f'{path}')
    return path

async def SdDraw2(prompt, negative_prompt, path, sdurl,groupid):
    url = sdurl

    payload = {
        "denoising_strength": 0.5,
        "enable_hr": 'false',
        "hr_scale": 1.5,
        "hr_second_pass_steps" : 15,
        "hr_upscaler" : 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 30,
        "cfg_scale": 7,
        "width": 1024,
        "height": 1024,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "DPM++ 2M Karras",
        "sampler_name": 'DPM++ 2M',
        "scheduler": 'Karras',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
            },
        "override_settings_restore_afterwards": False,
    }  #manba out
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    #我的建议是，直接返回base64，让它去审查
    #return r['images'][0]
    b64 = r['images'][0]
    if groupid in no_nsfw_group:
        check = await pic_audit_standalone(b64, return_none=True,url = sd1)
        if check:
            return False
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    #image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    #image.save(f'{path}')
    return path

async def getloras(sdurl="http://166.0.199.118:17858"):
    url = f'{sdurl}/sdapi/v1/loras'
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        r = response.json()
        result_lines = [f'<lora:{lora.get("name", "未知")}:1.0>,' for lora in r]
        result = '以下是可用的lora：\n' + '\n'.join(result_lines) + '\n'
        return result

async def ckpt2(model):
    global ckpt
    ckpt = model

async def getcheckpoints(sdurl="http://166.0.199.118:17858"):
    url = f'{sdurl}/sdapi/v1/sd-models'
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        r = response.json()
        model_lines = [f'{model.get("model_name", "未知")}' for model in r]
        result = f'当前底模: {ckpt}\n以下是可用的底模：\n' + '\n'.join(model_lines) + '\n'
        return result

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
    seed = random.randint(-999999, 999999)
    data1={"data":[1024,1024,8,3.5,prompt,seed],"event_data":None,"fn_index":0,"trigger_id":18,"dataType":["slider","slider","slider","slider","textbox","number"],"session_hash":session_hash}


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

async def SdreDraw(prompt, negative_prompt, path, sdurl, groupid, b64_in,args):
    url = sdurl
    args = args
    width = (args.get('w', 1024) if args.get('w', 1024) > 0 else 1024) if isinstance(args, dict) else 1024
    height = (args.get('h', 1024) if args.get('h', 1024) > 0 else 1024) if isinstance(args, dict) else 1024

    payload = {
        "init_images": [b64_in],
        "denoising_strength": 0.7,
        "enable_hr": 'true',
        "hr_scale": 1.5,
        "hr_second_pass_steps" : 15,
        "hr_upscaler" : 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "DPM++ 2M Karras",
        "sampler_name": 'DPM++ 2M',
        "scheduler": 'Karras',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
            },
        "override_settings_restore_afterwards": False,
    }  #manba out
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    r = response.json()
    if 'images' not in r or len(r['images']) == 0:
        logger.error("Response does not contain images field or it is empty")
        return None
    #我的建议是，直接返回base64，让它去审查
    b64 = r['images'][0]
    if groupid in no_nsfw_group:                                   # 推荐用kaggle部署sd，防止占线（kaggle搜spawnerqwq）
        check = await pic_audit_standalone(b64, return_none=True,url = sd1)  # 这里如果是使用我（spawnerqwq）的kaggle云端脚本部署的sd，参数可以写(b64,return_none=True,url)
        if check:                                                  # 注意自己装的wd14打标插件没用，官方插件有bug，我在kaggle部署的插件是修改过的
            return False                                           # 注意这里的url是sdurl，如果你在不是sd的画图模块也想开审核，注意把那个url的参数填sdurl
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    #image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    #image.save(f'{path}')
    return path 

async def SdDraw0(prompt, negative_prompt, path, sdurl,groupid,args):
    url = sdurl

    args = args
    width = (args.get('w', 1064) if args.get('w', 1064) > 0 else 1064) if isinstance(args, dict) else 1064
    height = (args.get('h', 1600) if args.get('h', 1600) > 0 else 1600) if isinstance(args, dict) else 1600
    
    payload = {
        "denoising_strength": 0.5,
        "enable_hr": 'false',
        "hr_scale": 1.5,
        "hr_second_pass_steps" : 15,
        "hr_upscaler" : 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "DPM++ 2M Karras",
        "sampler_name": 'DPM++ 2M',
        "scheduler": 'Karras',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
            },
        "override_settings_restore_afterwards": False,
    }  #manba out
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    #我的建议是，直接返回base64，让它去审查
    b64 = r['images'][0]
    if groupid in no_nsfw_group:                                   # 推荐用kaggle部署sd，防止占线（kaggle搜spawnerqwq）
        check = await pic_audit_standalone(b64, return_none=True,url = sd1)  # 这里如果是使用我（spawnerqwq）的kaggle云端脚本部署的sd，参数可以写(b64,return_none=True,url)
        if check:                                                  # 注意自己装的wd14打标插件没用，官方插件有bug，我在kaggle部署的插件是修改过的
            return False                                           # 注意这里的url是sdurl，如果你在不是sd的画图模块也想开审核，注意把那个url的参数填sdurl
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    #image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    #image.save(f'{path}')
    return path                   

async def cn1(prompt, negative_prompt, path, sdurl, groupid, b64_in,args):# 这是一个controlnet调用示例，想改的自己改
    url = sdurl
    args = args
    width = (args.get('w', 1064) if args.get('w', 1064) > 0 else 1064) if isinstance(args, dict) else 1064
    height = (args.get('h', 1600) if args.get('h', 1600) > 0 else 1600) if isinstance(args, dict) else 1600

    payload = {
        "denoising_strength": 0.7,
        "enable_hr": 'false',
        "hr_scale": 1.5,
        "hr_second_pass_steps" : 15,
        "hr_upscaler" : 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_index": "DPM++ 2M Karras",
        "sampler_name": 'DPM++ 2M',
        "scheduler": 'Karras',
        "clip_skip_steps": 2,
        "alwayson_scripts": {  # 下面是controlnet调用示例
            "controlnet":
                {
                    "args": [
                        {
                            "enabled": True,  # 启用
                            "control_mode": 0,  # 对应webui 的 Control Mode 可以直接填字符串 推荐使用下标 0 1 2
                            "model": "t2i-adapter_diffusers_xl_lineart [bae0efef]",  # 对应webui 的 Model
                            "module": "lineart_standard (from white bg & black line)",  # 对应webui 的 Preprocessor
                            "weight": 0.45,  # 对应webui 的Control Weight
                            "resize_mode": "Crop and Resize",
                            "threshold_a": 200,  # 阈值a 部分control module会用上
                            "threshold_b": 245,  # 阈值b
                            "guidance_start": 0,  # 什么时候介入 对应webui 的 Starting Control Step
                            "guidance_end": 0.7,  # 什么时候退出 对应webui 的 Ending Control Step
                            "pixel_perfect": True,  # 像素完美
                            "processor_res": 512,  # 预处理器分辨率
                            "save_detected_map": False,  # 因为使用了 controlnet API会返回生成controlnet的效果图，默认是True，如何不需要，改成False
                            "input_image": b64_in,  # 图片 格式为base64

                        },
                        # 多个controlnet 在复制上面一个字典下来就行
                        {
                            "enabled": False,
                            "control_mode": 1,
                            "model": "t2i-adapter_diffusers_xl_lineart [bae0efef]",
                            "module": "lineart_standard (from white bg & black line)",
                            "weight": 0.45,
                            "resize_mode": "Crop and Resize",
                            "threshold_a": 200,
                            "threshold_b": 245,
                            "guidance_start": 0,
                            "guidance_end": 0.7,
                            "pixel_perfect": True,
                            "processor_res": 512,
                            "save_detected_map": False,
                            "input_image": b64_in,

                        }
                    ]
                }
        },
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
            },
        "override_settings_restore_afterwards": False,
    }  #manba out
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    if 'images' not in r or len(r['images']) == 0:
        logger.error("Response does not contain images field or it is empty")
        return None
    b64 = r['images'][0]
    if groupid in no_nsfw_group:                                   # 推荐用kaggle部署sd，防止占线（kaggle搜spawnerqwq）
        check = await pic_audit_standalone(b64, return_none=True,url = sd1)  # 这里如果是使用我（spawnerqwq）的kaggle云端脚本部署的sd，参数可以写(b64,return_none=True,url)
        if check:                                                  # 注意自己装的wd14打标插件没用，官方插件有bug，我在kaggle部署的插件是修改过的
            return False                                           # 注意这里的url是sdurl，如果你在不是sd的画图模块也想开审核，注意把那个url的参数填sdurl
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    image.save(f'{path}')
    return path 

async def n4(prompt, negative_prompt, path, groupid):
    url = "https://image.novelai.net"

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    elif "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    else:
        width = 832
        height = 1216
    
    payload = {
        "input": f"{prompt}, rating:general, best quality, very aesthetic, absurdres",
        "model": "nai-diffusion-4-curated-preview",
        "action": "generate",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": 6,
            "sampler": "k_dpmpp_2m",
            "steps": 23,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "dynamic_thresholding": False,
            "controlnet_strength": 1,
            "legacy": False,
            "add_original_image": True,
            "cfg_rescale": 0,
            "noise_schedule": "exponential",
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
            "seed": random.randint(0, 2**32 - 1),
            "characterPrompts": [],
            "v4_prompt": {
                "caption": {
                    "base_caption": f"{prompt}, rating:general, best quality, very aesthetic, absurdres",
                    "char_captions": []
                },
                "use_coords": False,
                "use_order": True
            },
            "v4_negative_prompt": {
                "caption": {
                    "base_caption": "blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts",
                    "char_captions": []
                }
            },
            "negative_prompt": "blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts",
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "deliberate_euler_ancestral_bug": False,
            "prefer_brownian": True
        }
    }

    headers = {
        "Authorization": f"Bearer {nai_key}"
    }
    proxies = {
        "http://": proxy,
        "https://": proxy,
    }
    async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
        response = await client.post(url=f'{url}/ai/generate-image', json=payload, headers=headers)
        response.raise_for_status()
        zip_content = response.content
        zip_file = io.BytesIO(zip_content)
        with zipfile.ZipFile(zip_file, 'r') as zf:
            file_names = zf.namelist()
            if not file_names:
                raise ValueError("The zip archive is empty.")
            file_name = file_names[0]
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                raise ValueError("The zip archive does not contain an image file.")
            image_data = zf.read(file_name)
            if groupid in no_nsfw_group:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True, url=sd1)
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path

async def n3(prompt, negative_prompt, path, groupid):
    url = "https://image.novelai.net"

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    elif "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    else:
        width = 832
        height = 1216
    
    payload = {
        "input": f"{prompt}, best quality, amazing quality, very aesthetic, absurdres",
        "model": "nai-diffusion-3",
        "action": "generate",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": 5,
            "sampler": "k_dpmpp_2m",
            "steps": 23,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "sm": False,
            "sm_dyn": False,
            "dynamic_thresholding": False,
            "controlnet_strength": 1,
            "legacy": False,
            "add_original_image": True,
            "cfg_rescale": 0,
            "noise_schedule": "exponential",
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "seed": random.randint(0, 2**32 - 1),
            "characterPrompts": [],
            "negative_prompt": "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]",
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": []
        }
    }

    headers = {
        "Authorization": f"Bearer {nai_key}"
    }
    proxies = {
        "http://": proxy,
        "https://": proxy,
    }
    async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
        response = await client.post(url=f'{url}/ai/generate-image', json=payload, headers=headers)
        response.raise_for_status()
        zip_content = response.content
        zip_file = io.BytesIO(zip_content)
        with zipfile.ZipFile(zip_file, 'r') as zf:
            file_names = zf.namelist()
            if not file_names:
                raise ValueError("The zip archive is empty.")
            file_name = file_names[0]
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                raise ValueError("The zip archive does not contain an image file.")
            image_data = zf.read(file_name)
            if groupid in no_nsfw_group:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True, url=sd1)
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path

# 运行 Flask 应用
if __name__ == "__main__":
    asyncio.run(fluxDrawer("prompt:[[[artist:onineko]]], [[[artist:namie]]],cute, symbol-shaped pupils,school uniform, serafuku, clover print, sailor shirt, pleated skirt, sailor collar,shy, holding skirt,, 1girl, 1girl solo, loli, cat girl, animal ear fluff, cat ears,mid shot, x hair ornament, ahoge,traditional media, faux traditional media, lineart, {loli}"))

