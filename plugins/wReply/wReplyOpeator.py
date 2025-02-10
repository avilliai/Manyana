import asyncio
import json
import os
from typing import Tuple

import yaml
from fuzzywuzzy import fuzz

from plugins.toolkits import newLogger

logger=newLogger()
async def addRep(key,value,id="publicLexicon"):
    id=f"data/autoReply/lexicon/{id}.yaml"
    if os.path.exists(id):
        with open(id, 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
    else:
        result={}
    result[key] = value
    with open(id, 'w', encoding="utf-8") as file:
        yaml.dump(result, file, allow_unicode=True)
    return loadAllDict()
async def removeRep(key,value,id="publicLexicon"):
    id=f"data/autoReply/lexicon/{id}.yaml"
    with open(id, 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
        result[key] = value
def loadAllDict():
    GroupsDict={}
    for i in os.listdir("data/autoReply/lexicon"):
        if i.endswith(".yaml"):
            with open(f"data/autoReply/lexicon/{i}", 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
                GroupsDict[i.replace(".yaml","")]=result
    return GroupsDict
async def getRep(MainDict,key,threshold,mode,inMaxLength,inWeighting):
    result = await find_most_similar_key_async(
        MainDict,key,threshold,mode,inMaxLength,inWeighting
    )
    return result
async def find_most_similar_key_async(json_data, target_key, threshold,mode,inMaxLength,inWeighting):
    async def match_key(key: str) -> Tuple[str, int]:
        """异步计算目标键与给定键的相似度得分。"""
        try:
            #print(key,type(key))
            #print("===========")
            #print(target_key,type(target_key))
            key_data = json.loads(key)
            target_data = json.loads(target_key)
        except json.JSONDecodeError as e:
            pass
            return key, 0

        score = 0

        key_text = next((item.get('text') for item in key_data if 'text' in item), None)
        target_text = next((item.get('text') for item in target_data if 'text' in item), None) #这个是我们传入的关键字
        if mode=="in" and target_text is not None and key_text is not None:
            if len(target_text)*inMaxLength<len(key_text):
                return key, 0
        #print(key_text, target_text)
        addTextScore = False
        addImageScore=False
        if key_text and target_text:
            text_score = await asyncio.to_thread(fuzz.ratio, target_text, key_text)
            score += text_score
            addTextScore=True
        key_image_id = next((item.get('image_id') for item in key_data if 'image_id' in item), None)
        target_image_id = next((item.get('image_id') for item in target_data if 'image_id' in item), None)
        if key_image_id and target_image_id:
            image_score = await asyncio.to_thread(fuzz.ratio, target_image_id, key_image_id)
            score += image_score
            addImageScore=True
        if addTextScore and addImageScore:
            score=int(score/2)
        '''if not addTextScore and not addImageScore:
            # 如果 text 和 image_id 都没有匹配，则对整个键值对进行匹配
            overall_score = await asyncio.to_thread(fuzz.ratio, key, target_key)
            score = overall_score'''
        if mode == "in" and target_text is not None and key_text is not None:
            if key_text in target_text and score < threshold:
                logger.info(f"当前加权值{inWeighting}")
                score+=inWeighting
                logger.info(f"判断包含，加权成功 当前关键字 {target_text} 匹配对象 {key_text} {score} ")
        return key, score

    # 使用 asyncio.gather 并发计算所有键的相似度得分
    tasks = [match_key(key) for key in json_data.keys()]
    results = await asyncio.gather(*tasks)

    # 找到得分最高的键
    best_match = max(results, key=lambda x: x[1], default=(None, 0))
    best_key, best_score = best_match
    if best_score >= threshold:
        return best_key, json_data[best_key]
    else:
        return None
async def compare2messagechain(old,new):
    key_data=json.loads(old)
    target_data=json.loads(new)
    score = 0

    key_text = next((item.get('text') for item in key_data if 'text' in item), None)
    target_text = next((item.get('text') for item in target_data if 'text' in item), None)  # 这个是我们传入的关键字
    # print(key_text, target_text)
    addTextScore = False
    addImageScore = False
    if key_text and target_text:
        text_score = await asyncio.to_thread(fuzz.ratio, target_text, key_text)
        score += text_score
        addTextScore = True
    key_image_id = next((item.get('image_id') for item in key_data if 'image_id' in item), None)
    target_image_id = next((item.get('image_id') for item in target_data if 'image_id' in item), None)
    if key_image_id and target_image_id:
        image_score = await asyncio.to_thread(fuzz.ratio, target_image_id, key_image_id)
        score += image_score
        addImageScore = True
    if addTextScore and addImageScore:
        score = int(score / 2)
    return score
