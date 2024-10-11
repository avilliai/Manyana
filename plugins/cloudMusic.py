import asyncio

import httpx
import requests

from plugins.newsEveryDay import get_headers
from plugins.toolkits import newLogger

# 定义请求的URL
logger=newLogger()

async def newCloudMusic(musicname):
    url = f"http://api.caonmtx.cn/api/wangyi.php?msg={musicname}"
    async with httpx.AsyncClient(timeout=None, headers=get_headers()) as client:
        r = await client.get(url)
        return r.json().get("content")


async def newCloudMusicDown(musicid, downloadMusicUrl=False,onlyUrl=False):
    path = 'data/music/musicCache/' + str(musicid) + '.mp3'
    try:
        newR = f"https://api.bducds.com/api/music.163/?id={musicid}"
        async with httpx.AsyncClient(timeout=None, headers=get_headers()) as client:
            r2 = await client.get(newR)
            if onlyUrl:
                return r2.json()["data"][0]["url"]
            # print(r.json()["song_url"])
            waf = await client.get(r2.json()["data"][0]["url"])
            with open(path, "wb") as f:
                f.write(waf.content)
            if downloadMusicUrl:
                return path, r2.json()["data"][0]["url"]
            else:
                return path
    except:
        logger.error("解析源1失效")
    try:
        url = "https://api.toubiec.cn/api/music_v1.php"
        headers = {
            "referer": "https://api.toubiec.cn/wyapi.html",
            "Origin": "https://api.toubiec.cn",
            "Token": "49985bad586de8a12e00cb964674a319",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
        }
        data = {"url": f"https://music.163.com/#/song?id={musicid}", "level": "exhigh", "type": "song",
                "token": "49985bad586de8a12e00cb964674a319"}

        async with httpx.AsyncClient(headers=headers, timeout=20) as client:
            r2 = await client.post(url, json=data)
            waf = await client.get((r2.json()["url_info"]["url"]))
            with open(path, "wb") as f:
                f.write(waf.content)
            if downloadMusicUrl:
                return path, r2.json()["url_info"]["url"]
            else:
                return path
    except:
        logger.error("解析源2失效")
    try:
        url = f"https://api.injahow.cn/meting/?type=song&id={musicid}"
        async with httpx.AsyncClient(headers=get_headers(), timeout=20) as client:
            r2 = await client.get(url)
            # print(r2.json()[0]["url"])
            waf = await client.get(r2.json()[0]["url"])
            wbf = await client.get(waf.headers.get("location"))
            with open(path, "wb") as f:
                f.write(wbf.content)
            if downloadMusicUrl:
                return path, waf.headers.get("location")
            else:
                return path
    except Exception as e:
        logger.error("解析源3失效")
    raise Exception("所有解析源都未获取到结果！")




async def cccdddm(musicname):
    url = 'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s=' + musicname + '&type=1&offset=0&total=true&limit=20'
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
