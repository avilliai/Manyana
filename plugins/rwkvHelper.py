import asyncio

import httpx
import requests
import websockets
#from gradio_client import Client

url="http://127.0.0.1:8000/chat/completions"
async def rwkvHelper(text):
    async with httpx.AsyncClient(timeout=None) as client:
        data = {"messages": [{"role": "user","content": text}],"model": "rwkv","stream": False,"max_tokens": 1000,"temperature": 1.2,"top_p": 0.5,"presence_penalty": 0.4,"frequency_penalty": 0.4}
        r = await client.post(url,json=data)
        #print(r.json())
        #print(r.json().get("response"))
        return r.json().get("response")

'''async def onlineRWKV(text):
    client = Client(src="https://3aabd0bfae0d9019cf.gradio.live/",proxies={"http": "http://127.0.0.1:1080"})
    result = client.predict(
                    'null',	# str (Option from: []) in '请选择角色' Dropdown component
                    fn_index=2
    )
    print(result)


if __name__ == '__main__':


    client = Client("https://11d9ad68e4a47fcb8a.gradio.live/")
    re=client.submit("hello")

    print(re)
    #asyncio.run(onlineRWKV("你好"))'''