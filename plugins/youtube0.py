import yaml
import httpx
import random
from pytubefix import Channel, YouTube

from plugins.newsEveryDay import get_headers

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = result.get("proxy")
    proxies = {
        "http://": proxy,
        "https://": proxy
    }
    pyproxies = {       #pytubefix代理
        "http": proxy,
        "https": proxy
    }

with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
ASMR_channels = result.get("ASMR").get("channels")
 
with open('data/ASMR.yaml', 'r', encoding='utf-8') as f:
    ASMRpush = yaml.load(f.read(), Loader=yaml.FullLoader)
pushed_videos = ASMRpush.get("已推送ASMR")

client = httpx.AsyncClient(headers=get_headers(),timeout=100)

async def ASMR_today():
    global ASMR_channels     #ASMR频道列表
    global  pushed_videos    #已推送ASMR列表
    channel = random.choice(ASMR_channels)
    c = Channel(url=f'https://www.youtube.com/{channel}',proxies=pyproxies)
    athor = c.channel_name

    video_idlist = [video_url.video_id for video_url in c.video_urls]       #获取该频道所有ASMR视频id
    try:
        video_id = next(video_id for video_id in video_idlist if video_id not in pushed_videos)     #过滤已推送ASMR,不改变时间排序
        pushed_videos.append(video_id)
        ASMRpush["已推送ASMR"] = pushed_videos
        with open('data/ASMR.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(ASMRpush, file, allow_unicode=True)
    except:
        print(f"{athor}频道没有未推送的ASMR,从投稿中随机选择")    #如果没有未推送的ASMR,从该频道投稿中随机选择
        video_id = random.choice(c.video_urls).video_id
    url='https://www.youtube.com/watch?v='+video_id
    yt = YouTube(url)
    title = yt.title
    length = yt.length
    return athor,title,video_id,length

async def ASMR_random():
    global ASMR_channels     #ASMR频道列表
    channel = random.choice(ASMR_channels)
    c = Channel(url=f'https://www.youtube.com/{channel}',proxies=pyproxies)
    athor = c.channel_name
    video_id=str(random.choice(c.video_urls)).split('=')[1].replace('>', '') #从该频道投稿中随机选择
    url='https://www.youtube.com/watch?v='+video_id
    yt = YouTube(url,proxies=pyproxies)
    title = yt.title
    length = yt.length
    return athor,title,video_id,length

async def get_audio(video_id):
    url=f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url=url,client='IOS',proxies=pyproxies)
    path = f"data/music/musicCache/{video_id}.mp3"
    ys = yt.streams.get_audio_only()
    ys.download(mp3=True, output_path="data/music/musicCache/",filename=video_id)
    audiourl =await file_chain(path)
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
    path =f"data/pictures/cache/{video_id}.jpg"
    url=f"https://i.ytimg.com/vi/{video_id}/hq720.jpg"    #下载视频封面
    client = httpx.AsyncClient(headers=get_headers(),proxies=proxies,timeout=100)
    response = await client.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    imgurl =await file_chain(path)
    return imgurl

async def file_chain(path):     ##上传文件到ffsup.com并取得直链

    url = 'https://upload.ffsup.com/'
    with open(path, 'rb') as f:
        files = {'file': f}
        response = await client.post(url=url, files=files)
    return response.json()['data']['url']
