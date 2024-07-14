# -*- coding:utf-8 -*-
# -*- coding: utf-8 -*-
import asyncio
import os.path
import random
from io import BytesIO

import httpx
import yaml
from PIL import Image

from plugins.RandomStr import random_str


async def bbbgacha(bbb):
    character = []
    pool = {'3': ['白子', '星野', '阿露', '伊织', '日奈', '泉', '晴奈', '日富美', '鹤城', '花凛', '尼禄', '真纪', '响',
                  '菫', '纱绫', '瞬', '艾米', '真白', '泉奈', '爱丽丝', '绿', '切里诺', '柚子', '梓', '小春',
                  '梓（泳装）', '真白（泳装）', '日富美（泳装）', '日奈（泳装）', '伊织（泳装）', '白子（骑行）', '瞬（幼女）',
                  '纱绫（私服）', '尼禄（兔女郎）', '花凛（兔女郎）', '明日奈（兔女郎）', '夏', '初音未来（联动）', '亚子',
                  '切里诺（温泉）', '千夏（温泉）', '和香（温泉）', '阿露（正月）', '睦月（正月）', '芹香（正月）', '若藻', '濑名',
                  '千寻', '三森', '日向', '玛丽娜', '咲', '宫子', '美游', '枫', '伊吕波', '月咏', '美咲', '日和',
                  '亚津子', '野宫（泳装）', '若藻（泳装）', '星野（泳装）', '泉奈（泳装）', '千世（泳装）', '纱织', '萌绘',
                  '和纱', '心奈', '歌原（应援团）', '诺亚', '朱音（兔女郎）', '优香（体操服）', '玛丽（体操服）', '日鞠',
                  '时雨', '芹娜（圣诞）', '花绘（圣诞）', '晴奈（正月）', '枫香（正月）', '美祢', '未花', '惠', '康娜', '樱子',
                  '时', '渚', '忧', '小雪', '佳代子（正月）', '遥香（正月）', '果穗', '时（兔女郎）', '爱丽丝（女仆）', '玲纱',
                  '瑠美', '南', '实梨', '宫子（泳装）', '咲（泳装）', '白子（泳装）', '日向（泳装）', '忧（泳装）', '花子（泳装）',
                  '三森（泳装）', '梅露', '柯托莉（应援团）', '晴奈（体操服）', '霞', '一花', '时雨（温泉）', '御坂美琴',
                  '食蜂操祈', '缘里', '莲华', '桔梗', '艾米（泳装）'],
            '2': ['芹香', '绫音', '佳代子', '淳子', '明里', '枫香', '爱莉', '莲见', '朱音', '晴', '歌原', '优香', '椿',
                  '千世', '桃井', '野宫', '花绘', '静子', '花子', '桐乃', '玛丽', '睦月', '红叶'],
            '1': ['千夏', '好美', '芹娜', '明日奈', '柯托莉', '菲娜', '鹤城（泳装）', '吹雪', '满', '绫音（泳装）', '巴',
                  '静子（泳装）', '和香', '遥香', '泉（泳装）', '朱莉', '志美子', '铃美', '小玉', '响（应援团）',
                  '莲见（体操服）', '淳子（正月）', '柚子（女仆）', '美游（泳装）', '小春（泳装）', '佐天泪子']}
    while len(character) < 10:
        po = pool.get('2')
        cha = random.choice(po)
        # print(cha)
        character.append(cha)
        if random.randint(1, 101) < bbb.get("3star"):
            if random.randint(1, 101) < bbb.get("3up"):
                cha = bbb.get("3starUp")
            else:
                po = pool.get('3')
                cha = random.choice(po)
            #print(cha)
            character.append(cha)
        if random.randint(1, 101) < bbb.get("2star"):
            if random.randint(1, 101) < bbb.get("2up"):
                cha = bbb.get("2starUp")
            else:
                po = pool.get('2')
                cha = random.choice(po)
            #print(cha)
            character.append(cha)
        if random.randint(1, 101) < 100 - bbb.get("3star") - bbb.get("2star"):
            po = pool.get('1')
            cha = random.choice(po)
            #print(cha)
            character.append(cha)

    #print(character)
    a = 60
    b = 250
    count = 0
    st = Image.open('data/blueArchive/back.png')

    for i in character:
        # 剪切图像
        '''if count>0:
            st=Image.open('pictures\\imgs.png')'''
        st2 = Image.open("data/blueArchive/gacha/" + i + ".png")
        st2 = st2.resize((int(404 * 0.6), int(456 * 0.6)))

        mark = st2
        layer = Image.new('RGBA', st.size, (0, 0, 0, 0))
        #print(str(a)+'------'+str(b))
        layer.paste(mark, (a, b))
        a += 311
        count += 1
        if count == 5:
            b += 400
            a = 45
        st = Image.composite(layer, st, layer)
    pa = 'data/blueArchive/cache/' + random_str() + '.png'
    st.save(pa)
    return pa


def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers


async def arkGacha():
    headers = get_headers()
    url = "http://api.elapsetower.com/arknightsdraw"

    path = "data/pictures/cache/" + random_str() + ".png"
    #path="moyu.png"
    #print(path)
    if os.path.exists(path):
        return path
    else:
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            #print(path)
            return path


async def starRailGacha():
    with open('data/GachaData/StarRail.yaml', 'r', encoding='utf-8') as file:
        students = yaml.load(file, Loader=yaml.FullLoader)

    i = 0
    character = []

    while i < 10:
        if i == 0:
            ass = random.randint(1, 150)
            if ass < 75:
                cha = random.choice(list(students.get("四星角色").keys()))
            else:
                cha = random.choice(list(students.get("四星光锥").keys()))
            character.append(cha)
        else:
            ass = random.randint(1, 150)
            if ass < 4:
                if ass < 2:
                    cha = random.choice(list(students.get("五星角色").keys()))
                else:
                    cha = random.choice(list(students.get("五星光锥").keys()))
                # print(cha)
                character.append(cha)
            if 3 < ass < 40:
                if ass < 20:
                    cha = random.choice(list(students.get("四星角色").keys()))
                else:
                    cha = random.choice(list(students.get("四星光锥").keys()))
                character.append(cha)
            if ass > 39:
                cha = random.choice(list(students.get("三星光锥").keys()))
                # print(cha)
                character.append(cha)
        i += 1

    # print(character)
    a = 193
    b = 221
    count = 0
    st = Image.open('data/GachaData/StarRail/bg.png')
    path = "data/pictures/cache/" + random_str() + '.png'
    for i in character:
        # 剪切图像
        # 发起超级融合

        st2 = Image.open("data/GachaData/StarRail/" + i + ".png")

        im = st
        mark = st2
        layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
        # print(str(a)+'------'+str(b))
        layer.paste(mark, (a, b))
        a += 473
        count += 1
        if count == 5:
            b += 689
            a = 193
        out = Image.composite(layer, im, layer)
        st = out
    #st.show()
    st.save(path)
    #print(path)
    return path


if __name__ == '__main__':
    #asyncio.run(arkGacha())
    asyncio.run(starRailGacha())
