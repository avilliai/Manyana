import asyncio

import httpx
import requests
import websockets


url="http://127.0.0.1:8000/chat/completions"
async def rwkvHelper(text):
    async with httpx.AsyncClient(timeout=100) as client:
        data = {"messages": [{"role": "user","content": text}],"model": "rwkv","stream": False,"max_tokens": 1000,"temperature": 1.2,"top_p": 0.5,"presence_penalty": 0.4,"frequency_penalty": 0.4}
        r = await client.post(url,json=data)
        return r.json().get('choices')[0].get("message").get("content")



if __name__ == '__main__':


    #client = Client("https://11d9ad68e4a47fcb8a.gradio.live/")
    #re=client.submit("hello")

    #print(re)
    asyncio.run(rwkvHelper("你好"))