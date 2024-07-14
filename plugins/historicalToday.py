import asyncio

import httpx

url = "https://www.ipip5.com/today/api.php"
url2 = "https://api.pearktrue.cn/api/steamplusone/"


async def hisToday():
    async with httpx.AsyncClient(timeout=100) as client:
        data = {"type": "json"}
        r = await client.get(url, params=data)
        return r.json()


async def steamEpic():
    async with httpx.AsyncClient(timeout=100) as client:
        data = {"type": "json"}
        r = await client.get(url2, params=data)
        #print(str(r.json().get("data")).replace(",","\n"))
        st = ""
        for i in r.json().get("data"):
            st += "名称：" + i.get("name") + "\n"
            st += "开始时间：" + i.get('starttime') + "\n"
            st += "结束时间:" + i.get('endtime') + "\n"
            st += "平台:" + i.get('source') + "\n"
            st += "链接:" + i.get('url') + "\n"
            st += "======================\n"
        #print(st)
        return st


if __name__ == '__main__':
    asyncio.run(steamEpic())
