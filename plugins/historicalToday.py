import asyncio

import httpx

url="https://www.ipip5.com/today/api.php"
async def hisToday():
    async with httpx.AsyncClient(timeout=100) as client:
        data = {"type": "json"}
        r = await client.get(url, params=data)
        return r.json()
if __name__ == '__main__':
    asyncio.run(hisToday())
