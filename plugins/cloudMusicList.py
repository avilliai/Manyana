import asyncio
import json

import httpx


async def getMusicList(musicName):
    url = "http://music.163.com/api/search/pc"
    data = {"s": musicName, "offset": 3, "limit": 10, "type": 1}
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json=json.dumps(data))
        print(r.json())


asyncio.run(getMusicList("starlight delight"))
