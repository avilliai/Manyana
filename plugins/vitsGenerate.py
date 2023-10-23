# -*- coding: utf-8 -*-
import json
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
    url = 'http://localhost:9081/synthesize'
    data = json.dumps(data)
    try:
        async with httpx.AsyncClient(timeout=200) as client:
            await client.post(url, json=data)
    except:
        pass
    print("语音生成完成")