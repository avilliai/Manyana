# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import json
import os
import re

import asyncio
from concurrent.futures import ThreadPoolExecutor

import httpx
import requests
import websockets
import yaml

from plugins.toolkits import translate, random_str, random_session_hash, newLogger

logger=newLogger()
try:
    from plugins.modelsLoader import modelLoader

    models = modelLoader()  # 读取模型
    from vits import vG
except:
    pass

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
gptSovitsToken= resulttr.get("GptSovitsToken")
modelscopeCookie = resulttr.get("modelscopeCookie")
if modelscopeCookie == "":
    modelscopeCookie = "cna=j117HdPDmkoCAXjC3hh/4rjk; ajs_anonymous_id=5aa505b4-8510-47b5-a1e3-6ead158f3375; t=27c49d517b916cf11d961fa3769794dd; uuid_tt_dd=11_99759509594-1710000225471-034528; log_Id_click=16; log_Id_pv=12; log_Id_view=277; xlly_s=1; csrf_session=MTcxMzgzODI5OHxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCNFkwRTFkbXAwV0VVME0wOUliakZwfHNEIp5sKWkjeJWKw1IphSS3e4R_7GyEFoKKuDQuivUs; csrf_token=TkLyvVj3to4G5Mn_chtw3OI8rRA%3D; _samesite_flag_=true; cookie2=11ccab40999fa9943d4003d08b6167a0; _tb_token_=555ee71fdee17; _gid=GA1.2.1037864555.1713838369; h_uid=2215351576043; _xsrf=2|f9186bd2|74ae7c9a48110f4a37f600b090d68deb|1713840596; csg=242c1dff; m_session_id=769d7c25-d715-4e3f-80de-02b9dbfef325; _gat_gtag_UA_156449732_1=1; _ga_R1FN4KJKJH=GS1.1.1713838368.22.1.1713841094.0.0.0; _ga=GA1.1.884310199.1697973032; tfstk=fE4KxBD09OXHPxSuRWsgUB8pSH5GXivUTzyBrU0oKGwtCSJHK7N3ebe0Ce4n-4Y8X8wideDotbQ8C7kBE3queYwEQ6OotW08WzexZUVIaNlgVbmIN7MQBYNmR0rnEvD-y7yAstbcoWPEz26cnZfu0a_qzY_oPpRUGhg5ntbgh_D3W4ZudTQmX5MZwX9IN8ts1AlkAYwSdc9sMjuSF8g56fGrgX9SFbgs5bGWtBHkOYL8Srdy07KF-tW4Wf6rhWQBrfUt9DHbOyLWPBhKvxNIBtEfyXi_a0UyaUn8OoyrGJ9CeYzT1yZbhOxndoh8iuFCRFg38WZjVr6yVWunpVaQDQT762H3ezewpOHb85aq5cbfM5aaKWzTZQ_Ss-D_TygRlsuKRvgt_zXwRYE_VymEzp6-UPF_RuIrsr4vHFpmHbxC61Ky4DGguGhnEBxD7Zhtn1xM43oi_fHc61Ky4DGZ6xfGo3-rjf5..; isg=BKKjOsZlMNqsZy8UH4-lXjE_8ygE86YNIkwdKew665XKv0I51IGvHCUz7_tDrx6l"

with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
isjp= result.get("语音功能设置").get("isjp")

async def superVG(data, mode, urls="", langmode="<zh>"):
    pattern = re.compile(r'[\(\（][^\(\)（）（）]*?[\)\）]')

    # 去除括号及其中的内容
    cleaned_text = pattern.sub('', data.get("text"))
    data["text"] = cleaned_text.replace("·", "").replace("~", "").replace("-","")
    if langmode == "<zh>":
        speaker = data.get("speaker")
        if "_" in str(speaker):
            bbb = str(speaker).split("_")[1]
            if bbb == "ZH":
                langmode = "<zh>"
            if bbb == "EN":
                langmode = "<en>"
            if bbb == "JP":
                langmode = "<jp>"
    if langmode == "<jp>":
        try:
            #r=await translate(data.get("text"))
            #print(r)
            data["text"] = await translate(data.get("text"))
        except:
            print("语音合成翻译出错")
    elif langmode == "<en>":
        try:
            #r=await translate(data.get("text"))
            #print(r)
            data["text"] = await translate(data.get("text"), "ZH_CN2EN")
        except:
            print("语音合成翻译出错")
    if mode == "edgetts":
        speaker = data.get("speaker")
        text = data.get("text")
        # os.system("where python")
        p = random_str() + ".mp3"
        prf = "data/voices/" + p
        command = f"edge-tts --voice {speaker} --text {text} --write-media {prf}"
        os.system(command)
        return prf
    elif mode == "so-vits":
        url = "http://127.0.0.1:9082/synthesize"  # 后端服务的地址
        params = data  # 请求参数
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json=json.dumps(params))
            p = "data/voices/" + random_str() + '.wav'
            print("sovits语音合成路径：" + p)
            with open(p, "wb") as f:
                f.write(r.content)
            return p
    elif mode == "vits":
        # 向本地 API 发送 POST 请求

        print("start voice generate")

        text = data['text']
        out = data["out"]

        speaker = data['speaker']
        modelSelect = ['vits/voiceModel/nene/1374_epochsm.pth', 'vits/voiceModel/nene/config.json']
        speakerId="0"
        for i in models:
            if speaker in i:
                modelSelect = [models[i]["modelPath"], models[i]["configPath"]]
                speakerId=models[i]['speakers'].index(speaker)
                if "mixture" in models[i]['text_cleaners'][0]:
                    if langmode == "<zh>":
                        text =f"[ZH]{text}[ZH]"
                    elif langmode == "<en>":
                        text = f"[EN]{text}[EN]"
                    elif langmode == "<jp>":
                        if isjp and re.search(r"[\u3040-\u309F]", text.replace(botName, "")):    # 检测是否含有日语字符
                            text = f"[JA]{text}[JA]"
                            logger.info("文本含有日语字符，不做翻译")
                        else:
                            text = await translate(text)
                            text = f"[JA]{text}[JA]"
                break
        loop = asyncio.get_event_loop()
        # 使用线程池在子线程中运行 sync_function
        await loop.run_in_executor(ThreadPoolExecutor(), vG, text, out, speakerId, modelSelect)
        print("语音生成完成")
        return out
    elif mode == "bert_vits2":
        if urls == '':
            urls = "http://localhost:9080/synthesize"  # 后端服务的地址
            async with httpx.AsyncClient(timeout=200) as client:
                r = await client.post(urls, json=json.dumps(data))
                p = "data/voices/" + random_str() + '.wav'
                print("bert_vits语音合成路径：" + p)
                with open(p, "wb") as f:
                    f.write(r.content)
                return p
        else:
            if str(urls).endswith("/synthesize"):
                pass
            elif str(urls).endswith("/"):
                urls += "synthesize"
            else:
                urls += "/synthesize"
            '''proxies = {
                "http://": proxy,
                "https://": proxy
            }'''
            # 请求参数

            async with httpx.AsyncClient(timeout=200) as client:
                r = await client.post(urls, json=json.dumps(data))
                p = "data/voices/" + random_str() + '.wav'
                print("bert_vits语音合成路径：" + p)
                with open(p, "wb") as f:
                    f.write(r.content)
                return p
    elif mode == "modelscopeTTS":
        speaker = data.get("speaker")
        text = data.get("text")
        if text == "" or text == " ":
            text = "哼哼"
        if speaker in ['辛焱', '鹿野奈奈', '云堇', '瑶瑶', '珐露珊', '蒂玛乌斯', '那维莱特', '砂糖', '康纳', '刻晴', '嘉玛', '知易', '魈', '阿拉夫', '塞塔蕾', '大毫', '伊利亚斯', '欧菲妮', '玛塞勒', '「白老先生」', '式大将', '埃洛伊', '卡芙卡', '公输师傅', '舒伯特', '艾莉丝', '八重神子', '海妮耶', '克罗索', '明曦', '阿佩普', '掇星攫辰天君', '奥兹', '菲米尼', '甘雨', '奥列格', '巴达维', '老孟', '阿圆', '坎蒂丝', '鹿野院平藏', '佐西摩斯', '青镞', '凝光', '「博士」', '斯科特', '阿尔卡米', '沙扎曼', '白术', '派蒙', '纳比尔', '回声海螺', '荧', '帕斯卡', '埃德', '五郎', '萨齐因', '帕姆', '西拉杰', '流浪者', '松浦', '驭空', '「大肉丸」', '莫娜', '多莉', '大慈树王', '留云借风真君', '优菈', '希露瓦', '桑博', '宵宫', '元太', '温迪', '芙宁娜', '九条镰治', '开拓者(男)', '可可利亚', '阿巴图伊', '埃尔欣根', '布洛妮娅', '琳妮特', '岩明', '安柏', '玛乔丽', '费斯曼', '娜维娅', '停云', '天目十五', '莫塞伊思', '史瓦罗', '玛格丽特', '埃泽', '慧心', '绿芙蓉', '浮游水蕈兽·元素生命', '申鹤', '伊迪娅', '托马', '班尼特', '卢卡', '罗刹', 'anzai', '姬子', '菲谢尔', '悦', '莺儿', '莎拉', '金人会长', '迪希雅', '柊千里', '博来', '三月七', '烟绯', '拉齐', '丹吉尔', '赛诺', '虎克', '埃勒曼', '阿扎尔', '深渊法师', '刃', '戴因斯雷布', '神里绫华', '青雀', '萍姥姥', '笼钓瓶一心', '石头', '海芭夏', '九条裟罗', '安西', '阿贝多', '行秋', '可莉', '上杉', '钟离', '提纳里', '绮良良', '迪奥娜', '「公子」', '阿守', '言笑', '阿兰', '龙二', '阿洛瓦', '重云', '丹恒', '开拓者(女)', '常九爷', '瓦尔特', '凯瑟琳', '恕筠', '百闻', '阿娜耶', '米卡', '塔杰·拉德卡尼', '莱依拉', '旁白', '吴船长', '田铁嘴', '托克', '艾文', '香菱', '空', '迪卢克', '迪娜泽黛', '霄翰', '陆行岩本真蕈·元素生命', '七七', '神里绫人', '克列门特', '久利须', '早柚', '「女士」', '半夏', '荒泷一斗', '佩拉', '斯坦利', '柯莱', '艾尔海森', '晴霓', '艾丝妲', '娜塔莎', '白露', '珊瑚', '霍夫曼', '迈勒斯', '毗伽尔', '螺丝咕姆', '博易', '符玄', '嘉良', '胡桃', '彦卿', '卡波特', '丹枢', '阿祇', '林尼', '久岐忍', '深渊使徒', '琴', '芭芭拉', '妮露', '天叔', '凯亚', '「信使」', '夏洛蒂', '纯水精灵？', '羽生田千鹤', '影', '伦纳德', '罗莎莉亚', '哲平', '珊瑚宫心海', '素裳', '希儿', '查尔斯', '宛烟', '镜流', '克拉拉', '迈蒙', '玲可', '长生', '女士', '爱德琳', '丽莎', '「散兵」', '杰帕德', '艾伯特', '塞琉斯', '萨赫哈蒂', '爱贝尔', '枫原万叶', '雷电将军', '杜拉夫', '埃舍尔', '夜兰', '拉赫曼', '达达利亚', '阿晃', '纳西妲', '卡维', '诺艾尔', '德沃沙克', '浣溪', '北斗', '银狼', '景元', '黑塔', '恶龙', '雷泽', '昆钧']:
            p = await modelscopeV3(speaker, text)
            return p
        else:
            headers = {
                "Content-Type": "application/json",
                "Origin": "https://www.modelscope.cn",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
                "Cookie": modelscopeCookie
            }
            if speaker == "阿梓":
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/file="
            elif speaker == "BT":
                speaker = "Speaker"
                url = "https://www.modelscope.cn/api/v1/studio/MiDd1Eye/BT7274-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/MiDd1Eye/BT7274-Bert-VITS2/gradio/file="
            elif speaker == "otto":
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/file="
            elif speaker == "塔菲":
                speaker = "taffy"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/file="
            elif speaker == "星瞳":
                speaker = "XingTong"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/file="
            elif speaker == "丁真":
                url = "https://s5k.cn/api/v1/studio/MiDd1Eye/DZ-Bert-VITS2/gradio/run/predict"
                newurp = "https://s5k.cn/api/v1/studio/MiDd1Eye/DZ-Bert-VITS2/gradio/file="
                speaker = "Speaker"
            elif speaker == "东雪莲":
                speaker = "Azuma"
                url = "https://s5k.cn/api/v1/studio/Outcast/Azuma-Bert-VITS2/gradio/run/predict"
                newurp = "https://s5k.cn/api/v1/studio/Outcast/Azuma-Bert-VITS2/gradio/file="
            elif speaker == "嘉然":
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/file="
            elif speaker == "孙笑川":
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/file="
            elif speaker == "鹿鸣":
                speaker = "Lumi"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/file="
            elif speaker == "文静":
                speaker = "Wenjing"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/file="
            elif speaker == "亚托克斯":
                speaker = "Aatrox"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/file="
            elif speaker == "奶绿":
                speaker = "明前奶绿"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/file="
            elif speaker == "七海":
                speaker = "Nana7mi"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/file="
            elif speaker == "恬豆":
                speaker = "Bekki"
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/file="
            elif speaker == "科比":
                url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/file="
            elif speaker == "胡桃":
                speaker = "hutao"
                url = "https://www.modelscope.cn/api/v1/studio/Xzkong/AI-hutao/gradio/run/predict"
                newurp = "https://www.modelscope.cn/api/v1/studio/Xzkong/AI-hutao/gradio/file="
            data = {
                "data": [text, speaker, 0.5, 0.5, 0.9, 1, "auto", None, "Happy", "Text prompt", "", 0.7],
                "event_data": None,
                "fn_index": 0,
                "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider", "dropdown", "audio", "textbox",
                             "radio", "textbox", "slider"],
                "session_hash": random_session_hash(11)
            }
            p = "data/voices/" + random_str() + '.wav'
            async with httpx.AsyncClient(timeout=200, headers=headers) as client:
                r = await client.post(url, json=data)
                newurl = newurp + \
                         r.json().get("data")[1].get("name")
            async with httpx.AsyncClient(timeout=200, headers=headers) as client:
                r = await client.get(newurl)
                with open(p, "wb") as f:
                    f.write(r.content)
                return p
    elif mode == "outVits":
        p=await outVits(text = data['text'],speaker=data["speaker"])
        return p
    elif mode=="gptSovits":
        p=await gptSoVitsGenerator(gptSovitsToken,text=data['text'],speaker=data["speaker"])
        return p
#modelscopeTTS V3，对接原神崩铁语音合成器。API用法相较之前发生了变化，参考V2修改而成。
async def modelscopeV3(speaker,text):
    # 随机session hash
    session_hash = random_session_hash(11)
    # 第一个请求的URL
    queue_join_url = "https://s5k.cn/api/v1/studio/MuGeminorum/hoyoTTS/gradio/queue/join"
    # 第二个请求的URL
    queue_data_url = "https://s5k.cn/api/v1/studio/MuGeminorum/hoyoTTS/gradio/queue/data"
    # 标头
    headers = {
        "Host": "s5k.cn",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        "Cache-Control": "no-cache",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://s5k.cn/api/v1/studio/MuGeminorum/hoyoTTS/gradio/?",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    }
    # cookies
    cookies = {
        "csrf_token": "2kgLec2ZlH_FM5ICpxvb0nQrIro%3D",
        }
    # 准备第一个链接请求的数据
    join_template = {
        "data": [text, speaker, 0.2, 0.6, 0.8, 1],
        "event_data": None,
        "fn_index": 3,
        "trigger_id": 37,
        "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider"],
        "session_hash": session_hash,
    }
    # 准备第二个链接请求的数据
    data_params = {
        "session_hash": session_hash,
        "studio_token": None
    }
    # 发起第一个请求
    async with httpx.AsyncClient(timeout=10) as client:
        join_response = httpx.post(queue_join_url, json=join_template,headers=headers)
        csrf_token = join_response.cookies["csrf_token"]
        cookies["csrf_token"] = csrf_token
    # 发起第二个请求
    async with httpx.AsyncClient(timeout=20) as client:
        count = 0
        async with client.stream("GET", queue_data_url, params=data_params, headers=headers, cookies=cookies) as response:
            async for chunk in response.aiter_text():
                events = chunk.replace("data:", "").strip().split('\n')
                for event in events:
                    event = event.strip()
                    if not event:
                        continue
                    try:
                        event_data = json.loads(event)
                        if event_data.get("msg") == "process_completed":
                            p = "data/voices/" + random_str() + '.wav'
                            newurl = event_data['output']['data'][0]['url']
                            async with httpx.AsyncClient(timeout=200) as download_client:
                                r = await download_client.get(newurl, headers=headers, cookies=cookies)
                                with open(p, "wb") as f:
                                    f.write(r.content)
                                return p
                        count += 1
                        if count > 10:
                            raise Exception("Exceeded 10 events without entering return branch.")
                    except json.JSONDecodeError:
                        raise Exception(f"JSON decode error{event}")

async def edgetts(data):
    speaker = data.get("speaker")
    text = data.get("text")
    #os.system("where python")
    p = random_str() + ".mp3"
    prf = "data/voices/" + p
    command = f"edge-tts --voice {speaker} --text {text} --write-media {prf}"
    os.system(command)
    return prf


async def sovits(data):
    url = "http://127.0.0.1:9082/synthesize"  # 后端服务的地址
    params = data  # 请求参数
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url, json=json.dumps(params))
        p = "data/voices/" + random_str() + '.wav'
        print("sovits语音合成路径：" + p)
        with open(p, "wb") as f:
            f.write(r.content)
        return p


async def taffySayTest(data, url, proxy=None):
    if url == '':
        url = "http://localhost:9080/synthesize"  # 后端服务的地址
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json=json.dumps(data))
            p = "data/voices/" + random_str() + '.wav'
            print("bert_vits语音合成路径：" + p)
            with open(p, "wb") as f:
                f.write(r.content)
            return p
    else:
        if str(url).endswith("/synthesize"):
            pass
        elif str(url).endswith("/"):
            url += "synthesize"
        else:
            url += "/synthesize"
        '''proxies = {
            "http://": proxy,
            "https://": proxy
        }'''
        # 请求参数

        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json=json.dumps(data))
            p = "data/voices/" + random_str() + '.wav'
            print("bert_vits语音合成路径：" + p)
            with open(p, "wb") as f:
                f.write(r.content)
            return p


async def outVits(text,speaker):
    # os.system("where python")
    #p = random_str() + ".mp3"
    #p = "data/voices/" + p
    p = "data/voices/" + random_str() + '.wav'
    url = f"https://api.lolimi.cn/API/yyhc/api.php?msg={text}&sp={speaker}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.get(url)
        print(r)
        newUrl = r.json().get("mp3")
        print("outvits语音合成路径：" + p)
        r1 = requests.get(newUrl)
        with open(p, "wb") as f:
            f.write(r1.content)
        return p


async def voiceGenerate(data):
    print("start voice generate")
    text = data['text']
    out = data["out"]
    try:
        speaker = data['speaker']
        modelSelect = data['modelSelect']
    except Exception as e:
        speaker = 2
        modelSelect = ['vits/voiceModel/nene/1374_epochsm.pth', 'vits/voiceModel/nene/config.json']
        print(e)
        # with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        # result = yaml.load(f.read(), Loader=yaml.FullLoader)
        # speaker = result.get("vits").get("speaker")
        # modelSelect = result.get("vits").get("modelSelect")
    # 调用 voiceG() 函数
    if modelSelect[0].endswith("I.pth"):
        text = text.replace("[JA]", "").replace("[ZH]", "")
    # print("get")
    await vG(tex=text, out=out, speakerID=speaker, modelSelect=modelSelect)
    print("语音生成完成")
    return out


async def modelscopeTTS(data):
    speaker = data.get("speaker")
    text = data.get("text")
    if speaker == "阿梓":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/run/predict"

    data = {
        "data": ["<zh>" + text, speaker, 0.5, 0.5, 0.9, 1, "ZH", None, "Happy", "Text prompt", "", 0.7],
        "event_data": None,
        "fn_index": 0,
        "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider", "dropdown", "audio", "textbox",
                     "radio", "textbox", "slider"],
        "session_hash": random_session_hash(11)
    }
    p = "data/voices/" + random_str() + '.wav'
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url, json=data)
        newurl = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/file=" + \
                 r.json().get("data")[1].get("name")
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.get(newurl)
            with open(p, "wb") as f:
                f.write(r.content)
            return p


from plugins.aiReplyCore import modelReply, clearsinglePrompt


async def gptVitsSpeakers():
    url = "https://infer.acgnai.top/infer/spks"
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json={
            "type": "tts",
            "brand": "gpt-sovits",
            "name": "anime"
        })
    return r.json()["spklist"]

try:
    GPTSOVITS_SPEAKERS = asyncio.run(gptVitsSpeakers())
except:
    print("GPTSOVITS_SPEAKERS获取失败")

async def gptSoVitsGenerator(token, text, speaker):
    try:
        if len(GPTSOVITS_SPEAKERS[speaker]) > 1:
            r = await modelReply("emotionInclinationTester", 00000,
                                 f"对下面的文本进行情感倾向分析，结果只能从下面的列表：{GPTSOVITS_SPEAKERS[speaker]} 中选取，直接输出结果，不要回复任何其他内容，下面是需要分析的文本:{text}",
                                 noRolePrompt=True)
            await clearsinglePrompt(00000)
            for i in GPTSOVITS_SPEAKERS[speaker]:
                if i in r:
                    inclination = i
                    break
                inclination = "中立"
        else:
            inclination = "中立"
    except:
        inclination = "中立"

    url = "https://infer.acgnai.top/infer/gen"
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json={
            "access_token": token,
            "type": "tts",
            "brand": "gpt-sovits",
            "name": "anime",
            "method": "api",
            "prarm": {
                "speaker": speaker,
                "emotion": inclination,
                "text": text,
                "text_language": "多语种混合",
                "text_split_method": "按标点符号切",
                "fragment_interval": 0.3,
                "batch_size": 1,
                "batch_threshold": 0.75,
                "parallel_infer": True,
                "split_bucket": True,
                "top_k": 10,
                "top_p": 1.0,
                "temperature": 1.0,
                "speed_factor": 1.0
            }
        })
    print(r.json())
    r=requests.get(r.json()['audio'])
    p = "data/voices/" + random_str() + '.wav'
    with open(p, "wb") as f:
        f.write(r.content)
    return p

#asyncio.run(superVG({"text": "你好，欢迎使用语音合成服务。", "out": "output.wav", "speaker": "綾地寧々"},"vits", urls="", langmode="<zh>"))