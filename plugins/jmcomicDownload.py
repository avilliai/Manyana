# -*- coding:utf-8 -*-
import os.path
import shutil

import jmcomic
import yaml
from jmcomic import *

from plugins.toolkits import fileToUrl, lanzouFileToUrl, random_str


class MyDownloader(jmcomic.JmDownloader):
    start = 0
    end = 0
    album_index = 1
    onlyFirstPhoto = False
    def do_filter(self, detail,start=start,end=end):
        start = self.start
        end = self.end
        if detail.is_album() and self.onlyFirstPhoto:
            album: jmcomic.JmAlbumDetail = detail
            if len(album)<self.album_index:
                self.album_index = len(album)-1
            if self.album_index<1:
                self.album_index = 1
            return [album[self.album_index-1]]
        if detail.is_photo():
            photo: jmcomic.JmPhotoDetail = detail
            print(len(photo))
            if end>len(photo):
                end = len(photo)
            if start>len(photo):
                start = len(photo)
            if start == end:
                start = 0
                end = len(photo)
            return photo[start:end]
        return detail

def queryJM(name,num=3):
    client = jmcomic.JmOption.default().new_jm_client()
    page: jmcomic.JmSearchPage = client.search_site(search_query=name, page=1)
    results=[]
    for i in page.content:
        file = downloadComic(i[0], start=1, end=2)
        print([f"车牌号：{i[0]} \n name：{i[1]['name']}\nauthor：{i[1]['author']}",file[0]])
        results.append([f"车牌号：{i[0]} \n name：{i[1]['name']}\nauthor：{i[1]['author']} \n部分预览图：",file[0]])
        if len(results) > num:
            return results
        print(results)
        
def JM_search(name):
    client = JmOption.default().new_jm_client()

    # 分页查询，search_site就是禁漫网页上的【站内搜索】
    page: JmSearchPage = client.search_site(search_query=f'{name}', page=1)
    # page默认的迭代方式是page.iter_id_title()，每次迭代返回 albun_id, title
    result=''
    number=0
    for album_id, title in page:
        #print(f'[{album_id}]: {title}')
        result += f'[{album_id}]: {title}\n'
        number+=1
        if number==30:break
    return result

def JM_search_week():
    op = JmOption.default()
    cl = op.new_jm_client()
    page: JmCategoryPage = cl.week_ranking(1)
    result=''
    for page in cl.categories_filter_gen(page=1, # 起始页码
                                         # 下面是分类参数
                                         time=JmMagicConstants.TIME_WEEK,
                                         category=JmMagicConstants.CATEGORY_ALL,
                                         order_by=JmMagicConstants.ORDER_BY_VIEW,
                                         ):
        number=0
        for aid, atitle in page:
            result += f'[{aid}]: {atitle}\n'
            #print(aid, atitle)
            number+=1
            if number==20:break
        break
    return result
    
def JM_search_comic_id():
    op = JmOption.default()
    cl = op.new_jm_client()
    page: JmCategoryPage = cl.week_ranking(1)
    for page in cl.categories_filter_gen(page=1, # 起始页码
                                         # 下面是分类参数
                                         time=JmMagicConstants.TIME_MONTH,
                                         category=JmMagicConstants.CATEGORY_ALL,
                                         order_by=JmMagicConstants.ORDER_BY_VIEW,
                                         ):
        for aid, atitle in page:
            yield aid
        #print(result)
    
def downloadComic(comic_id,start=1,end=5):
    with open("config/jmcomic.yml", 'r', encoding='utf-8') as f: #不知道他这个options咋传的，我就修改配置文件得了。
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    result["dir_rule"]["base_dir"]=f"data/pictures/benzi/temp{comic_id}"
    #临时修改
    with open("config/jmcomic.yml", 'w', encoding="utf-8") as file:
        yaml.dump(result, file, allow_unicode=True)
    option = jmcomic.create_option_by_file('config/jmcomic.yml')
    if not os.path.exists(f'data/pictures/benzi/temp{comic_id}'):
        os.mkdir(f'data/pictures/benzi/temp{comic_id}')


    MyDownloader.start = start
    MyDownloader.end = end
    MyDownloader.onlyFirstPhoto = True
    jmcomic.JmModuleConfig.CLASS_DOWNLOADER = MyDownloader


    jmcomic.download_album(comic_id, option)

    folder_path = f'data/pictures/benzi/temp{comic_id}'
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    file_names = os.listdir(folder_path)
    print(file_names)
    new_files = []
    for i in file_names:
        #print(file_names)
        image_raw = Image.open(f"data/pictures/benzi/temp{comic_id}/"+i)
        # convert image to black and white
        image_black_white = image_raw.convert('1')
        newPath=f"data/pictures/cache/{random_str()}.png"
        new_files.append(newPath)
        image_black_white.save(newPath)
    #png_files = [os.path.join(folder_path, file) for file in file_names if file.lower().endswith('.png')]
    return new_files
def downloadALLAndToPdf(comic_id,savePath,URLSource=0,proxy=""):
    with open("config/jmcomic.yml", 'r', encoding='utf-8') as f: #不知道他这个options咋传的，我就修改配置文件得了。
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    tempResult = copy.deepcopy(result)
    tempResult["dir_rule"]["base_dir"]=f"{savePath}/{comic_id}"
    
    if os.path.exists(f"{savePath}/{comic_id}"):
        shutil.rmtree(f"{savePath}/{comic_id}")
    if "plugins" not in tempResult:
        tempResult["plugins"]={}
    if "after_photo" not in tempResult["plugins"]:
        tempResult["plugins"]["after_photo"]=[]
    tempResult["plugins"]["after_photo"].append({"plugin": "img2pdf","kwargs":{"filename_rule":"Pid","pdf_dir":savePath}})
    with open("config/jmcomic.yml", 'w', encoding="utf-8") as file:
        yaml.dump(tempResult, file, allow_unicode=True)
    # 创建配置对象
    option = jmcomic.create_option_by_file('config/jmcomic.yml')
    with open("config/jmcomic.yml", 'w', encoding="utf-8") as file:
        yaml.dump(result, file, allow_unicode=True)
    #这里需要再设置一下类变量，不然本子下载不全
    MyDownloader.start = 0
    MyDownloader.end =0
    MyDownloader.onlyFirstPhoto = True
    jmcomic.JmModuleConfig.CLASS_DOWNLOADER = MyDownloader
    # 使用option对象来下载本子
    jmcomic.download_album(comic_id, option)
    if URLSource==0:
        r=lanzouFileToUrl(f"{savePath}/{comic_id}.pdf")
    elif URLSource==1:
        r=fileToUrl(f"{savePath}/{comic_id}.pdf",proxy)
    else:
        return False
    return r

