# -*- coding: utf-8 -*-
import base64
import io

import PIL
import asyncio
import copy

import google.generativeai as genai
import httpx

from plugins.RandomStr import random_str
from plugins.gacha import get_headers


#官方sdk的prompt和使用post请求的prompt结构不同，需要进行转换
def promptConvert(input_list):
    for item in input_list:
        new_parts = []
        for part in item.get('parts', []):
            if isinstance(part, dict):  # 如果part是字典，保持不变
                new_parts.append(part)
            else:  # 如果part不是字典，转换成{'text': part}
                new_parts.append({'text': part})
        item['parts'] = new_parts
    return input_list


def convert_content_to_parts_and_role(input_list):
    for item in input_list:
        # 转换'content'键到'parts'
        if 'content' in item:
            item['parts'] = [item['content']]
            del item['content']
        # 转换'role'值从"assistant"到"model"
        if item.get('role') == "assistant":
            item['role'] = "model"
    return input_list


safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

async def GeminiDownloadAllImagesAndSetPrompts(imgurls,rev=False):
    imgresults=[]
    for i in imgurls:
        async with httpx.AsyncClient(timeout=20) as client:
            res =await client.get(i)
            path=f"data/pictures/cache/{random_str()}.png"
            with open(path, 'wb') as f:
                f.write(res.content)
            organ = PIL.Image.open(path)
            organ = organ.resize(((600, int(organ.size[1] * 600 / organ.size[0]))), resample=PIL.Image.LANCZOS)
            if rev:
                buffer = io.BytesIO()
                organ.save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                imgresults.append({"inline_data": {"mime_type": "image/jpeg", "data": img_base64}})
            else:
                imgresults.append(organ)
    return imgresults
async def geminirep(ak, messages, bot_info, GeminiRevProxy="",imgurls=None):
    messages_copy = copy.deepcopy(messages)

    # 在副本上进行操作
    messages_copy.insert(0, {"role": "user", "parts": [bot_info]})
    messages_copy.insert(1, {"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]})
    # 假设convert_content_to_parts_and_role是一个自定义函数，确保它不会修改外部状态
    messages_copy = convert_content_to_parts_and_role(messages_copy)
    if imgurls!=None:
        if GeminiRevProxy==" " or GeminiRevProxy=="":
            rev=False
        else:
            rev=True
        imgPromptResults=await GeminiDownloadAllImagesAndSetPrompts(imgurls,rev)
    if GeminiRevProxy == "" or GeminiRevProxy == " ":
        # Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
        model1 = "gemini-1.5-flash"

        GOOGLE_API_KEY = ak

        genai.configure(api_key=GOOGLE_API_KEY)

        #model = genai.GenerativeModel('gemini-pro')
        generation_config = {
            "candidate_count": 1,
            "max_output_tokens": 256,
            "temperature": 1.0,
            "top_p": 0.7,
        }

        model = genai.GenerativeModel(
            model_name=model1,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        #print(type(messages))
        if imgurls!=None:
            for vb in imgPromptResults:
                messages_copy[-1]['parts'].append(vb)

        response = model.generate_content(messages_copy)

        r = str(response.text.rstrip())
        #print(response.text)

    else:
        messages_copy = promptConvert(messages_copy)
        if imgurls != None:
            for vb in imgPromptResults:
                messages_copy[-1]['parts'].append(vb)
        r = await geminiCFProxy(ak, messages_copy, GeminiRevProxy)
        r = r.rstrip()
    return r


async def geminiCFProxy(ak, messages, proxyUrl):
    url = f"{proxyUrl}/v1beta/models/gemini-1.5-flash:generateContent?key={ak}"
    #print(requests.get(url,verify=False))
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json={"contents": messages, "safetySettings": [
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HARASSMENT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', "threshold": "BLOCK_None"}]})
        print(r)
        return r.json()['candidates'][0]["content"]["parts"][0]["text"]
    #r=requests.post(url,json=message,verify=False)
#支持图片识别的gemini
