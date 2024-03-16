import asyncio
import os
import random

import httpx
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
        base_url="https://api.xty.app/v1",
        api_key=os.environ.get("OPENAI_API_KEY"),
        http_client=httpx.Client(base_url="https://api.xty.app/v1", follow_redirects=True)
    )
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的主人喵"})
    chat_completion = client.chat.completions.create(
        messages=prompt,
        model="gpt-3.5-turbo",
        stream=False,
    )
    # print(chat_completion.choices[0].message.content)
    return {"role": "assistant", "content": chat_completion.choices[0].message.content}
