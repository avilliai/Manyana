import httpx
import json
import random

from pytubefix import Channel, YouTube, Playlist, Stream

from plugins.newsEveryDay import get_headers

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = result.get("proxy")
    proxies = {
        "http": proxy,
        "https": proxy
    }
    pyproxies = {       #pytubefix代理
        "http": proxy,
        "https": proxy
    }

ASMR_channels = ['@emococh','@-gabisroom-4153']
pushed_videos = ['HG-U_0nazgc']

client = httpx.AsyncClient(headers=get_headers(),timeout=100)

async def ASMR_today():
    global ASMR_channels     #ASMR频道列表
    global  pushed_videos    #已推送ASMR列表
    channel = random.choice(ASMR_channels)
    c = Channel(url=f'https://www.youtube.com/{channel}',proxies=pyproxies)
    athor = c.channel_name
    video_idlist=[]
    for url in c.video_urls:
        video_id=str(url).split('=')[1].replace('>', '')
        video_idlist.append(video_id)
    # video_idlist=list(set(video_idlist)-set(pushed_videos))    #该方法可以去除重复ASMR,但是会导致ASMR顺序不确定
    for pushed_video in pushed_videos:      #去除已推送ASMR
        if pushed_video in video_idlist:
            video_idlist.remove(pushed_video)

    try:
        video_id=video_idlist[0]    #获取一个最新的未推送ASMR 
    except:
        print(f"{athor}频道没有未推送的ASMR,从投稿中随机选择")    #如果没有未推送的ASMR,从该频道投稿中随机选择
        video_id=str(random.choice(c.video_urls)).split('=')[1].replace('>', '')
    url='https://www.youtube.com/watch?v='+video_id
    yt = YouTube(url)
    title = yt.title
    length = yt.length
    pushed_videos.append(url)
    return athor,title,video_id,length

async def ASMR_random():
    global ASMR_channels     #ASMR频道列表
    channel = random.choice(ASMR_channels)
    c = Channel(url=f'https://www.youtube.com/{channel}',proxies=pyproxies)
    athor = c.channel_name
    video_id=str(random.choice(c.video_urls)).split('=')[1].replace('>', '') #从该频道投稿中随机选择
    url='https://www.youtube.com/watch?v='+video_id
    yt = YouTube(url)
    title = yt.title
    length = yt.length
    pushed_videos.append(url)
    return athor,title,video_id,length

async def get_audio(video_id):
    url=f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url=url,proxies=pyproxies)
    title = yt.title

    url=f"https://ripyoutube.com/mates/en/convert?id={video_id}"    #从ripyoutube获取音频下载地址
    data ={
        'platform': 'youtube',
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'title': title,
        'id': 'iCMgE7C1JltWuflTeD0TJm==',
        'ext': 'mp3',
        'note': '128k',
        'format': ''
    }

    response = await client.post(url=url,data=data)
    audiourl = response.json()['downloadUrlX']
    response = await client.get(audiourl)
    path = "data\Youtube\ASMR.mp3"
    with open(path, 'wb') as f:
        f.write(response.content)
    audiourl = file_chain(path)
    return audiourl

async def get_video(video_id):
    url=f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url=url,proxies=pyproxies)
    title = yt.title

    url=f"https://ripyoutube.com/mates/en/convert?id={video_id}"    #从ripyoutube获取视频下载地址
    data ={
        'platform': 'youtube',
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'title': title,
        'id': 'iCMgE7C1JltWuflTeD0TJn==',
        'ext': 'mp4',
        'note': '1080p',
        'format': 137
    }

    response = await client.post(url=url,data=data)
    videourl = response.json()['downloadUrlX']
    return videourl

async def get_img(video_id):
    path =f"data/Youtube/{video_id}.jpg"
    url=f"https://i.ytimg.com/vi/{video_id}/hq720.jpg"    #下载视频封面
    client = httpx.AsyncClient(headers=get_headers(),proxies=proxies,timeout=100)
    response = await client.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    imgurl = file_chain(path)
    return imgurl

async def file_chain(path):     ##上传文件到ffsup.com并取得直链
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Sec-Ch-Ua' : '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile' : '?0',
    'Sec-Ch-Ua-Platform' : '"Windows"',
    'Sec-Fetch-Dest' : 'empty',
    'Sec-Fetch-Mode' : 'cors',
    'Sec-Fetch-Site' : 'same-site',
    }

    url = 'https://upload.ffsup.com/'
    file = {'file': open(path, 'rb')}
    response = await client.post(url, files=file, headers=headers)
    return response.json()['data']['url']