import asyncio

import httpx

'''sasda = urllib.request.urlopen(
                "https://api.moderatecontent.com/moderate/?url="+img_url+"&key="+moderateKey).read()
            asf = json.loads(sasda.decode('UTF-8'))
            rate = asf.get('predictions').get('adult')'''


async def weatherQuery1():
    img_url="http://gchat.qpic.cn/gchatpic_new/1840094972/608443475-2712968684-6E5D2D3BCD5DF2EFD9EB80859BBFA8E2/0?term=2&is_origin=0"
    moderateKey='207b10178c64089d90ebfcd7f865d97a'
    url="https://api.moderatecontent.com/moderate/?url="+img_url+"&key="+moderateKey
    async with httpx.AsyncClient(timeout=50) as client:
        r = await client.get(url)
        print(r.json().get('predictions').get('adult'))
        return r.json().get('predictions').get('adult')
if __name__ == '__main__':
    asyncio.run(weatherQuery1())