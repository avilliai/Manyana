import asyncio

import httpx


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
        return r.text
if __name__ == '__main__':
    prompt=[]
    while True:
        text=input("textHere:")
        #print(prompt)
        prompt.append({"role": "user", "content":text})
        text1=asyncio.run(lolimigpt(prompt,"你是yucca，yucca是一个人工智能。1、yucca的形象与设定属于二次元动漫中的女孩子，说话喜欢带上啊，哦等语气词。2、yucca尤其喜欢用颜文字或表情符号，在日常聊天中会尽可能使用颜文字。3、yucca的性格非常天真，但拥有丰富的文学与戏剧方面的知识，并且对自己的能力非常自信。4、yucca在生活中会经常犯一些小错误。yucca十分依赖并喜欢指挥"))
        prompt.append({"role": "assistant", "content":text1})
        print(text1)