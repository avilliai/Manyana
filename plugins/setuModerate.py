import asyncio

import httpx


async def setuModerate(img_url,moderateKey):
    url="https://api.moderatecontent.com/moderate/?url="+str(img_url)+"&key="+str(moderateKey)
    async with httpx.AsyncClient(timeout=50) as client:
        r = await client.get(url)
        print(r.json().get('predictions').get('adult'))
        return r.json().get('predictions').get('adult')
async def fileImgModerate(filePath,moderateKey):
    data = {
        "file": (filePath, open(image_path, "rb")),
        "key": moderateKey,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url="https://api.moderatecontent.com/moderate/", data=data)
    print(r.json().get('predictions').get('adult'))
    return r.json().get('predictions').get('adult')

if __name__ == '__main__':

    asyncio.run(setuModerate(a,b))
