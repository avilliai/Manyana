# -*- coding:utf-8 -*-
import copy
import os
import random

import httpx
import requests
import zhipuai
from openai import OpenAI


def gptOfficial(prompt, apikeys, proxy, bot_info, model):
    os.environ["OPENAI_API_KEY"] = random.choice(apikeys)
    os.environ["http_proxy"] = proxy  # 指定代理，解决连接问题
    os.environ["https_proxy"] = proxy  # 指定代理，解决连接问题
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    prompt_copy = copy.deepcopy(prompt)
    prompt_copy.insert(0, {"role": "user", "content": bot_info})
    prompt_copy.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    chat_completion = client.chat.completions.create(
        messages=prompt_copy,
        model=model,
        stream=False,
    )
    # print(chat_completion.choices[0].message.content)
    return {"role": "assistant", "content": chat_completion.choices[0].message.content}


def gptUnofficial(prompt, apikeys, transitURL, bot_info, model):
    os.environ["OPENAI_API_KEY"] = random.choice(apikeys)
    client = OpenAI(
        # This is the default and can be omitted
        base_url=transitURL,
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    prompt_copy = copy.deepcopy(prompt)
    prompt_copy.insert(0, {"role": "user", "content": bot_info})
    prompt_copy.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    chat_completion = client.chat.completions.create(
        messages=prompt_copy,
        model=model,
        stream=False,
    )
    # print(chat_completion.choices[0].message.content)
    return {"role": "assistant", "content": chat_completion.choices[0].message.content}


# 以下是api.alcex.cn的各种AI接口
def kimi(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")

    url = f"https://api.alcex.cn/API/ai/kimi.php?messages={prompt}"
    # print(url)
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def qingyan(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")

    url = f"https://api.alcex.cn/API/chatglm/?messages={prompt}"
    # print(url)
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def lingyi(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")

    url = f"https://api.alcex.cn/API/ai/zeroyi.php?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def stepAI(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")

    url = f"https://api.alcex.cn/API/ai/step.php?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def qwen(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")

    url = f"https://api.alcex.cn/API/ai/qwen.php?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def gptvvvv(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")

    url = f"https://api.alcex.cn/API/gpt-4/v2.php?messages={prompt}&model=gpt-3.5-turbo"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def Gemma(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/Gemma/?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def alcex_GPT3_5(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/gpt-3.5/?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def binggpt4(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/gpt-4/?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def grop(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/ai/grop.php?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def gpt4hahaha(prompt, meta):
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/gpt-4/v2.php?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def xinghuo(prompt, meta):
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的~"})
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/spark/?messages={str(prompt)}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def freeGemini(prompt, bot_info):
    prompt.insert(0, {"role": "user", "content": bot_info})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    pro1 = {"contents": prompt}
    prompt1 = str(pro1).replace("\"", "%22").replace("\'", "%22").rstrip()
    r = "{%22contents%22:[{%22parts%22:[{%22text%22:%22%E4%BD%A0%E5%A5%BD%22}]}]}"

    url = f"https://api.alcex.cn/API/gemini/?q={prompt1}"
    r = requests.get(url)
    return {"role": "assistant", "content": r.json()["answer"]["candidates"][0]["content"]["parts"][0]["text"]}


# 以上是api.alcex.cn的各种AI接口

def localAurona(prompt, meta):
    url = "http://127.0.0.1:3040/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer fff"}
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    data = {
        "model": "gpt-3.5-turbo",
        "messages": prompt,
        "stream": False
    }
    r = requests.post(url, headers=headers, json=data, timeout=20)


def anotherGPT35(prompt, id):
    prompt = prompt[-1]["content"]
    url = f"https://api.shenke.love/api/ChatGPT.php?msg={prompt}&id={id}"
    r = requests.get(url, timeout=20).json()["data"]["message"]
    return {"role": "assistant", "content": r}


def chatGLM(api_key, bot_info, prompt):
    zhipuai.api_key = api_key
    response = zhipuai.model_api.sse_invoke(
        model="characterglm",
        meta=bot_info,
        prompt=prompt,
        incremental=True
    )
    str1 = ""
    for event in response.events():
        if event.event == "add":
            str1 += event.data
        elif event.event == "error" or event.event == "interrupted":
            str1 += event.data
        elif event.event == "finish":
            str1 += event.data

        else:
            str1 += event.data
    return str1


async def yubanGPTReply(text, id=None):
    if id is not None:
        url = "https://ybapi.cn/API/gpt.php?type=1&msg=" + text + "&id=" + id
    else:
        url = "https://ybapi.cn/API/gpt.php?type=1&msg=" + text
    async with httpx.AsyncClient(timeout=20) as client:  # 100s超时
        r = await client.get(url)  # 发起请求
        return r.json().get("text"), r.json().get("id")  # 返回结果


async def luoyueGPTReply(text, id=None):
    if id is not None:
        url = "https://api.vkeys.cn/API/gpt?msg=" + text + "&session_id=" + id
    else:
        url = "https://api.vkeys.cn/API/gpt?msg=" + text
    async with httpx.AsyncClient(timeout=20) as client:  # 100s超时
        r = await client.get(url)  # 发起请求
    return r.json().get("data").get("content"), r.json().get("session_id")  # 返回结果


async def lolimigpt(prompt, meta):
    url = f"https://api.lolimi.cn/API/AI/mfcat3.5.php?sx={meta}&msg={str(prompt)}"
    async with httpx.AsyncClient(timeout=20) as client:  # 100s超时
        r = await client.get(url)  # 发起请求
        return {"role": "assistant", "content": r.text}


async def lolimigpt2(prompt, meta):
    url = "https://api.lolimi.cn/API/AI/c.php?"
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url=url, json=prompt)
        return {"role": "assistant", "content": r.text}


def relolimigpt2(prompt, meta):
    url = "https://api.lolimi.cn/API/AI/c.php?"
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"})
    r = requests.post(url=url, json=prompt, timeout=20)
    return {"role": "assistant", "content": r.text}


def glm4hahaha(prompt, meta):
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的~"})
    url = f"https://api.lolimi.cn/API/AI/zp.php?msg={str(prompt)}"
    r = requests.get(url, timeout=20)
    return {"role": "assistant", "content": r.json().get("data").get("output")}


if __name__ == '__main__':
    k = binggpt4([{"role": "user", "content": "谁赢得了2020年的世界职业棒球大赛?"},
                  {"role": "assistant", "content": "洛杉矶道奇队在2020年赢得了世界职业棒球大赛冠军."},
                  {"role": "user", "content": "它在哪里举办的?"}], "你是一只猫娘")
    print(k)
