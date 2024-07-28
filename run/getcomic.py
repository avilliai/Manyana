# -*- coding:utf-8 -*-
import random

import yaml
from mirai import GroupMessage,MessageChain,Image,FriendMessage
import os
import shutil
import random
import jmcomic
from mirai.models import ForwardMessageNode, Forward
from functools import partial

class MyDownloader(jmcomic.JmDownloader):
    start = 0
    end = 0
    def do_filter(self, detail,start=start,end=end):
        start = self.start
        end = self.end
        if detail.is_photo():
            photo: jmcomic.JmPhotoDetail = detail
            # 支持[start,end,step]
            return photo[start:end]

        return detail

def main(bot, logger):
    @bot.on(GroupMessage)
    async def querycomic(event: GroupMessage):
        if str(event.message_chain).startswith("来点好康的#"):
            querycomic = str(event.message_chain).split("#")[1]
            client = jmcomic.JmOption.default().new_jm_client()
            # 分页查询，search_site就是禁漫网页上的【站内搜索】
            try:
                page: jmcomic.JmSearchPage = client.search_site(search_query=querycomic, page=1)
                # page默认的迭代方式是page.iter_id_title()，每次迭代返回 albun_id, title
                # album_id, title = next(page.iter_id_title())
                comics_id = []
                comics_title = []
                for album_id, title in page:
                    comics_id.append(album_id)
                    comics_title.append(title)
                random_id = comics_id[int(random.randint(1,len(comics_id)))]
                random_title = comics_title[int(random.randint(1,len(comics_id)))]
            except Exception as e:
                logger.error(e)
                logger.exception("详细错误如下：")
            if len(comics_id) == 0:
                await bot.send(event,"没有找到捏,你的xp很奇怪")
            else:
                cmList=[]
                node = ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain("id号:"+random_id))
                cmList.append(node)
                node = ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain("本子标题:"+random_title))
                cmList.append(node)
                node = ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain("已为主人挑选好这部本子，主人可以输入\n[下载本子#[开始页数-最后页数](最多5张)+ # + id号]查看本子喵~\n例如:下载本子#1-5#114514"))
                cmList.append(node)
                await bot.send(event, Forward(node_list=cmList))

    @bot.on(GroupMessage)
    async def download(event: GroupMessage):
        if str(event.message_chain).startswith("下载本子#"):
            comic_id = str(event.message_chain).split("#")[2]
            range_str = str(event.message_chain).split("#")[1]
            start_str, end_str = range_str.split('-')
            start = int(start_str)-1  
            end = int(end_str)      
            range_int = end - start
            if(range_int>5):
                await bot.send(event,"页数太多")
            else:
                option = jmcomic.create_option_by_file('run/option.yml')
                directories = ['run/download/']
                for directory in directories:
                    if os.path.exists(directory):
                        try:
                            shutil.rmtree(directory)
                        except Exception as e:
                               logger.error(f"Error removing {directory}: {e}")
                    else:
                        logger.info(f"Directory {directory} does not exist. Skipping.")

                MyDownloader.start = start
                MyDownloader.end = end
                jmcomic.JmModuleConfig.CLASS_DOWNLOADER = MyDownloader
                await bot.send(event,"下载中...")
                try:
                    jmcomic.download_album(comic_id, option)
                except Exception as e:
                    logger.exception("获取失败，错误如下：")
                    await bot.send(event,"下载失败")
                folder_path = 'run/download/'

                file_names = os.listdir(folder_path)

                png_files = [os.path.join(folder_path, file) for file in file_names if file.lower().endswith('.png')]
                image_array = []
                logger.info(png_files)
                for path in png_files[::-1]:
                    logger.warning(path)
                    image_array.append(Image(path=path))
                cmList=[]
                node = ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain(image_array))
                cmList.append(node)
                node = ForwardMessageNode(sender_id=bot.qq, sender_name="ninethnine",message_chain=MessageChain("可能显示不出来"))
                cmList.append(node)
                await bot.send(event, Forward(node_list=cmList))


   
