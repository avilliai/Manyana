import asyncio

import httpx


async def setuModerate(img_url,moderateKey):
    url="https://api.moderatecontent.com/moderate/?url="+str(img_url)+"&key="+str(moderateKey)
    async with httpx.AsyncClient(timeout=50) as client:
        r = await client.get(url)
        print(r.json().get('predictions').get('adult'))
        return r.json().get('predictions').get('adult')
if __name__ == '__main__':
    a="http://gchat.qpic.cn/gchatpic_new/3552663628/608443475-2630406812-F801C42FB8A2E650EC2F313BFA70C3B5/0?term=2&is_origin=0"
    b="207b10178c64089d90ebfcd7f865d97a"
    asyncio.run(setuModerate(a,b))