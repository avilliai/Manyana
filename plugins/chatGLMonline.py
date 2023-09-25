# -*- coding: utf-8 -*-
import asyncio

import zhipuai
async def chatGLM(api_key,bot_info,text):
    zhipuai.api_key = api_key
    response = zhipuai.model_api.sse_invoke(
        model="characterglm",
        meta= bot_info,
        prompt= [
            {
                "role": "user",
                "content": text
            }
        ],
        incremental=True
    )
    str1=""
    for event in response.events():
      if event.event == "add":
          str1+=event.data
          #print(event.data)
      elif event.event == "error" or event.event == "interrupted":
          str1 += event.data
          #print(event.data)
      elif event.event == "finish":
          str1 += event.data
          #print(event.data)
          print(event.meta)
      else:
          str1 += event.data
          #print(event.data)
    #print(str1)
    return str1
if __name__ == '__main__':
    apiKey=""
    bot_info={
            "user_info": "liris是yucca最喜欢的人",
            "bot_info": "yucca是一个由avilliai开发的人工智能，yucca的形象与设定属于二次元动漫中的女孩子，说话喜欢带上啊，哦等语气词，yucca的性格非常天真，但拥有丰富的文学与戏剧方面的知识，并且对自己的能力非常自信，在生活中会经常犯一些小错误。yucca十分依赖并喜欢liris",
            "bot_name": "yucca",
            "user_name": "liris"
        }
    while True:
        tex=input("you:")
        asyncio.run(chatGLM(apiKey,bot_info,tex))