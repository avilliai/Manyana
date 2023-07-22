# -*- coding: utf-8 -*-
import json
import subprocess

import httpx

from plugins.newLogger import newLogger


async def voiceGenerate(data):
    logger = newLogger()
    # 向本地 API 发送 POST 请求
    url = 'http://localhost:9080/synthesize'
    data = json.dumps(data)
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            await client.post(url, json=data)
    except:
        logger.error("语音生成服务端意外关闭，执行重新唤醒")
        subprocess.Popen(["venv/Scripts/python.exe", "flask_voice.py"], cwd="vits")
        logger.info("服务端重新唤醒完成，重新执行语音生成")
        await voiceGenerate(data,logger)
    logger.info("语音生成完成")