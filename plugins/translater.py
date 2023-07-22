import httpx
import requests
import time
import hashlib
import uuid

youdao_url = 'https://openapi.youdao.com/api'  # 有道api地址

# 需要翻译的文本'
async def translate(txt,app_id,app_key,ori="zh-CHS",aim="ja"):
    translate_text = txt

    # 翻译文本生成sign前进行的处理
    input_text = ""

    # 当文本长度小于等于20时，取文本
    if (len(translate_text) <= 20):
        input_text = translate_text

    # 当文本长度大于20时，进行特殊处理
    elif (len(translate_text) > 20):
        input_text = translate_text[:10] + str(len(translate_text)) + translate_text[-10:]

    time_curtime = int(time.time())  # 秒级时间戳获取
     # 应用id
    uu_id = uuid.uuid4()  # 随机生成的uuid数，为了每次都生成一个不重复的数。
      # 应用密钥

    sign = hashlib.sha256(
        (app_id + input_text + str(uu_id) + str(time_curtime) + app_key).encode('utf-8')).hexdigest()  # sign生成

    data = {
        'q': translate_text,  # 翻译文本
        'from': ori,  # 源语言
        'to': aim,  # 翻译语言
        'appKey': app_id,  # 应用id
        'salt': uu_id,  # 随机生产的uuid码
        'sign': sign,  # 签名
        'signType': "v3",  # 签名类型，固定值
        'curtime': time_curtime,  # 秒级时间戳
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(youdao_url, params=data)
        return r.json()["translation"][0]
    #print("翻译后的结果：" + r["translation"][0])  # 获取翻译内容

