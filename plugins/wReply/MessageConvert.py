import json
from mirai import FriendMessage, GroupMessage, At, Plain,MessageChain,Startup,Image

from plugins.toolkits import picDwn, random_str


async def EventMessageConvert(messagechain,temp=True):
    if "Plain" in messagechain.json() or "Image" in messagechain.json():
        mesChain=[]
        for i in json.loads(messagechain.json()):
            if i["type"]=="Plain":
                mesChain.append({"text":i["text"]})
            elif i["type"]=="Image":
                if temp:
                    path=await picDwn(i["url"], f"data/pictures/cache/{random_str()}.jpg")
                    mesChain.append({"image":path})
                else:
                    path=await picDwn(i["url"], f"data/autoReply/imageReply/{random_str()}.jpg")
                    mesChain.append({"image":path})
    else:
        mesChain=messagechain.json()
    return mesChain
