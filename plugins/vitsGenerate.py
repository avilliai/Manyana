# -*- coding: utf-8 -*-
import json
import os
import subprocess
from asyncio import sleep

import httpx

from plugins.newLogger import newLogger

async def taffySayTest(data):
    url = "http://localhost:9080/synthesize"  # 后端服务的地址
    # 请求参数
    async with httpx.AsyncClient(timeout=200) as client:
        await client.post(url, json=json.dumps(data))

async def voiceGenerate(data):
    # 向本地 API 发送 POST 请求
    if "MoeGoe.py" in os.listdir():
        import MoeGoe.voiceGenerate as vg
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
        url = 'http://localhost:9081/synthesize'
        data = json.dumps(data)
        try:
            async with httpx.AsyncClient(timeout=200) as client:
                await client.post(url, json=data)
        except:
            pass
    print("语音生成完成")