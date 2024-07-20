
from bs4 import BeautifulSoup

from plugins.newsEveryDay import get_headers

import httpx
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