# -*- coding: utf-8 -*-
import json
import subprocess

import httpx
import psutil

def voiceGenerate(data):
    # 向本地 API 发送 POST 请求
    url = 'http://localhost:9080/synthesize'
    data = json.dumps(data)
    try:
        async with httpx.AsyncClient(timeout=200) as client:
            await client.post(url, json=data)
    except:
        print("语音生成服务端意外关闭，执行重新唤醒")
        # 关闭旧的 flask_voice 进程
        for p in psutil.process_iter():
            if p.name() == "flask_voice.py":
                p.kill()
        # 启动新的 flask_voice 进程
        subprocess.Popen(["python.exe", "flask_voice.py"], cwd="vits")
        print("服务端重新唤醒完成，重新执行语音生成")
        await voiceGenerate(data)
    print("语音生成完成")