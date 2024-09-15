# -*- coding: utf-8 -*-
import json
import random
from bs4 import BeautifulSoup as bs
import httpx
import os
from io import BytesIO
import urllib
import re
from PIL import Image
from emoji import is_emoji
import asyncio
from bs4 import BeautifulSoup  # 用于解析 HTML
from plugins.toolkits import random_str, get_headers

ark = {
    "方舟种族": [
        "阿达克利斯", "阿达克利斯", "阿达克利斯", "阿达克利斯", "阿戈尔", "阿戈尔", "阿戈尔", "阿戈尔", "阿纳萨",
        "阿纳萨", "阿纳萨", "阿纳缇", "阿纳缇", "阿斯兰", "阿斯兰", "埃拉菲亚", "埃拉菲亚", "埃拉菲亚", "埃拉菲亚",
        "安努拉", "安努拉", "德拉克", "德拉克", "杜林", "杜林", "杜林", "杜林", "菲林", "菲林", "菲林", "菲林", "菲林",
        "菲林", "斐迪亚", "斐迪亚", "斐迪亚", "斐迪亚", "丰蹄", "丰蹄", "丰蹄", "丰蹄", "丰蹄", "鬼", "鬼", "鬼", "鬼",
        "鬼", "精灵", "卡普里尼", "卡普里尼", "卡普里尼", "卡普里尼", "卡普里尼", "卡特斯", "卡特斯", "卡特斯",
        "卡特斯", "卡特斯", "库兰塔", "库兰塔", "库兰塔", "库兰塔", "库兰塔", "黎博利", "黎博利", "黎博利", "黎博利",
        "黎博利", "黎博利", "龙", "龙", "鲁珀", "鲁珀", "鲁珀", "鲁珀", "曼提柯", "佩洛", "佩洛", "佩洛", "佩洛",
        "佩洛", "皮洛萨", "皮洛萨", "匹特拉姆", "匹特拉姆", "奇美拉", "麒麟", "瑞柏巴", "瑞柏巴", "瑞柏巴", "萨弗拉",
        "萨弗拉", "萨弗拉", "萨卡兹", "萨卡兹", "萨卡兹", "萨卡兹", "萨科塔", "萨科塔", "萨科塔", "萨科塔", "塞拉托",
        "塞拉托", "瓦伊凡", "瓦伊凡", "瓦伊凡", "瓦伊凡", "未公开（“巨兽”）", "未公开（“神”）", "未公开（海嗣）",
        "未知（人类）", "沃尔珀", "沃尔珀", "沃尔珀", "沃尔珀", "沃尔珀", "乌萨斯", "乌萨斯", "乌萨斯", "乌萨斯",
        "依特拉", "依特拉", "札拉克", "札拉克", "札拉克", "札拉克", "未知"
    ],

    "方舟地区": [
        "阿戈尔", "玻利瓦尔", "东", "哥伦比亚", "卡西米尔", "卡兹戴尔", "拉特兰", "莱塔尼亚", "雷姆必拓", "龙门",
        "米诺斯", "萨尔贡", "萨米", "维多利亚", "乌萨斯", "谢拉格", "叙拉古", "炎", "伊比利亚", "未公开"
    ],

    "方舟职业": [
        "狙击-{}",
        "术师-{}",
        "医疗-{}",
        "辅助-{}",
        "先锋-{}",
        "近卫-{}",
        "重装-{}",
        "特种-{}"
    ],

    "狙击分支": [
        "速射手\n【特性】优先攻击空中单位",
        "投掷手\n【特性】攻击对小范围的地面敌人造成两次物理伤害（第二次为余震，伤害降低至攻击力的一半）",
        "炮手\n【特性】攻击造成群体物理伤害",
        "攻城手\n【特性】优先攻击重量最重的单位",
        "神射手\n【特性】优先攻击攻击范围内防御力最低的敌方单位",
        "重射手\n【特性】高精度的近距离射击",
        "散射手\n【特性】攻击范围内的所有敌人，对自己前方一横排的敌人攻击力提升至150%"
    ],

    "术师分支": [
        "中坚术师\n【特性】攻击造成法术伤害",
        "扩散术师\n【特性】攻击造成群体法术伤害",
        "轰击术师\n【特性】攻击造成超远距离的群体法术伤害",
        "阵法术师\n【特性】通常时不攻击且防御力和法术抗性大幅度提升，技能开启时攻击造成群体法术伤害",
        "秘术师\n【特性】攻击造成法术伤害，在找不到攻击目标时可以将攻击能量储存起来之后一齐发射（最多3个）",
        "链术师\n【特性】攻击造成法术伤害，且会在4个敌人间跳跃，每次跳跃伤害降低15%并造成短暂停顿",
        "驭械术师\n【特性】操作浮游单元造成法术伤害\n单元攻击同一敌人伤害提升（最高造成干员110%攻击力的伤害）"
    ],

    "近卫分支": [
        "剑豪\n【特性】普通攻击连续造成两次伤害",
        "强攻手\n【特性】同时攻击阻挡的所有敌人",
        "无畏者\n【特性】能够阻挡一个敌人",
        "术战者\n【特性】攻击造成法术伤害",
        "领主\n【特性】可以进行远程攻击，但此时攻击力降低至80%",
        "斗士\n【特性】能够阻挡一个敌人",
        "武者\n【特性】不成为其他角色的治疗目标，每次攻击到敌人后回复自身70生命",
        "解放者\n【特性】通常不攻击且阻挡数为0，技能未开启时40秒内攻击力逐渐提升至最高+200%且技能结束时重置攻击力",
        "收割者\n【特性】无法被友方角色治疗，攻击造成群体伤害，每攻击到一个敌人回复自身50生命，最大生效数等于阻挡数",
        "重剑手\n【特性】同时攻击阻挡的所有敌人",
        "教官\n【特性】可以攻击到较远敌人，攻击自身未阻挡的敌人时攻击力提升至120%"
    ],

    "重装分支": [
        "铁卫\n【特性】能够阻挡三个敌人",
        "哨戒铁卫\n【特性】能够阻挡三个敌人，可以进行远程攻击",
        "驭法铁卫\n【特性】技能开启时普通攻击会造成法术伤害",
        "不屈者\n【特性】无法被友方角色治疗",
        "决战者\n【特性】只有阻挡敌人时才能够回复技力",
        "守护者\n【特性】技能可以治疗友方单位",
        "要塞\n【特性】不阻挡敌人时优先远程群体物理攻击"
    ],

    "医疗分支": [
        "医师\n【特性】恢复友方单位生命",
        "咒愈师\n【特性】攻击造成法术伤害，攻击敌人时为攻击范围内一名友方干员治疗相当于50%伤害的生命值",
        "群愈师\n【特性】同时恢复三个友方单位的生命",
        "链愈师\n【特性】恢复友方单位生命，且会在3个友方单位间跳跃，每次跳跃治疗量降低25%",
        "疗养师\n【特性】拥有较大治疗范围，但在治疗较远目标时治疗量变为80%",
        "行医\n【特性】恢复友方单位生命，并回复相当于攻击力50%的元素损伤（可以回复未受伤友方单位的元素损伤）"
    ],

    "辅助分支": [
        "凝滞师\n【特性】攻击造成法术伤害，并对敌人造成短暂的停顿",
        "削弱者\n【特性】攻击造成法术伤害",
        "吟游者\n【特性】不攻击，持续恢复范围内所有友军生命（每秒相当于自身攻击力10%的生命），自身不受鼓舞影响",
        "工匠\n【特性】能够阻挡两个敌人，使用<支援装置>协助作战",
        "召唤师\n【特性】攻击造成法术伤害\n可以使用召唤物协助作战",
        "护佑者\n【特性】攻击造成法术伤害，技能开启后改为治疗友方单位（治疗量相当于75%攻击力）"
    ],

    "特种分支": [
        "处决者\n【特性】再部署时间大幅度减少",
        "推击手\n【特性】同时攻击阻挡的所有敌人，可以放置于远程位",
        "钩索师\n【特性】技能可以使敌人产生位移，可以放置于远程位",
        "陷阱师\n【特性】可以使用陷阱来协助作战，但陷阱无法放置于敌人已在的格子中",
        "行商\n【特性】再部署时间减少，撤退时不返还部署费用，在场时每3秒消耗3点部署费用（不足时自动撤退）",
        "伏击客\n【特性】对攻击范围内所有敌人造成伤害\n拥有50%的物理和法术闪避且不容易成为敌人的攻击目标",
        "傀儡师\n【特性】受到致命伤时不撤退，切换成<替身>作战（替身阻挡数为0），持续20秒后自身再次替换<替身>",
        "怪杰\n【特性】自身生命会不断流失（每秒流失3%生命值）"
    ],
    "先锋分支": [
        "冲锋手\n【特性】击杀敌人后获得1点部署费用，撤退时返还初始部署费用",
        "尖兵\n【特性】能够阻挡两个敌人",
        "情报官\n【特性】再部署时间减少，可使用远程攻击",
        "战术家\n【特性】可以在攻击范围内选择一次战术点来召唤援军，自身攻击援军阻挡的敌人时攻击力提升至150%",
        "执旗手\n【特性】技能发动期间阻挡数变为0"
    ],

    "方舟稀有度": [
        "★",
        "★★",
        "★★",
        "★★★",
        "★★★",
        "★★★",
        "★★★★",
        "★★★★",
        "★★★★",
        "★★★★",
        "★★★★★",
        "★★★★★",
        "★★★★★",
        "★★★★★",
        "★★★★★",
        "★★★★★",
        "★★★★★★",
        "★★★★★★",
        "★★★★★★",
        "★★★★★★",
        "★★★★★★",
        "★★★★★★★"
    ],

    "_测试结果": [
        "缺陷",
        "普通",
        "普通",
        "普通",
        "标准",
        "标准",
        "标准",
        "优良",
        "优良",
        "优良",
        "卓越",
        "■■"
    ],

    "干员性别": [
        "男",
        "男",
        "男",
        "女",
        "女",
        "女",
        "未知"
    ],

    "感染情况": [
        "非感染者\n【体细胞与源石融合率】0%\n【血液源石结晶密度】0.0[1d9]u/L",
        "非感染者\n【体细胞与源石融合率】0%\n【血液源石结晶密度】0.0[1d9]u/L",
        "非感染者\n【体细胞与源石融合率】0%\n【血液源石结晶密度】0.[1d9+10]u/L",
        "非感染者\n【体细胞与源石融合率】0%\n【血液源石结晶密度】0.[1d9+10]u/L",
        "非感染者\n【体细胞与源石融合率】0%\n【血液源石结晶密度】0.00u/L",
        "感染者\n【体细胞与源石融合率】[1d10]%\n【血液源石结晶密度】0.[3d6+10]u/L",
        "感染者\n【体细胞与源石融合率】[1d10]%\n【血液源石结晶密度】0.[3d6+10]u/L",
        "感染者\n【体细胞与源石融合率】[3d6]%\n【血液源石结晶密度】0.[3d6+15]u/L",
        "感染者\n【体细胞与源石融合率】[3d6]%\n【血液源石结晶密度】0.[3d6+15]u/L",
        "感染者\n【体细胞与源石融合率】[1d5+15]%\n【血液源石结晶密度】0.[5d6+25]u/L",
        "未公开\n【体细胞与源石融合率】未公开\n【血液源石结晶密度】未公开"
    ],

    "综合体检测试": [
        "【物理强度】{}\n【战场机动】{}\n【生理耐受】{}\n【战术规划】{}\n【战斗技巧】{}\n【源石技艺适应性】{}"
    ],

    "战斗经验": ["没有战斗经验", "没有战斗经验", "没有战斗经验", "未知", "未公开", "_数字a年"],

    "_数字a": ["一", "两", "三", "四", "五", "六", "七", "八", "九"],

    "干员信息作成": [
        "为{nick}生成的干员信息如下：\n{%方舟稀有度}\n【性别】{%干员性别}\n【种族】{%方舟种族}\n【出身地】{%方舟地区}\n【战斗经验】{%战斗经验}\n【身高】[3d6*5+2d12+100]cm\n【感染情况】{%感染情况}\n—综合体检测试—\n{%综合体检测试}\n【职业】{%方舟职业}"
    ],

    "干员作成": [
        "为{nick}生成的干员信息如下：\n{%方舟稀有度}\n【性别】{%干员性别}\n【种族】{%方舟种族}\n【出身地】{%方舟地区}\n【战斗经验】{%战斗经验}\n【身高】[3d6*5+2d12+100]cm\n【职业】{%方舟职业}\n【感染情况】{%感染情况}\n—综合体检测试—\n{%综合体检测试}\n—技能—\n{%一套干员技能}"
    ]
}


def calc():
    infected = random.choice(ark.get("感染情况")).replace('[1d9+10]', str(random.randint(11, 19))).replace('[1d9]',
                                                                                                           str(random.randint(
                                                                                                               1,
                                                                                                               9))).replace(
        '[1d10]', str(random.randint(1, 10))).replace('[3d6+10]', str(random.randint(13, 28))).replace("[3d6+15]",
                                                                                                       str(random.randint(
                                                                                                           18,
                                                                                                           33))).replace(
        '[3d6]', str(random.randint(3, 18))).replace("[1d5+15]", str(random.randint(16, 20))).replace("[5d6+25]",
                                                                                                      str(random.randint(
                                                                                                          30, 55)))
    return str(infected)


def ceshi():
    jieguo = random.choice(ark.get("综合体检测试"))
    sfas = ark.get("_测试结果")
    jieguo = jieguo.format(random.choice(sfas), random.choice(sfas), random.choice(sfas), random.choice(sfas),
                           random.choice(sfas), random.choice(sfas))
    return jieguo


def zhiye():
    zhiye = random.choice(ark.get("方舟职业"))
    mainZ = zhiye.split("-")[0] + "分支"

    zhiye = zhiye.format(random.choice(ark.get(mainZ)))
    return zhiye


def arkOperator():
    s = "为生成的干员信息如下：\n{}\n【性别】{}\n【种族】{}\n【出身地】{}\n【战斗经验】{}\n【身高】[{}]cm\n【感染情况】{}\n—综合体检测试—\n{}\n【职业】{}".format(
        random.choice(ark.get("方舟稀有度")), random.choice(ark.get("干员性别")), random.choice(ark.get("方舟种族")),
        random.choice(ark.get("方舟地区")),
        random.choice(ark.get("战斗经验")).replace("_数字a", str(random.randint(1, 34))), str(random.randint(146, 210)),
        calc(), ceshi(), zhiye())
    return s

def get_cp_mesg(gong, shou):
    with open('data/autoReply/cp.json', "r", encoding="utf-8") as f:
        cp_data = json.loads(f.read())
    return random.choice(cp_data['data']).replace('<攻>', gong).replace('<受>', shou)


async def emojimix(emoji1, emoji2):
    if is_emoji(emoji1) and is_emoji(emoji2):
        pass
    else:
        print("not emoji")
        return None
    url = f"http://promptpan.com/mix/{emoji1}/{emoji2}"
    #url=f"https://emoji6.com/emojimix/?emoji={emoji1}+{emoji2}"
    path = "data/pictures/cache/" + random_str() + ".png"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        #print(r.content)
        with open(path, "wb") as f:
            f.write(r.content)  # 从二进制数据创建图片对象
        # print(path)
        return path
url = "https://www.ipip5.com/today/api.php"
url2 = "https://api.pearktrue.cn/api/steamplusone/"


async def hisToday():
    async with httpx.AsyncClient(timeout=100) as client:
        data = {"type": "json"}
        r = await client.get(url, params=data)
        return r.json()


async def steamEpic():
    url = 'https://steamstats.cn/en/xi'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.41'}
    
    async with httpx.AsyncClient(timeout=100) as client:
        try:
            response = await client.get(url, headers=headers)
            
            response.raise_for_status()
            
            soup = bs(response.text, "html.parser")
            tbody = soup.find('tbody')
            tr = tbody.find_all('tr')
            
            i = 1
            text = "\n"
            for tr in tr:
                td = tr.find_all('td')
                name = td[1].string.strip().replace('\n', '').replace('\r', '')
                gametype = td[2].string.replace(" ", "").replace('\n', '').replace('\r', '')
                start = td[3].string.replace(" ", "").replace('\n', '').replace('\r', '')
                end = td[4].string.replace(" ", "").replace('\n', '').replace('\r', '')
                time = td[5].string.replace(" ", "").replace('\n', '').replace('\r', '')
                oringin = td[6].find('span').string.replace(" ", "").replace('\n', '').replace('\r', '')
                text += f"序号：{i}\n" \
                        f"游戏名称：{name}\n" \
                        f"DLC/game：{gametype}\n" \
                        f"开始时间：{start}\n" \
                        f"结束时间：{end}\n" \
                        f"是否永久：{time}\n" \
                        f"平台：{oringin}\n"
                i += 1

        except httpx.HTTPStatusError as e:
            text = f"HTTP错误: {e}"
        except Exception as e:
            text = f"发生错误: {e}"

    return text
async def arkSign(url):
    url = f"https://api.lolimi.cn/API/ark/a2.php?img={url}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
    #print(r.text)
    #print(r.text,type(r.json()))
    return str(r.text)
# 百度图片搜索并下载图片
async def baidusearch_and_download_image(keyword):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
        "Priority": "u=4",
        "TE": "Trailers"
    }
    search_url = f"https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&word={keyword}"
    
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            response = await client.get(search_url)
            response.raise_for_status()
            data = response.json()

            # 找到第一次出现的thumbURL
            thumb_url = next((item['thumbURL'] for item in data.get('data', []) if 'thumbURL' in item), None)
            
            if not thumb_url:
                raise ValueError("未找到thumbURL")

            print(f"找到的thumbURL: {thumb_url}")

            # 下载图片
            image_response = await client.get(thumb_url)
            image_response.raise_for_status()

            # 保存图片为JPEG格式
            ranpath = random_str()
            path = f"data/pictures/cache/{ranpath}.jpg"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            img = Image.open(BytesIO(image_response.content))
            img.save(path, format='JPEG')
            print(f"图片保存路径: {path}")
            return path
        
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} {e.response.text}")
        except Exception as e:
            print(f"搜索和下载图片失败: {e}")
        return None
#mc服务器查询
async def minecraftSeverQuery(ip):
    async with httpx.AsyncClient(headers=get_headers(),timeout=20) as client:
        r=await client.get(f"https://list.mczfw.cn/?ip={ip}")

        soup = BeautifulSoup(r.text, 'html.parser')
        # 找到 class 为 "form" 的第一个 <tr> 标签
        description = soup.find('meta', attrs={'name': 'description'}).get('content')
        og_title = soup.find('meta', property='og:title').get('content')
        favicon = soup.find('meta', property='og:image').get('content')
        return "https:"+str(favicon),og_title,description
# Bing 图片搜索并下载图片
async def bingsearch_and_download_image(keyword):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36'
    }
    url = "https://cn.bing.com/images/async?q={0}&first={1}&count={2}&scenario=ImageBasicHover&datsrc=N_I&layout=ColumnBased&mmasync=1&dgState=c*9_y*2226s2180s2072s2043s2292s2295s2079s2203s2094_i*71_w*198&IG=0D6AD6CBAF43430EA716510A4754C951&SFX={3}&iid=images.5599"
    
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            search_url = url.format(urllib.parse.quote(keyword), 1, 35, 1)
            response = await client.get(search_url)
            response.raise_for_status()
            html = response.text
            
            # 从缩略图列表页中找到原图的url
            soup = BeautifulSoup(html, "lxml")
            link_list = soup.find_all("a", class_="iusc")
            image_url = None
            rule = re.compile(r"\"murl\"\:\"http\S[^\"]+")
            for link in link_list:
                result = re.search(rule, str(link))
                if result:
                    image_url = result.group(0).replace('amp;', '')[8:]
                    break
            
            if not image_url:
                raise ValueError("未找到图片URL")
            
            print(f"找到的imageURL: {image_url}")

            # 下载图片
            image_response = await client.get(image_url)
            image_response.raise_for_status()

            # 保存图片为JPEG格式
            ranpath = random_str()
            path = f"data/pictures/cache/{ranpath}.jpg"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            img = Image.open(BytesIO(image_response.content))
            img.save(path, format='JPEG')
            print(f"图片保存路径: {path}")
            return path
        
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} {e.response.text}")
        except Exception as e:
            print(f"搜索和下载图片失败: {e}")
        return None

# 并发请求百度和Bing图片搜索，返回最先成功的图片路径
async def search_and_download_image(keyword):
    tasks = [
        asyncio.create_task(baidusearch_and_download_image(keyword)),
        asyncio.create_task(bingsearch_and_download_image(keyword))
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in done:
        path = task.result()
        if path:
            # 取消未完成的任务
            for task in pending:
                task.cancel()
            return path

    # 如果第一个完成的任务返回None，继续等待其他任务完成
    done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
    for task in done:
        path = task.result()
        if path:
            return path

    return None
#英语语法分析
async def eganylist(text,proxy):
    proxies=None
    if proxy!="" or proxy!=" ":
        proxies = {
            "http://": proxy,
            "https://": proxy
        }
    URL = f"https://api.aipie.cool/api/ega/analysis/img?text={text}"
    async with httpx.AsyncClient(timeout=20,proxies=proxies,verify=False) as client:
        r = await client.get(URL)
        p = "data/pictures/cache/" + random_str() + '.png'
        with open(p, "wb") as f:
            f.write(r.content)
        return p
