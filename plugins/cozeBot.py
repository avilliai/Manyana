# -*- coding: utf-8 -*-
import os

import requests

def cozeBotRep(url,text,proxy,channelid=None):
    os.environ["http_proxy"] = proxy
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "messages": text,
        "stream": False
    }

    r = requests.post(url, headers=headers, json=data)
    print(r)
    print(r.text)
    print(r)
    if r.status_code == 200:
        result = r.json()
        return result.get('choices')[0].get('message')

    else:
        print(f'Error: {r.status_code}')



#cozeBotRep(url,text,proxy)
#creatChannel("http://127.0.0.1:10809")