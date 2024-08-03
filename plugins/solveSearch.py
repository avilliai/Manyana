import re
import httpx
import asyncio
import time
import datetime
from PIL import Image
import io

# 配置
PROXY = None

async def get_steam_game_description(game_id,proxy=None):
    url = f"https://store.steampowered.com/app/{game_id}/"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
        "referer": "https://steamstats.cn/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36",
    }
    async with httpx.AsyncClient(proxies={"http://": proxy, "https://": proxy} if proxy else None) as client:
        response = await client.get(url,headers=headers)
        html = response.text
    
    description = re.findall(r'<div class="game_description_snippet">(.*?)</div>', html, re.S)
    if len(description) == 0:
        return "none"
    return description[0].strip()

async def get_steam_game_search(keyword,proxy=None):
    url = f"https://steamstats.cn/api/steam/search?q={keyword}&page=1&format=json&lang=zh-hans"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
        "referer": "https://steamstats.cn/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36",
    }

    async with httpx.AsyncClient(proxies={"http://": proxy, "https://": proxy} if proxy else None) as client:
        response = await client.get(url, headers=headers)
        result = response.json()

    if len(result["data"]["results"]) == 0:
        print(f"搜索不到{keyword}呢~检查下有没有吧~搜英文名的效果可能会更好喵~")
        return None
    
    return result["data"]["results"][0]

async def solve(keyword,proxy=None):
    search_result = await get_steam_game_search(keyword,proxy)
    if search_result:
        img_url = search_result["avatar"]
        async with httpx.AsyncClient(proxies={"http://": proxy, "https://": proxy} if proxy else None) as client:
            response = await client.get(img_url)
            img_content = response.content
        image = Image.open(io.BytesIO(img_content))
        path = f"data/pictures/cache/{search_result['name']}.png"
        image.save(path)
        description = await get_steam_game_description(search_result["app_id"])

        result_dict = {
            "name": search_result['name'],
            "name_cn": search_result['name_cn'],
            "app_id": search_result['app_id'],
            "description": description,
            "steam_url": f"https://store.steampowered.com/app/{search_result['app_id']}/",
            "path": path
        }
        return result_dict


if __name__ == "__main__":
    keyword = "星露谷物语"  # 替换为你要搜索的关键词
    asyncio.run(solve(keyword))
