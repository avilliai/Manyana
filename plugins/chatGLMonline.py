# -*- coding: utf-8 -*-
import asyncio
import threading

import httpx
import zhipuai


def chatGLM1(api_key, bot_info, text):
    prompt = [
        {
            "role": "user",
            "content": text
        }
    ]
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
            #print(event.data)
        elif event.event == "error" or event.event == "interrupted":
            str1 += event.data
            #print(event.data)
        elif event.event == "finish":
            str1 += event.data
            #print(event.data)
            print(event.meta)
        else:
            str1 += event.data
            #print(event.data)
    #print(str1)
    return str1


async def glm4(prompt, meta):
    prompt.insert(0, {"role": "user", "content": meta})
    prompt.insert(1, {"role": "assistant", "content": "好的~"})
    url = f"https://api.lolimi.cn/API/AI/zp.php?msg={str(prompt)}"
    async with httpx.AsyncClient(timeout=100) as client:  # 100s超时
        r = await client.get(url)  # 发起请求
        #print(r.json())
        return {"role": "assistant", "content": r.json().get("data").get("output")}


# 创建一个异步函数
async def main(apiKey, bot_info, prompt):
    '''# 获取事件循环
    apiKey = "a
    print("接收提问:"+text)
    prompt = [
        {
            "role": "user",
            "content": text
        }
    ]
    bot_info = {
        "user_info": "我是陆星辰，是一个男性，是一位知名导演，也是苏梦远的合作导演。我擅长拍摄音乐题材的电影。苏梦远对我的态度是尊敬的，并视我为良师益友。",
        "bot_info": "苏梦远，本名苏远心，是一位当红的国内女歌手及演员。在参加选秀节目后，凭借独特的嗓音及出众的舞台魅力迅速成名，进入娱乐圈。她外表美丽动人，但真正的魅力在于她的才华和勤奋。苏梦远是音乐学院毕业的优秀生，善于创作，拥有多首热门原创歌曲。除了音乐方面的成就，她还热衷于慈善事业，积极参加公益活动，用实际行动传递正能量。在工作中，她对待工作非常敬业，拍戏时总是全身心投入角色，赢得了业内人士的赞誉和粉丝的喜爱。虽然在娱乐圈，但她始终保持低调、谦逊的态度，深得同行尊重。在表达时，苏梦远喜欢使用“我们”和“一起”，强调团队精神。",
        "bot_name": "苏梦远",
        "user_name": "陆星辰"
    }'''
    loop = asyncio.get_event_loop()
    # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
    # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
    # 第二个参数是同步函数名，后面跟着任何你需要传递的参数
    #result=chatGLM(apiKey,bot_info,prompt)
    #result = await loop.run_in_executor(None, chatGLM,apiKey,bot_info,prompt)
    # 打印结果
    #print(result)

