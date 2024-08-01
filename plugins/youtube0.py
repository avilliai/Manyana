import httpx
import random

from pytubefix import Channel, YouTube, Playlist, Stream

from plugins.newsEveryDay import get_headers

ASMR_channels = ['@emococh','@-gabisroom-4153']
pushed_videos = ['HG-U_0nazgc']
async def ASMR_today(proxies):
    global ASMR_channels     #ASMR频道列表
    global  pushed_videos    #已推送ASMR列表
    channel = random.choice(ASMR_channels)
    c = Channel(url=f'https://www.youtube.com/{channel}',proxies=proxies)
    athor = c.channel_name
    video_idlist=[]
    for url in c.video_urls[:10]:
        video_id=str(url).split('=')[1].replace('>', '')
        video_idlist.append(video_id)
    # video_idlist=list(set(video_idlist)-set(pushed_videos))    #该方法可以去除重复ASMR,但是会导致ASMR顺序不确定
    for pushed_video in pushed_videos:      #去除已推送ASMR
        if pushed_video in video_idlist:
            video_idlist.remove(pushed_video)
    print(c.video_urls[:10])
    print(video_idlist)
    try:
        video_id=video_idlist[0]    #获取一个最新的未推送ASMR 
    except:
        print(f"{athor}频道没有未推送的ASMR,从投稿中随机选择")    #如果没有未推送的ASMR,从该频道投稿中随机选择
        video_id=random.choice(c.video_urls).split('=')[1].replace('>', '')
    url='https://www.youtube.com/watch?v='+video_id
    yt = YouTube(url)
    title = yt.title
    length = yt.length
    pushed_videos.append(url)
    return athor,title,video_id,length

async def get_audio(video_id,proxies):
    url=f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url=url,proxies=proxies)
    title = yt.title

    url=f"https://ripyoutube.com/mates/en/convert?id={video_id}"    #从ripyoutube获取音频下载地址
    data ={
        'platform': 'youtube',
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'title': title,
        'id': video_id,
        'ext': 'mp3',
        'note': '128k',
        'format': ''
    }
    client = httpx.AsyncClient(headers=get_headers(),proxies=proxies,timeout=100)
    responese = client.post(url=url,data=data)
    audiourl = responese.json()['downloadUrlX']
    return audiourl

async def get_video(video_id,proxies):
    url=f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url=url,proxies=proxies)
    title = yt.title

    url=f"https://ripyoutube.com/mates/en/convert?id={video_id}"    #从ripyoutube获取视频下载地址
    data ={
        'platform': 'youtube',
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'title': title,
        'id': video_id,
        'ext': 'mp4',
        'note': '1080p',
        'format': 137
    }
    client = httpx.AsyncClient(headers=get_headers(),proxies=proxies,timeout=100)
    responese = client.post(url=url,data=data)
    videourl = responese.json()['downloadUrlX']
    return videourl

async def get_img(video_id,proxies):
    path =f"data/Youtube/{video_id}.jpg"
    url=f"https://i.ytimg.com/vi/{video_id}/hq720.jpg"    #下载视频封面
    client = httpx.AsyncClient(headers=get_headers(),proxies=proxies,timeout=100)
    response = client.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path
