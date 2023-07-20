
import asyncio

import httpx
apiKey=""
url="https://api.openweathermap.org/data/2.5/weather?q=BeiJing&appid="+apiKey+"&lang=zh_cn"
async def weatherQuery1(proxy):
    proxies = {
        "http://": proxy,
        "https://": proxy
    }
    async with httpx.AsyncClient(proxies=proxies) as client:
        r = await client.get(url)
        print(r.json())
        return r.json()
async def querys(city,API_KEY) -> str:
    """查询天气数据。"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f'https://api.seniverse.com/v3/weather/now.json', params={
                'key': API_KEY,
                'location': city,
                'language': 'zh-Hans',
                'unit': 'c',
            })
            resp.raise_for_status()
            data = resp.json()
            return f'当前{data["results"][0]["location"]["name"]}天气为' \
                f'{data["results"][0]["now"]["text"]}，' \
                f'气温{data["results"][0]["now"]["temperature"]}℃。'
        except (httpx.NetworkError, httpx.HTTPStatusError, KeyError):
            return f'抱歉，没有找到{city}的天气数据。'
if __name__ == '__main__':

    asyncio.run(weatherQuery1("http://127.0.0.1:1080"))