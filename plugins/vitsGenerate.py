# -*- coding: utf-8 -*-
import json
import os
import re

import httpx
import requests
import websockets
import yaml

from plugins.RandomStr import random_str
from plugins.translater import translate

try:
    from plugins.modelsLoader import modelLoader

    models, default, characters = modelLoader()  # 读取模型
    from vits import vG
except:
    pass

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
modelscopeCookie = resulttr.get("modelscopeCookie")
if modelscopeCookie == "":
    modelscopeCookie = "cna=j117HdPDmkoCAXjC3hh/4rjk; ajs_anonymous_id=5aa505b4-8510-47b5-a1e3-6ead158f3375; t=27c49d517b916cf11d961fa3769794dd; uuid_tt_dd=11_99759509594-1710000225471-034528; log_Id_click=16; log_Id_pv=12; log_Id_view=277; xlly_s=1; csrf_session=MTcxMzgzODI5OHxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCNFkwRTFkbXAwV0VVME0wOUliakZwfHNEIp5sKWkjeJWKw1IphSS3e4R_7GyEFoKKuDQuivUs; csrf_token=TkLyvVj3to4G5Mn_chtw3OI8rRA%3D; _samesite_flag_=true; cookie2=11ccab40999fa9943d4003d08b6167a0; _tb_token_=555ee71fdee17; _gid=GA1.2.1037864555.1713838369; h_uid=2215351576043; _xsrf=2|f9186bd2|74ae7c9a48110f4a37f600b090d68deb|1713840596; csg=242c1dff; m_session_id=769d7c25-d715-4e3f-80de-02b9dbfef325; _gat_gtag_UA_156449732_1=1; _ga_R1FN4KJKJH=GS1.1.1713838368.22.1.1713841094.0.0.0; _ga=GA1.1.884310199.1697973032; tfstk=fE4KxBD09OXHPxSuRWsgUB8pSH5GXivUTzyBrU0oKGwtCSJHK7N3ebe0Ce4n-4Y8X8wideDotbQ8C7kBE3queYwEQ6OotW08WzexZUVIaNlgVbmIN7MQBYNmR0rnEvD-y7yAstbcoWPEz26cnZfu0a_qzY_oPpRUGhg5ntbgh_D3W4ZudTQmX5MZwX9IN8ts1AlkAYwSdc9sMjuSF8g56fGrgX9SFbgs5bGWtBHkOYL8Srdy07KF-tW4Wf6rhWQBrfUt9DHbOyLWPBhKvxNIBtEfyXi_a0UyaUn8OoyrGJ9CeYzT1yZbhOxndoh8iuFCRFg38WZjVr6yVWunpVaQDQT762H3ezewpOHb85aq5cbfM5aaKWzTZQ_Ss-D_TygRlsuKRvgt_zXwRYE_VymEzp6-UPF_RuIrsr4vHFpmHbxC61Ky4DGguGhnEBxD7Zhtn1xM43oi_fHc61Ky4DGZ6xfGo3-rjf5..; isg=BKKjOsZlMNqsZy8UH4-lXjE_8ygE86YNIkwdKew665XKv0I51IGvHCUz7_tDrx6l"


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
        if speaker in ['anzai', '「信使」', '「公子」', '「博士」', '「大肉丸」', '「女士」', '「散兵」', '「白老先生」', '七七', '三月七', '上杉', '丹吉尔', '丹恒', '丹枢', '丽莎', '久利须', '久岐忍', '九条裟罗', '九条镰治', '云堇', '五郎', '伊利亚斯', '伊迪娅', '优菈', '伦纳德', '佐西摩斯', '佩拉', '停云', '元太', '克列门特', '克拉拉', '克罗索', '八重神子', '公输师傅', '凝光', '凯亚', '凯瑟琳', '刃', '刻晴', '北斗', '半夏', '博易', '博来', '卡波特', '卡维', '卡芙卡', '卢卡', '可可利亚', '可莉', '史瓦罗', '吴船长', '哲平', '嘉玛', '嘉良', '回声海螺', '坎蒂丝', '埃勒曼', '埃尔欣根', '埃德', '埃泽', '埃洛伊', '埃舍尔', '塔杰·拉德卡尼', '塞塔蕾', '塞琉斯', '夏洛蒂', '多莉', '夜兰', '大慈树王', '大毫', '天叔', '天目十五', '奥兹', '奥列格', '女士', '妮露', '姬子', '娜塔莎', '娜维娅', '安柏', '安西', '宛烟', '宵宫', '岩明', '巴达维', '布洛妮娅', '希儿', '希露瓦', '帕姆', '帕斯卡', '常九爷', '康纳', '开拓者(女)', '开拓者(男)', '式大将', '彦卿', '影', '德沃沙克', '恕筠', '恶龙', '悦', '慧心', '戴因斯雷布', '托克', '托马', '拉赫曼', '拉齐', '掇星攫辰天君', '提纳里', '斯坦利', '斯科特', '旁白', '早柚', '昆钧', '明曦', '景元', '晴霓', '杜拉夫', '杰帕德', '松浦', '林尼', '枫原万叶', '柊千里', '查尔斯', '柯莱', '桑博', '欧菲妮', '毗伽尔', '沙扎曼', '派蒙', '流浪者', '浣溪', '浮游水蕈兽·元素生命', '海妮耶', '海芭夏', '深渊使徒', '深渊法师', '温迪', '烟绯', '爱德琳', '爱贝尔', '玛乔丽', '玛塞勒', '玛格丽特', '玲可', '珊瑚', '珊瑚宫心海', '珐露珊', '班尼特', '琳妮特', '琴', '瑶瑶', '瓦尔特', '甘雨', '田铁嘴', '申鹤', '留云借风真君', '白术', '白露', '百闻', '知易', '石头', '砂糖', '神里绫人', '神里绫华', '空', '符玄', '笼钓瓶一心', '米卡', '素裳', '纯水精灵？', '纳比尔', '纳西妲', '绮良良', '绿芙蓉', '罗刹', '罗莎莉亚', '羽生田千鹤', '老孟', '胡桃', '舒伯特', '艾丝妲', '艾伯特', '艾尔海森', '艾文', '艾莉丝', '芙宁娜', '芭芭拉', '荒泷一斗', '荧', '莎拉', '莫塞伊思', '莫娜', '莱依拉', '莺儿', '菲米尼', '菲谢尔', '萍姥姥', '萨赫哈蒂', '萨齐因', '蒂玛乌斯', '虎克', '螺丝咕姆', '行秋', '西拉杰', '言笑', '诺艾尔', '费斯曼', '赛诺', '辛焱', '达达利亚', '迈勒斯', '迈蒙', '迪卢克', '迪奥娜', '迪娜泽黛', '迪希雅', '那维莱特', '重云', '金人会长', '钟离', '银狼', '镜流', '长生', '阿佩普', '阿兰', '阿圆', '阿娜耶', '阿守', '阿尔卡米', '阿巴图伊', '阿扎尔', '阿拉夫', '阿晃', '阿洛瓦', '阿祇', '阿贝多', '陆行岩本真蕈·元素生命', '雷泽', '雷电将军', '霄翰', '霍夫曼', '青镞', '青雀', '香菱', '驭空', '魈', '鹿野奈奈', '鹿野院平藏', '黑塔', '龙二']:
            p=await modelscopeV2(speaker, text)
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
                "session_hash": "xjwen214wqf"
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
        speaker = data.get("speaker")
        text = data.get("text")
        p = "data/voices/" + random_str() + '.wav'
        url = f"https://api.lolimi.cn/API/yyhc/y.php?msg={text}&speaker={speaker}"
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url)
            newUrl = r.json().get("music")
            #print("outvits语音合成路径：" + p)
            r1 = requests.get(newUrl)
            with open(p, "wb") as f:
                f.write(r1.content)
            return p
    elif mode == "FishTTS":
        modelid = data.get("speaker")

        text = data.get("text")
        if os.path.exists("./config/api.yaml"):
            with open('config/api.yaml', 'r', encoding='utf-8') as f:
                res = yaml.load(f.read(), Loader=yaml.FullLoader)
                proxy = res.get("proxy")
                Authorization = res.get("FishTTSAuthorization")
        if len(modelid) < 15:
            modelid = await fetch_FishTTS_ModelId(proxy, Authorization, modelid)
        if proxy == "" or proxy == " ":
            async with httpx.AsyncClient(timeout=20, verify=False) as client:
                async def send_options_request(client):
                    url = "https://api.fish.audio/task"
                    headers = {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Access-Control-Request-Headers": "authorization,content-type",
                        "Access-Control-Request-Method": "POST",
                        "Origin": "https://fish.audio",
                        "Referer": "https://fish.audio/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
                    }

                    try:
                        response = await client.options(url, headers=headers)
                        #print("POST Response Status:", response.status_code)
                        # print("POST Response Headers:", response.headers)
                        # print("POST Response Text:", response.text)
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error occurred: {e}")
                    except httpx.ReadTimeout:
                        print("The request timed out while reading from the server.")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    # print("OPTIONS Response Status:", response.status_code)
                    # print("OPTIONS Response Headers:", response.headers)
                    # print("OPTIONS Response Text:", response.text)

                async def send_post_request(client, modelid, text, Authorization):
                    url = "https://api.fish.audio/task"
                    headers = {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Authorization": Authorization,
                        "Content-Type": "application/json",
                        "Origin": "https://fish.audio",
                        "Referer": "https://fish.audio/",
                        "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
                    }
                    data = {
                        "type": "tts",
                        "channel": "free",
                        "stream": True,
                        "model": str(modelid),
                        "parameters": {
                            "text": text
                        }
                    }

                    try:
                        response = await client.post(url, headers=headers, json=data, timeout=60.0)
                        # print("POST Response Status:", response.status_code)
                        # print("POST Response Headers:", response.headers)
                        # print("POST Response Text:", response.text)

                        # 提取 task-id
                        task_id = response.headers.get('task-id')
                        # print("Task-ID:", task_id)
                        return task_id
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error occurred: {e}")
                    except httpx.ReadTimeout:
                        print("The request timed out while reading from the server.")
                    except Exception as e:
                        print(f"An error occurred: {e}")

                async def send_get_request(client, task_id, Authorization):
                    url = f"https://api.fish.audio/task/{task_id}"
                    headers = {
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Authorization": Authorization,
                        "Origin": "https://fish.audio",
                        "Referer": "https://fish.audio/",
                        "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
                    }

                    try:
                        response = await client.get(url, headers=headers, timeout=60.0)
                        # print("GET Response Status:", response.status_code)
                        # print("GET Response Headers:", response.headers)
                        # print("GET Response Text:", response.text)
                        return response.json()
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error occurred: {e}")
                    except httpx.ReadTimeout:
                        print("The request timed out while reading from the server.")
                    except Exception as e:
                        print(f"An error occurred: {e}")

                await send_options_request(client)
                task_id = await send_post_request(client, modelid, text, Authorization)
                if task_id:
                    result = await send_get_request(client, task_id, Authorization)
                    # print("GET Request Result:", result)
                    audio_url = result['result']
                    rb = await client.get(audio_url)
                    path = "data/voices/" + random_str() + '.wav'
                    with open(path, "wb") as f:
                        f.write(rb.content)
                    return path
        else:
            proxies = {
                "http://": proxy,
                "https://": proxy
            }
            async with httpx.AsyncClient(proxies=proxies, timeout=20, verify=False) as client:
                async def send_options_request(client):
                    url = "https://api.fish.audio/task"
                    headers = {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Access-Control-Request-Headers": "authorization,content-type",
                        "Access-Control-Request-Method": "POST",
                        "Origin": "https://fish.audio",
                        "Referer": "https://fish.audio/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
                    }

                    try:
                        response = await client.options(url, headers=headers)
                        #print("POST Response Status:", response.status_code)
                        #print("POST Response Headers:", response.headers)
                        # print("POST Response Text:", response.text)
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error occurred: {e}")
                    except httpx.ReadTimeout:
                        print("The request timed out while reading from the server.")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    # print("OPTIONS Response Status:", response.status_code)
                    # print("OPTIONS Response Headers:", response.headers)
                    # print("OPTIONS Response Text:", response.text)

                async def send_post_request(client, modelid, text, Authorization):
                    url = "https://api.fish.audio/task"
                    headers = {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Authorization": Authorization,
                        "Content-Type": "application/json",
                        "Origin": "https://fish.audio",
                        "Referer": "https://fish.audio/",
                        "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
                    }
                    data = {
                        "type": "tts",
                        "channel": "free",
                        "stream": True,
                        "model": str(modelid),
                        "parameters": {
                            "text": text
                        }
                    }

                    try:
                        response = await client.post(url, headers=headers, json=data, timeout=60.0)
                        # print("POST Response Status:", response.status_code)
                        #print("POST Response Headers:", response.headers)
                        # print("POST Response Text:", response.text)

                        # 提取 task-id
                        task_id = response.headers.get('task-id')
                        #print("Task-ID:", task_id)
                        return task_id
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error occurred: {e}")
                    except httpx.ReadTimeout:
                        print("The request timed out while reading from the server.")
                    except Exception as e:
                        print(f"An error occurred: {e}")

                async def send_get_request(client, task_id, Authorization):
                    url = f"https://api.fish.audio/task/{task_id}"
                    headers = {
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Authorization": Authorization,
                        "Origin": "https://fish.audio",
                        "Referer": "https://fish.audio/",
                        "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
                    }

                    try:
                        response = await client.get(url, headers=headers, timeout=60.0)
                        #print("GET Response Status:", response.status_code)
                        # print("GET Response Headers:", response.headers)
                        #print("GET Response Text:", response.text)
                        return response.json()
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error occurred: {e}")
                    except httpx.ReadTimeout:
                        print("The request timed out while reading from the server.")
                    except Exception as e:
                        print(f"An error occurred: {e}")

                await send_options_request(client)
                task_id = await send_post_request(client, modelid, text, Authorization)
                if task_id:
                    result = await send_get_request(client, task_id, Authorization)
                    #print("GET Request Result:", result)
                    audio_url = result['result']
                    rb = await client.get(audio_url)
                    path = "data/voices/" + random_str() + '.wav'
                    with open(path, "wb") as f:
                        f.write(rb.content)
                    return path
    #firefly模式不再可用，仅作为以后的代码参考。
    elif mode == "firefly":
        datap = data
        uri = "wss://fs.firefly.matce.cn/queue/join"
        session_hash = "1fki0r8hg8mj"

        async with websockets.connect(uri) as ws:
            # 连接后发送的第一次请求
            await ws.send(json.dumps({"fn_index": 4, "session_hash": session_hash}))
            await ws.send(json.dumps(
                {"data": [datap.get("speaker")], "event_data": None, "fn_index": 1, session_hash: "1fki0r8hg8mj"}))
            while True:
                message = await ws.recv()
                print("Received '%s'" % message)
                data = json.loads(message)
                # 当消息中包含 'name' 并且是所需文件路径时
                if "output" in data and "data" in data["output"]:
                    ibn = data["output"]["data"][0]
                    exampletext = data["output"]["data"][1]
                    break
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"fn_index": 4, "session_hash": session_hash}))
            await ws.send(
                json.dumps({"data": [ibn], "event_data": None, "fn_index": 2, "session_hash": "1fki0r8hg8mj"}))
            while True:
                message = await ws.recv()
                data = json.loads(message)
                # 当消息中包含 'name' 并且是所需文件路径时
                if "output" in data and "data" in data["output"]:
                    for item in data["output"]["data"]:
                        if item and "name" in item and "/tmp/gradio/" in item["name"]:
                            # 提取文件的路径
                            example = item["name"]
                            # print(f"这里是请求结果：{example}")
                            break
                    break
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"fn_index": 4, "session_hash": session_hash}))
            # 连接后发送的第二次请求
            await ws.send(json.dumps({"data": [datap.get("text"), True, {"name": f"{example}",
                                                                         "data": f"https://fs.firefly.matce.cn/file={example}",
                                                                         "is_file": True, "orig_name": "audio.wav"},
                                               exampletext, 0, 90, 0.7, 1.5, 0.7, datap.get("speaker")],
                                      "event_data": None, "fn_index": 4, "session_hash": "1fki0r8hg8mj"}))

            # 等待并处理服务器的消息
            while True:
                message = await ws.recv()
                print("Received '%s'" % message)
                data = json.loads(message)
                # 当消息中包含 'name' 并且是所需文件路径时
                if "output" in data and "data" in data["output"]:
                    for item in data["output"]["data"]:
                        if item and "name" in item and "/tmp/gradio/" in item["name"]:
                            # 提取文件的路径
                            file_path = item["name"]
                            # 拼接 URL
                            full_url = f"https://fs.firefly.matce.cn/file={file_path}"
                            break
                    break
            p = "data/voices/" + random_str() + '.wav'
            async with httpx.AsyncClient(timeout=200) as client:
                r = await client.get(full_url)
                with open(p, "wb") as f:
                    f.write(r.content)
                return p
#modelscopeTTS v2，对接崩铁语音合成器
async def modelscopeV2(speaker,text):
    # 第一个请求的URL和参数
    queue_join_url = "https://s5k.cn/api/v1/studio/gally16/Bert-VITS21.x/gradio/queue/join"
    queue_join_params = {
        "backend_url": "/api/v1/studio/gally16/Bert-VITS21.x/gradio/",
        "sdk_version": "4.8.0",
        "t": "1722421391963",
        "studio_token": "f6325151-b86a-44d8-ba1d-aa95c485b173",
        "fn_index": "3",
        "session_hash": "wlev3x7dnvb"
    }

    # 第二个请求的URL和headers
    queue_data_url = "https://s5k.cn/api/v1/studio/gally16/Bert-VITS21.x/gradio/queue/data"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "connection": "keep-alive",
        "content-type": "application/json",
        "cookie": "_xsrf=2|6f60a475|a5b476579343255f3f4497ee1f7f3c4e|1722420837; _ga_R1FN4KJKJH=GS1.1.1722421405.7.0.1722421405.0.0.0; _ga=GA1.2.1599116772.1719823591; _gid=GA1.2.696222127.1722421405; _gat_gtag_UA_156449732_1=1",
        "origin": "https://s5k.cn",
        "referer": "https://s5k.cn/inner/studio/gradio?backend_url=/api/v1/studio/gally16/Bert-VITS21.x/gradio/&sdk_version=4.8.0&t=1722421391963&studio_token=f6325151-b86a-44d8-ba1d-aa95c485b173",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "x-studio-token": "f6325151-b86a-44d8-ba1d-aa95c485b173"
    }

    # 准备第二个请求的数据
    data_template = {
        "data": [text, speaker, 0.2, 0.6, 0.8, 1],
        "event_data": None,
        "fn_index": 3,
        "trigger_id": 37,
        "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider"],
        "session_hash": "wlev3x7dnvb",
        "event_id": ""  # 这里将会填入从第一个请求中获取的 event_id
    }

    # 发起第一个请求
    with httpx.Client(headers=headers,timeout=20) as client:
        count=0
        with client.stream("GET", queue_join_url, params=queue_join_params) as response:
            for event in response.iter_text():
                if event:
                    event_data = json.loads(event.replace("data:","").replace(" ",""))
                    if event_data.get("msg") == "send_data":
                        event_id = event_data.get("event_id")
                        data_template["event_id"] = event_id
                        response = client.post(queue_data_url, json=data_template, headers=headers)
                    # 持续监听第一个请求的后续结果
                    elif event_data.get("msg") == "process_completed":
                        p="./test.wav"
                        newurl=f"https://s5k.cn/api/v1/studio/gally16/Bert-VITS21.x/gradio/file={event_data['output']['data'][0]['path']}"
                        async with httpx.AsyncClient(timeout=200, headers=headers) as client:
                            r = await client.get(newurl)
                            with open(p, "wb") as f:
                                f.write(r.content)
                            return p
                    count+=1
                    if count>10:
                        raise Exception("Exceeded 10 events without entering return branch.")
async def fetch_FishTTS_ModelId(proxy, Authorization, speaker):
    proxies = {
        "http://": proxy,
        "https://": proxy
    }

    url = "https://api.fish.audio/model"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Authorization": Authorization,
        "Origin": "https://fish.audio",
        "Referer": "https://fish.audio/",
        "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
    }

    params = {
        "page_size": 10,
        "page_number": 1,
        "self": "false",
        "title": speaker
    }
    if proxy == "" or proxy == " ":
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                # print(data)
                return data["items"][0]["_id"]
    else:
        async with httpx.AsyncClient(proxies=proxies, timeout=20) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                #print(data)
                return data["items"][0]["_id"]


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


async def outVits(data):
    speaker = data.get("speaker")
    text = data.get("text")
    # os.system("where python")
    #p = random_str() + ".mp3"
    #p = "data/voices/" + p
    p = "data/voices/" + random_str() + '.wav'
    url = f"https://api.lolimi.cn/API/yyhc/y.php?msg={text}&speaker={speaker}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url)
        newUrl = r.json().get("music")
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
        "session_hash": "xjwen214wqf"
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