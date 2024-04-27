# -*- coding:utf-8 -*-
import asyncio
import os
import random

import httpx
import requests
from openai import OpenAI

def gptOfficial(prompt,apikeys,proxy,bot_info):
    os.environ["OPENAI_API_KEY"] = random.choice(apikeys)
    os.environ["http_proxy"] = proxy  # 指定代理，解决连接问题
    os.environ["https_proxy"] = proxy  # 指定代理，解决连接问题
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    prompt.insert(0,{"role":"user","content":bot_info})
    chat_completion = client.chat.completions.create(
        messages=prompt,
        model="gpt-3.5-turbo",
        stream=False,
    )
    #print(chat_completion.choices[0].message.content)
    return {"role":"assistant","content":chat_completion.choices[0].message.content}
def gptUnofficial(prompt,apikeys,proxy,bot_info):
    os.environ["OPENAI_API_KEY"] = random.choice(apikeys)
    client = OpenAI(
        # This is the default and can be omitted
        base_url="https://api.chatanywhere.com.cn",
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求，我会根据您的需求扮演好您设定的角色。"})
    chat_completion = client.chat.completions.create(
        messages=prompt,
        model="gpt-3.5-turbo",
        stream=False,
    )
    # print(chat_completion.choices[0].message.content)
    return {"role": "assistant", "content": chat_completion.choices[0].message.content}
def kimi(prompt,bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求，我会根据您的需求扮演好您设定的角色。"})
    prompt=str(prompt).replace("\"","%22").replace("\'","%22")

    url = f"https://api.alcex.cn/API/ai/kimi.php?messages={prompt}"
    #print(url)
    r=requests.get(url).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}
def qingyan(prompt,bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求，我会根据您的需求扮演好您设定的角色。"})
    prompt=str(prompt).replace("\"","%22").replace("\'","%22")

    url = f"https://api.alcex.cn/API/chatglm/?messages={prompt}"
    #print(url)
    r=requests.get(url).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}

def lingyi(prompt,bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求，我会根据您的需求扮演好您设定的角色。"})
    prompt=str(prompt).replace("\"","%22").replace("\'","%22")

    url = f"https://api.alcex.cn/API/ai/zeroyi.php?messages={prompt}"
    #print(url)
    r=requests.get(url).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}
def stepAI(prompt,bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求，我会根据您的需求扮演好您设定的角色。"})
    prompt=str(prompt).replace("\"","%22").replace("\'","%22")

    url = f"https://api.alcex.cn/API/ai/step.php?messages={prompt}"
    #print(url)
    r=requests.get(url).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}
def qwen(prompt,bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求，我会根据您的需求扮演好您设定的角色。"})
    prompt=str(prompt).replace("\"","%22").replace("\'","%22")

    url = f"https://api.alcex.cn/API/ai/qwen.php?messages={prompt}"
    #print(url)
    r=requests.get(url).json()
    print(r)
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}
def gptvvvv(prompt,bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求，我会根据您的需求扮演好您设定的角色。"})
    prompt=str(prompt).replace("\"","%22").replace("\'","%22")

    url = f"https://api.alcex.cn/API/gpt-4/v2.php?messages={prompt}&model=gpt-3.5-turbo"
    #print(url)
    r=requests.get(url).json()
    print(r)
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


