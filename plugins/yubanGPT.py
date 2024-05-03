import asyncio
import json
import urllib

import httpx
import requests


async def yubanGPTReply(text,id=None):
    if id!=None:
        url="https://ybapi.cn/API/gpt.php?type=1&msg="+text+"&id="+id
    else:
        url="https://ybapi.cn/API/gpt.php?type=1&msg="+text
    async with httpx.AsyncClient(timeout=100) as client: #100s超时
        r = await client.get(url)  #发起请求
        return r.json().get("text"), r.json().get("id")  #返回结果
async def luoyueGPTReply(text,id=None):
    if id!=None:
        url="https://api.vkeys.cn/API/gpt?msg="+text+"&session_id="+id
    else:
        url="https://api.vkeys.cn/API/gpt?msg="+text
    async with httpx.AsyncClient(timeout=100) as client: #100s超时
        r = await client.get(url)  #发起请求
    return r.json().get("data").get("content"), r.json().get("session_id")  #返回结果
async def lolimigpt(prompt,meta):
    url=f"https://api.lolimi.cn/API/AI/mfcat3.5.php?sx={meta}&msg={str(prompt)}"
    async with httpx.AsyncClient(timeout=100) as client: #100s超时
        r = await client.get(url)  #发起请求
        return {"role":"assistant","content":r.text}

async def lolimigpt2(prompt,meta):
    url="https://api.lolimi.cn/API/AI/c.php?"
    prompt.insert(0,{"role":"user","content":meta})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色"})
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url=url,json=prompt)
        return {"role":"assistant","content":r.text}
def relolimigpt2(prompt,meta):
    url = "https://api.lolimi.cn/API/AI/c.php?"
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色"})
    r = requests.post(url=url, json=prompt)
    return {"role": "assistant", "content": r.text}

if __name__ == '__main__':
    k = kimi([{"role": "user", "content": "你好"}])
    print(k)