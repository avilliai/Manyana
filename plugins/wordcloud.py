# -*- coding:utf-8 -*-
from concurrent.futures import ProcessPoolExecutor
import asyncio
import jieba
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
import numpy as np
from collections import Counter
import os
import datetime
from plugins.toolkits import random_str, newLogger


def create_chinese_wordcloud(text, save_path="./test.png"):
    mask_path = "data/fonts/wordcloud.jpg"
    font_path = "data/fonts/H-TTF-BuMing-B-2.ttf"
    background_color = "white"
    max_words = 200
    colormap = "viridis"
    mask = np.array(Image.open(mask_path))
    img_width, img_height = mask.shape[1], mask.shape[0]
    max_font_size = img_height // 20
    words = jieba.lcut(text)
    stopwords = ["的", "是", "在", "了", "和", "就", "都", "而", "与", "着", "得", "地", "也", "或", "者", "一个", "一种", "这", "那", "这些", "那些"]
    word_list = [word for word in words if word not in stopwords]
    word_counts = Counter(word_list)

    # 如果词总数少于100，则重复单词
    if len(word_counts) < 100:
        repeated_words = []
        while len(repeated_words) < 100:
            for word, count in word_counts.items():
                repeated_words.extend([word] * count)
                if len(repeated_words) >= 100:
                    break
        word_list = repeated_words

    text = ' '.join(word_list)

    wc = WordCloud(
        background_color=background_color,
        max_words=max_words,
        mask=mask,
        font_path=font_path,
        colormap=colormap,
        stopwords=STOPWORDS,
        scale=3,
        width=img_width,
        height=img_height,
        max_font_size=max_font_size,
        collocations=False
    )

    wc.generate(text)
    image_colors = ImageColorGenerator(mask)
    wc.recolor(color_func=image_colors)
    wc.to_file(save_path)
async def create_chinese_wordcloud_async(text,save_path):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        await loop.run_in_executor(
            pool,
            create_chinese_wordcloud,
            text,
            save_path,
        )
async def appendData(tempData):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        await loop.run_in_executor(
            pool,
            record_user_input,
            tempData
        )
logger=newLogger()
def record_user_input(tempData):
    for i in tempData:
        text=str(tempData[i])
        groupid=i.split("/")[0]
        userid=i.split("/")[1]
        if not os.path.exists(f"data/text/wordcloudData/{groupid}/{datetime.date.today().strftime('%Y-%m-%d')}"):
            os.makedirs(f"data/text/wordcloudData/{groupid}/{datetime.date.today().strftime('%Y-%m-%d')}", exist_ok=True) #创建目录
        file_path =f"data/text/wordcloudData/{groupid}/{datetime.date.today().strftime('%Y-%m-%d')}/{userid}.txt"
        if not os.path.exists(file_path):
            open(file_path, 'w').close()
        with open(file_path, 'a', encoding='utf-8') as f:
            try:
                f.write(text + '\n')
            except Exception as e:
                logger.error(e)
async def getMyAllText(group_path, user_id):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool,
            find_and_read_user_files, 
            group_path,
            user_id
        )
    return result

async def getgroupText(group_id, type):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool,
            getGroupTextrea, 
            group_id,
            type
        )
    return result
logger=newLogger()
def getGroupTextrea(groupid,type="all"):
    if type=="today":
        text = ""
        for i in os.listdir(f"data/text/wordcloudData/{groupid}/{datetime.date.today().strftime('%Y-%m-%d')}"):
            try:
                with open(f"data/text/wordcloudData/{groupid}/{datetime.date.today().strftime('%Y-%m-%d')}/{i}",
                          'r', encoding='utf-8') as f:
                    content = f.read()
                    text += content
            except:
                logger.info(
                    f"读取data/text/wordcloudData/{groupid}/{datetime.date.today().strftime('%Y-%m-%d')}/{i} 失败，无法使用的坏文件")
    elif type=="all":
        text = ""
        for date1 in os.listdir(f"data/text/wordcloudData/{groupid}"):
            for i in os.listdir(f"data/text/wordcloudData/{groupid}/{date1}"):
                try:
                    with open(f"data/text/wordcloudData/{groupid}/{date1}/{i}", 'r', encoding='utf-8') as f:
                        content = f.read()
                        text += content
                except:
                    logger.info(
                        f"读取data/text/wordcloudData/{groupid}/{date1}/{i} 失败，无法使用的坏文件")
    return text
def find_and_read_user_files(group_path, user_id):
    user_data =""
    if os.path.isdir(group_path):
        for date_str in os.listdir(group_path):
            date_path = os.path.join(group_path, date_str)
            if os.path.isdir(date_path):
                user_file = os.path.join(date_path, f"{user_id}.txt")
                if os.path.exists(user_file):
                    with open(user_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        user_data+=content
    return user_data
def findAllUserSaid(groupid,target):
    user_files_content = find_and_read_user_files(f"data/text/wordcloudData/{groupid}", target)
    return user_files_content
if __name__ == '__main__':
    text = "Python 是一种流行的编程语言。 Python 广泛用于 Web 开发、数据科学、机器学习等领域。文学研究在学术界处于危机之中。英语专业的学生正在减少，随着教授退休，终身职位正在被取消，整个系都落在了管理者的斧头之下。更紧迫的是，世界正处于火海之中，年轻一代比他们的父母更糟糕，各种国内和国际冲突有可能演变成更大的暴力。那么，当文学研究在大学里消失，各种危机——生态、经济、政治——在没有文学研究的情况下复合在一起时，文学理论的意义何在？在无所不在的危机的火焰的映衬下，安娜·科恩布鲁的《即时性，或太晚资本主义的风格》和丹尼尔·赖特的《小说的基础》对这个问题提供了两个答案。对他们来说，文学理论可以是先锋的，也可以是抒情的，它可以是一种从世界上退一步的工具，也可以是一种更充分地栖居于其中的工具。即使危机成倍增加，他们也断言理论仍然是有价值的。科恩布鲁的理论几乎是一种武器：一种切断文化和社会经济“即时性”的紧密网络的手段，这种网络随时都可能吞噬我们每个人。对她来说，理论对于创造距离至关重要，它为我们提供了观察、抽象思考和想象一个与这个世界不同的世界所必需的呼吸空间。这一点现在尤为重要，因为根据科恩布鲁的说法，我们周围普遍存在的即时性文化坚持其“现实性”，即使它根本不是这样。相比之下，赖特的理论就像一个滑梯：一个光滑的表面，旨在引导你深入到我们世界的基本特征以及我们在其中构建的文化对象的基石。对他来说，理论对于揭示那些被感知但未被表达出来的基础，并使其可见，至关重要。它让我们能够抛弃错误的二元对立，认识到社会世界的根本多元性，也许，正如他挑衅性地指出的那样，也认识到我们脚下的大地的根本多元性。从这个意义上说，科恩布鲁和赖特是截然相反的，他们对理论的目的提供了相互竞争、相互排斥的理解。但他们共同拥有的——我也是——是对理论本身的信念。如果说对文学理论这种深奥的东西的信念似乎很荒谬，那么就考虑一种更熟悉的人类知识工具：小说。作为一种形式，“小说”有能力同时在两个层面上运作，既代表社会世界的广度，也代表个人生活的复杂细节。没有理由认为，从总体上看，理论不能或不应该做同样的事情，为我们提供描述文化系统的抽象运作和日常经验的具体基础的语言。鉴于我们面前的危机的范围，我们将需要各种各样的理论来找到前进的道路。在早先一场危机，即 2008 年金融危机的紧要关头，扎迪·史密斯在《纽约书评》上发表了一篇题为《小说的两条道路》的文章。她当时正在评论两部小说——约瑟夫·奥尼尔的《荷兰》和汤姆·麦卡锡的《余数》——她认为这两部小说代表了当代文学中两种相互关联但又截然不同的趋势：分别是“抒情现实主义”和“先锋派”。《荷兰》的抒情现实主义使其置身于一种悠久的小说传统之中，这种传统的基本假设是“语言具有揭示真相的神奇力量”，“自我是一个无底洞”。深入到人物的生活和内心世界，发现日常细节中的美，这种风格的小说家断言，日常生活的美学化呈现是他们的首要任务。但在史密斯看来，新千年的接踵而至的危机——从互联网泡沫破裂到气候灾难再到经济大萧条——威胁到了中产阶级生存的安全性（这也就是抒情现实主义者所说的“日常生活”的意思），并由此催生了一种文学上的挑战者。抒情现实主义陶醉于经验的重要模糊性，而“先锋派”小说则对其主题采取了一种更加冷静、疏离的视角。《余数》“完全掏空了内在性”，使日常生活及其在小说中的表现形式都变得陌生化；它的运作方式是识别读者的预期，然后“兴高采烈地将其一块块地拆解”。1抒情现实主义和先锋派在史密斯看来是新小说可以遵循的两条潜在道路，她希望其中一条道路能够将文学从 2008 年的废墟中拉出来，进入到新的领域。这些相同的类别为我们提供了一个有用的框架，可以用来阐释《即时性》和《小说的基础》的不同方法，并理解它们各自与我们这个危机时刻的关系。"
    save_path=f"data/pictures/cache/{random_str()}.png"
    print(save_path)
    asyncio.run(create_chinese_wordcloud_async(text,save_path))
