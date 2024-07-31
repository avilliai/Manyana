import copy
import os.path
import shutil

import jmcomic
import yaml
from jmcomic import *

from plugins.RandomStr import random_str
from plugins.tookits import fileToUrl, lanzouFileToUrl


class MyDownloader(jmcomic.JmDownloader):
    start = 0
    end = 0
    onlyFirstPhoto = False
    def do_filter(self, detail,start=start,end=end):
        start = self.start
        end = self.end
        if detail.is_album() and self.onlyFirstPhoto:
            album: jmcomic.JmAlbumDetail = detail
            return [album[0]]
        if(detail.is_photo()):
            photo: jmcomic.JmPhotoDetail = detail
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

def downloadComic(comic_id,start=1,end=5):
    with open("config/jmcomic.yml", 'r', encoding='utf-8') as f: #不知道他这个options咋传的，我就修改配置文件得了。
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    result["dir_rule"]["base_dir"]=f"data/pictures/benzi/temp{comic_id}"
    with open("config/jmcomic.yml", 'w', encoding="utf-8") as file:
        yaml.dump(result, file, allow_unicode=True)
    option = jmcomic.create_option_by_file('config/jmcomic.yml')
    if not os.path.exists(f'data/pictures/benzi/temp{comic_id}'):
        os.mkdir(f'data/pictures/benzi/temp{comic_id}')


    MyDownloader.start = start
    MyDownloader.end = end
    MyDownloader.onlyFirstPhoto = False
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
def downloadALLAndToPdf(comic_id,savePath):
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
    # 使用option对象来下载本子
    jmcomic.download_album(comic_id, option)
    r=lanzouFileToUrl(f"{savePath}/{comic_id}.pdf")
    #r=fileToUrl(f"{savePath}/{comic_id}.pdf",proxy)
    return r

