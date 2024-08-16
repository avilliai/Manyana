import asyncio

import httpx
import requests

from plugins.newsEveryDay import get_headers


# 定义请求的URL


async def newCloudMusic(musicname):
    url = f"http://api.caonmtx.cn/api/wangyi.php?msg={musicname}"
    async with httpx.AsyncClient(timeout=None, headers=get_headers()) as client:
        r = await client.get(url)
        return r.json().get("content")


async def newCloudMusicDown(musicid, downloadMusicUrl=False):
    path = f'data/music/musicCache/{musicid}.mp3'

    url = "https://api.toubiec.cn/api/music_v1.php"
    headers = {
        "referer": "https://api.toubiec.cn/wyapi.html",
        "Origin": "https://api.toubiec.cn",
        "Token": "49985bad586de8a12e00cb964674a319",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
    }
    data = {"url": f"https://music.163.com/#/song?id={musicid}", "level": "exhigh", "type": "song",
            "token": "49985bad586de8a12e00cb964674a319"}

    async with httpx.AsyncClient() as client:
        r2 = await client.post(url, headers=headers, json=data)
    waf = requests.get(r2.json()["url_info"]["url"], timeout=20).content
    with open(path, "wb") as f:
        f.write(waf)
    if downloadMusicUrl:
        return path, r2.json()["url_info"]["url"]
    else:
        return path



async def cccdddm(musicname):
    # 导入selenium库
    url = 'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s=' + musicname + '&type=1&offset=0&total=true&limit=20'
    #DAT={'s': musicname,'offset': 1,'limit': 1,'type': 1}
    #url = "http://music.wandhi.com/?name=" + musicname + "&type=netease"
    #header=get_headers()

    #r=requests.post(url)
    #print(r.text)
    async with httpx.AsyncClient(timeout=None, headers=get_headers()) as client:
        r = await client.post(url)
        #print(r.json().get("result").get("songs"))
        #print(r.json().get("result").get("songs")[0].get("id"))
        newa = []

        for i in r.json().get("result").get("songs"):
            #newa.append([i.get("name"),i.get("id"),i.get("artists")[0].get("img1v1Url"),i.get("artists")[0].get("name")])
            newa.append(
                [i.get("name"), i.get("id"), i.get("artists")[0].get("name")])
        return newa
        #id=r.json().get("result").get("songs")[0]
        #name=r.json().get("result").get("songs")[0].get("name")


async def musicDown(id, name):
    url = "http://music.163.com/song/media/outer/url?id=" + str(id) + ".mp3"
    waf = requests.get(url).content
    path = 'data/music/musicCache/' + name + '.mp3'

    # path=await convert_to_silk(path)

    with open(path, "wb") as f:
        f.write(waf)
    return path
#asyncio.run(1940303073)
# musicDown("http://music.163.com/song/media/outer/url?id=1940303073.mp3")
