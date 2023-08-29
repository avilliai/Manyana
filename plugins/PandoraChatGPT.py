# -*- coding: utf-8 -*-
import asyncio
import json
import subprocess
import uuid
from asyncio import sleep

import httpx
import requests




def ask_chatgpt(prompt, model, message_id, parent_message_id, conversation_id=None, stream=False):
    base_url="http://127.0.0.1:23459"
    data = {
        "prompt": prompt,
        "model": model,
        "message_id": message_id,
        "parent_message_id": parent_message_id,
        "stream": stream,
        "conversation_id": conversation_id,
    }
    if conversation_id is not None:
        data["conversation_id"] = conversation_id

    response = requests.post(f"{base_url}/api/conversation/talk", json=data)
    response_data = response.text
    r=requests.get(f"{base_url}/api/conversations")
    #print("会话列表：",r.json())

    if len(response_data.split("\n")) > 1:
        #print("继续之前的会话", response_data)
        response_data = json.loads(response_data)
    else:
        response_data = json.loads(response_data)

        #print("创建会话", response_data)
    parts = response_data['message']['content']['parts']
    # 将 parts 中的字符串连接起来形成完整的回复
    response_message = ''.join(parts)
    #print(response_message)
    if conversation_id==None:
        conversation_id = r.json().get("items")[0].get("id")
    return response_data["message"]['id'],conversation_id,response_message
if __name__ == '__main__':
    parent_message_id = None
    prompt = "我爱你啊！！！！！！！！！"
    conversation_id = None
    while True:
        # 向ChatGPT提问，等待其回复
        model = "text-davinci-002-render-sha"  # 选择一个可用的模型Default (GPT-3.5)：text-davinci-002-render-sha
        message_id = str(uuid.uuid4())  # 随机生成一个消息ID
        if parent_message_id is None:
            parent_message_id = "f0bf0ebe-1cd6-4067-9264-8a40af76d00e"

        print("当前conversation_id",conversation_id)
        # conversation_id = None
        parent_message_id,conversation_id = ask_chatgpt(prompt, model, message_id, parent_message_id, conversation_id)
        print("当前会话的id:", parent_message_id)
        print("当前conversation_id",conversation_id)
        prompt = str(input("请输入prompt："))

