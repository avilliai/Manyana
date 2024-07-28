import os

import yaml
import asyncio
from typing import Dict, List, Tuple, Optional

from fuzzywuzzy import fuzz

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
async def getRep(MainDict,key,threshold=80):
    result = await find_most_similar_key_async(
        MainDict,key,threshold
    )
    return result
async def find_most_similar_key_async(json_data, target_key, threshold):
    async def match_key(key: str) -> Tuple[str, int]:
        """异步计算目标键与给定键的相似度得分。"""
        key_data = json_data[key]
        score = 0
        if isinstance(key_data, dict) and ('text' in key_data or 'image_id' in key_data):
            target_data = eval(target_key)
            if 'text' in target_data and 'text' in key_data:
                text_score = await asyncio.to_thread(fuzz.ratio, target_data['text'], key_data['text'])
                score += text_score
            if 'image_id' in target_data and 'image_id' in key_data:
                image_score = await asyncio.to_thread(fuzz.ratio, target_data['image_id'], key_data['image_id'])
                score += image_score
            score=int(score/2)
        else:
            score = await asyncio.to_thread(fuzz.ratio, target_key, key)
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