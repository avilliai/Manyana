
from bs4 import BeautifulSoup

from plugins.newsEveryDay import get_headers

import httpx
async def banguimiList(year,month,day=None):

    rank = 1  # 排名
    page = 1  # 页数
    top = 24  # 显示上限（默认显示前24个即显示第一页）
    '''try:
        if "年" in str(event.message_chain):
            year = str(event.message_chain).split("年")[0][-1:-5]  # 获取年份参数
            year = re.sub(r'[^\d]', '', year)
        if "月" in str(event.message_chain):
            month = str(event.message_chain).split("月")[0][-1:-3]  # 获取月份参数
            month = re.sub(r'[^\d]', '', month)
            if len(month) < 2:     month = "0" + month  # 月份使用0补齐
        if "top" in str(event.message_chain):
            top = int(str(event.message_chain).split("top")[1])  # 获取top参数
        elif "排行" in str(event.message_chain):
            top = int(str(event.message_chain).split("排行")[1])
        page = top // 24  # 计算页数
        if top % 24 != 0:
            page += 1  # 向上取整
    except:
        pass''' #不太明白是干啥的，没时间看了先注释掉。
    str0 = year + "年" + month + "月 | Bangumi 番组计划\n"
    finNal_Cover = []
    fiNal_Text=[]
    for i in range(1, page + 1):
        url = f"https://bgm.tv/anime/browser/airtime/{year}-{month}?sort=rank&page={i}"  # 构造请求网址，page参数为第i页
        #print(url)
        async with httpx.AsyncClient(timeout=20, headers=get_headers()) as client:  # 100s超时
            response = await client.get(url)  # 发起请求
        soup = BeautifulSoup(response.content, "html.parser")
        #print(soup)
        name_list = soup.find_all("h3")  # 获取番剧名称列表
        score_list = soup.find_all("small", class_="fade")  # 获取番剧评分列表
        popularity_list = soup.find_all("span", class_="tip_j")  # 获取番剧评分人数列表)
        anime_items = soup.find_all("img", class_="cover")

        for iCover in anime_items:
            src_value = str(iCover).split('src="')[1].split('"')[0]
            # 自动补全https前缀
            src_url = f"https:{src_value}"
            finNal_Cover.append(src_url)

        for j in range(len(score_list)):
            try:
                name_jp = name_list[j].find("small", class_="grey").string + "\n    "  # 获取番剧日文名称
            except:
                name_jp = ""
            name_ch = name_list[j].find("a", class_="l").string  # 获取番剧中文名称
            #print(name_list)
            score = score_list[j].string  # 获取番剧评分
            popularity = popularity_list[j].string  # 获取番剧评分人数
            fiNal_Text.append("{:<3}".format(rank)+f"{name_jp}{name_ch}\n    {score}☆  {popularity}\n")
            if rank == top:  # 达到显示上限
                break
            rank += 1
        if len(score_list) < top - (i - 1) * 24:  # 番剧数量少于显示上限
            break
    return fiNal_Text,finNal_Cover

async def bangumisearch(url):
    async with httpx.AsyncClient(timeout=20,headers=get_headers()) as client:  # 100s超时
        response = await client.get(url)  # 发起请求
    soup = BeautifulSoup(response.content, "html.parser")
    subjectlist=soup.find_all("h3")[0:-2]
    crtlist = soup.find_all("h3")[-2].find_all("dd")
    if len(crtlist) == 0:
        subjectlist=soup.find_all("h3")[0:-3]
        crtlist = soup.find_all("h3")[-3].find_all("dd")
    str0=soup.find("title").string+"\n"
    for i in range(len(subjectlist)):
        str0+=f"{i+1}.{subjectlist[i].find('a').string}\n"
    str0+="相关人物：\n"
    for j in range(len(crtlist)):
        str0+=f"0{j+1}.{crtlist[j].string}\n"
    list=[str0,subjectlist,crtlist]
    return list