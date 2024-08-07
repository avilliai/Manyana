from mirai import Image
from mirai import GroupMessage

from plugins.youtube0 import get_video,get_audio,get_img

def main(bot,logger,proxy):
    proxies = {
        'http://': proxy,
        'https://': proxy,
    }
    logger.info("Youtube功能已启动")

    @bot.on(GroupMessage)
    async def youtube_download(event: GroupMessage):
        if str(event.message_chain).startswith('youtube视频下载'):
            try:
                video_id = str(event.message_chain).replace("youtube视频下载","")
                logger.info(f"正在获取{video_id}的视频下载链接")
                await bot.send(event, "正在获取视频下载链接，请稍后……")

                video_url = await get_video(video_id,proxies)
                await bot.send(event, f"视频下载链接：{video_url}/n为防止失效，请尽快使用",True)
            except:
                logger.error("视频下载链接获取失败")
                await bot.send(event, "下载链接获取失败，请检查输入是否正确",True)
        elif str(event.message_chain).startswith('youtube音频下载'):
            try:
                video_id = str(event.message_chain).replace("youtube音频下载","")
                logger.info(f"正在获取{video_id}的音频下载链接")
                await bot.send(event, "正在获取音频下载链接，请稍后……")

                audio_url = await get_audio(video_id,proxies)
                await bot.send(event, f"音频下载链接：{audio_url}/n为防止失效，请尽快使用",True)
            except:
                logger.error("音频下载链接获取失败")
                await bot.send(event, "下载链接获取失败，请检查输入是否正确",True)
        elif str(event.message_chain).startswith('youtube封面下载'):
            try:
                video_id = str(event.message_chain).replace("youtube封面下载","")
                logger.info(f"正在获取{video_id}的封面下载链接")
                await bot.send(event, "正在获取封面下载链接，请稍后……")
                
                img_path = await get_img(video_id,proxies)
                await bot.send(event, [f"{video_id}的封面：",Image(path = img_path)],True)
            except:
                logger.error("封面下载链接获取失败")
                await bot.send(event, "封面下载失败，请检查输入是否正确",True)
