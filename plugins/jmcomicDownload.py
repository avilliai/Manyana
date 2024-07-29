import random
import shutil

import jmcomic
from jmcomic import *

from plugins.RandomStr import random_str


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

def queryJM(name,num=4):
    client = jmcomic.JmOption.default().new_jm_client()
    page: jmcomic.JmSearchPage = client.search_site(search_query=name, page=1)
    results=[]
    fal=0
    for i in page.content:
        if fal>10:
            raise Exception
            break
        try:
            file = downloadComic(i[0], start=1, end=2)
            print([f"车牌号：{i[0]} \n name：{i[1]['name']}\nauthor：{i[1]['author']}",file])
            results.append([f"车牌号：{i[0]} \n name：{i[1]['name']}\nauthor：{i[1]['author']}",file])
            if len(results) > num:
                return results
        except Exception as e:
            print(e)
            continue
            fal+=1
def downloadComic(comic_id,start=1,end=5):
    option = jmcomic.create_option_by_file('config/jmcomic.yml')
    if not os.path.exists('data/pictures/benzi'):
        os.mkdir('data/pictures/benzi')
    directories = ['data/pictures/benzi']
    for directory in directories:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
            except Exception as e:
                print(f"Error removing {directory}: {e}")
        else:
            print(f"Directory {directory} does not exist. Skipping.")

    MyDownloader.start = start
    MyDownloader.end = end
    MyDownloader.onlyFirstPhoto = False
    jmcomic.JmModuleConfig.CLASS_DOWNLOADER = MyDownloader


    jmcomic.download_album(comic_id, option)

    folder_path = 'data/pictures/benzi'
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    file_names = os.listdir(folder_path)
    #print(file_names)
    image_raw = Image.open("data/pictures/benzi/"+file_names[0])
    # convert image to black and white
    image_black_white = image_raw.convert('1')
    newPath=f"data/pictures/cache/{random_str()}.png"
    image_black_white.save(newPath)

    #png_files = [os.path.join(folder_path, file) for file in file_names if file.lower().endswith('.png')]
    return newPath

#queryJM("碧蓝档案")
