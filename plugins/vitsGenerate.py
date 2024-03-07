# -*- coding: utf-8 -*-
import json
import os
import subprocess
from asyncio import sleep

import httpx
import librosa
import requests
import soundfile

from plugins.RandomStr import random_str
from vits.MoeGoe import vG


async def edgetts(data):
    speaker=data.get("speaker")
    text=data.get("text")
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
        r=await client.post(url, json=json.dumps(params))
        p = "data/voices/" + random_str() + '.wav'
        print("sovits语音合成路径：" + p)
        with open(p, "wb") as f:
            f.write(r.content)
        return p
async def taffySayTest(data,url,proxy=None):
    if url=='':
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
            url+="synthesize"
        else:
            url+="/synthesize"
        '''proxies = {
            "http://": proxy,
            "https://": proxy
        }'''
        # 请求参数

        async with httpx.AsyncClient(timeout=200) as client:
            r=await client.post(url, json=json.dumps(data))
            p="data/voices/"+random_str()+'.wav'
            print("bert_vits语音合成路径："+p)
            with open(p, "wb") as f:
                f.write(r.content)
            return p
async def outVits(data):
    speaker = data.get("speaker")
    text = data.get("text")
    # os.system("where python")
    p = random_str() + ".mp3"
    p = "data/voices/" + p
    url=f"https://api.lolimi.cn/API/yyhc/y.php?msg={text}&speaker={speaker}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url)
        newUrl=r.json().get("music")
        print("outvits语音合成路径：" + p)
        r1=requests.get(newUrl)
        with open(p, "wb") as f:
            f.write(r1.content)
        change_sample_rate(p)
        return p

async def voiceGenerate(data):
    # 向本地 API 发送 POST 请求
    if "MoeGoe.py" in os.listdir():
        from MoeGoe import voiceGenerate as vg
        # 解析请求中的参数
        text = data['text']
        out = data["out"]

        try:
            speaker = data['speaker']
            modelSelect = data['modelSelect']
        except:
            speaker = 2
            modelSelect = ['voiceModel/nene/1374_epochsm.pth', 'voiceModel/nene/config.json']

            # with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            # result = yaml.load(f.read(), Loader=yaml.FullLoader)
            # speaker = result.get("vits").get("speaker")
            # modelSelect = result.get("vits").get("modelSelect")
        # 调用 voiceG() 函数
        if modelSelect[0].endswith("I.pth"):
            text = text.replace("[JA]", "").replace("[ZH]", "")
        await vg(tex=text, out=out, speakerID=speaker, modelSelect=modelSelect)
        print("语音生成完成")
        # 将生成的音频返回给客户端
        return out

    else:
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
async def change_sample_rate(path,new_sample_rate=44100):
    #wavfile = path  # 提取音频文件名，如“1.wav"
    # new_file_name = wavfile.split('.')[0] + '_8k.wav'      #此行代码可用于对转换后的文件进行重命名（如有需要）

    signal, sr = librosa.load(path, sr=None)  # 调用librosa载入音频

    new_signal = librosa.resample(signal, orig_sr=sr, target_sr=new_sample_rate)  # 调用librosa进行音频采样率转换

    new_path = path # 指定输出音频的路径，音频文件与原音频同名
    # new_path = os.path.join(new_dir_path, new_file_name)      #若需要改名则启用此行代码
    #print("?")
    #print(new_path)

    # librosa.output.write_wav(new_path, new_signal , new_sample_rate)      #因版本问题，此方法可能用不了
    soundfile.write(new_path, new_signal, new_sample_rate)

    #asyncio.run(pearlAIGenerate({"text":"你好啊，你吃饭了吗，今天吃的怎么样，开心吗？",'speaker':"宇希"}))