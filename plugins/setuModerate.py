import asyncio
import base64

import httpx


async def setuModerate(img_url, moderateKey):
    url = "https://api.moderatecontent.com/moderate/?url=" + str(img_url) + "&key=" + str(moderateKey)
    async with httpx.AsyncClient(timeout=50) as client:
        r = await client.get(url)
        #print(r.json().get('predictions').get('adult'))
        return r.json().get('predictions').get('adult')


async def fileImgModerate(image_path, moderateKey, image_base64=None):
    if image_base64 is None:
        #print(image_path)
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # Encode the image data to base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Prepare the request body
    data = {
        "key": moderateKey,
        "base64": "true",
        "url": f"data:image/png;base64,{image_base64}",
    }

    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.post(url="https://api.moderatecontent.com/moderate/", data=data)
    return r.json().get('predictions').get('adult')


if __name__ == '__main__':
    asyncio.run(fileImgModerate("Pa@RRfK111.png", "6fb083462b3806a00545ddae4c3f2a5b"))
