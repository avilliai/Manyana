# -*- coding: utf-8 -*-
import asyncio
import os

import google.generativeai as genai
import httpx
#官方sdk的prompt和使用post请求的prompt结构不同，需要进行转换
def promptConvert(input_list):
    for item in input_list:
        new_parts = []
        for part in item.get('parts', []):
            if isinstance(part, dict):  # 如果part是字典，保持不变
                new_parts.append(part)
            else:  # 如果part不是字典，转换成{'text': part}
                new_parts.append({'text': part})
        item['parts'] = new_parts
    return input_list
def convert_content_to_parts_and_role(input_list):
    for item in input_list:
        # 转换'content'键到'parts'
        if 'content' in item:
            item['parts'] = [item['content']]
            del item['content']
        # 转换'role'值从"assistant"到"model"
        if item.get('role') == "assistant":
            item['role'] = "model"
    return input_list
safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]
async def geminirep(ak,messages,bot_info,GeminiRevProxy=""):
    messages.insert(0,{"role": "user", "parts": [bot_info]})
    messages.insert(1,{"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]})
    messages=convert_content_to_parts_and_role(messages)
    messages = promptConvert(messages)
    if GeminiRevProxy=="" or GeminiRevProxy==" ":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={ak}"
    else:
        url = f"{GeminiRevProxy}/v1beta/models/gemini-1.5-flash:generateContent?key={ak}"
    r = await geminiCFProxy(messages, url)
    return r.rstrip()
async def geminiCFProxy(messages,url):
    #print(requests.get(url,verify=False))
    async with httpx.AsyncClient(timeout=100,verify=False) as client:

        r = await client.post(url,json={"contents":messages,"safetySettings":[{'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', "threshold": "BLOCK_None"},
         {'category': 'HARM_CATEGORY_HATE_SPEECH', "threshold": "BLOCK_None"},
         {'category': 'HARM_CATEGORY_HARASSMENT', "threshold": "BLOCK_None"},
         {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', "threshold": "BLOCK_None"}]})
        return r.json()['candidates'][0]["content"]["parts"][0]["text"]
    #r=requests.post(url,json=message,verify=False)
