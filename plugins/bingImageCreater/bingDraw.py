import os

import httpx

from plugins.RandomStr import random_str
from plugins.bingImageCreater.bingImg import BingArt


async def bingCreate(sockProxy, prompt, _U, kiev):
    os.environ["http_proxy"] = sockProxy
    os.environ["https_proxy"] = sockProxy
    bing_art = BingArt(auth_cookie_U=_U, auth_cookie_KievRPSSecAuth=kiev, auto=True)
    results = bing_art.generate_images(prompt)
    #print(results)
    paths = []
    for i in results.get("images"):
        url2 = i.get("url")
        async with httpx.AsyncClient(timeout=40) as client:
            r1 = await client.get(url2)
        path = "data/pictures/cache/" + random_str() + ".png"
        paths.append(path)
        with open(path, "wb") as f:
            f.write(r1.content)
        # print(path)
    return paths
