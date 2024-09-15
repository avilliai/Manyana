import json
from mirai import FriendMessage, GroupMessage, At, Plain,MessageChain,Startup,Image

from plugins.toolkits import picDwn, random_str


async def EventMessageConvert(messagechain):
    if "Plain" in messagechain.json() or "Image" in messagechain.json():
        mesChain=[]
        for i in json.loads(messagechain.json()):
            if i["type"]=="Plain":
                mesChain.append({"text":i["text"]})
            elif i["type"]=="Image":
                path=await picDwn(i["url"], f"data/autoReply/imageReply/{random_str()}.jpg")
                mesChain.append({"image":path})
    else:
        mesChain=messagechain.json()
    return mesChain
