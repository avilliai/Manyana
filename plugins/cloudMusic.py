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
    path = 'data/music/musicCache/' + str(musicid) + '.mp3'

    newR = f"https://dataiqs.com/api/netease/music/?type=songid&id={musicid}"
    async with httpx.AsyncClient(timeout=None, headers=get_headers()) as client:
        r2 = await client.get(newR)
        # print(r.json()["song_url"])
    waf = requests.get(r2.json()["song_url"], timeout=20).content
    with open(path, "wb") as f:
        f.write(waf)
    if downloadMusicUrl:
        return path, r2.json()["song_url"]
    else:
        return path


'''import os, pilk
from pydub import AudioSegment

async def convert_to_silk(media_path: str) -> str:
    """将输入的媒体文件转出为 silk, 并返回silk路径"""
    media = AudioSegment.from_file(media_path)
    pcm_path = os.path.basename(media_path)
    rrr=media_path.replace(pcm_path,"")
    #print(rrr)
    pcm_path = os.path.splitext(pcm_path)[0]
    silk_path = rrr+pcm_path + '.silk'
    pcm_path += '.pcm'
    pcm_path=rrr+pcm_path
    print(silk_path,pcm_path)
    media.export(pcm_path, 's16le', parameters=['-ar', str(media.frame_rate), '-ac', '1']).close()
    pilk.encode(pcm_path, silk_path, pcm_rate=media.frame_rate, tencent=True)

    return silk_path'''


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

#r=asyncio.run(cccdddm("しゃろう superstar"))
#print(r)
# musicDown("http://music.163.com/song/media/outer/url?id=1940303073.mp3")
