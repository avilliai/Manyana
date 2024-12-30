# -*- coding: utf-8 -*-
import asyncio
import os
import random
import re
import copy
# 注释
import yaml

from plugins.ReplyModels import gptOfficial, gptUnofficial, kimi, qingyan,alcexGpt4o,lingyi, stepAI, qwen, gptvvvv, grop, \
    gpt4hahaha, anotherGPT35, chatGLM, relolimigpt2, xinghuo, Gemma, binggpt4, alcex_GPT3_5, freeGemini, free_phi_3_5, \
    free_gemini, sparkAI, wenxinAI, YuanQiTencent,meta_llama
from plugins.googleGemini import geminirep
from plugins.toolkits import newLogger,random_str,translate
logger=newLogger()
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
CoziUrl = resulttr.get("cozi")
berturl = resulttr.get("bert_colab")
#腾讯元器相关配置
yuanqiBotId=resulttr.get("腾讯元器").get("智能体ID")
yuanqiBotToken=resulttr.get("腾讯元器").get("token")
#gemini
geminiapikey = resulttr.get("gemini")
#openai相关配置
openai_transit = resulttr.get("openaiSettings").get("openai-transit")
gptkeys = resulttr.get("openaiSettings").get("openai-keys")
openai_model = resulttr.get("openaiSettings").get("openai-model")
#代理
proxy = resulttr.get("proxy")
GeminiRevProxy = resulttr.get("GeminiRevProxy")
geminimodel=resulttr.get("geminimodel")
#讯飞星火模型配置
sparkAppKey=resulttr.get("sparkAI").get("apiKey")
sparkAppSecret=resulttr.get("sparkAI").get("apiSecret")
sparkModel=resulttr.get("sparkAI").get("spark-model")
#文心一言模型配置
wenxinAppKey=resulttr.get("wenxinAI").get("apiKey")
wenxinAppSecret=resulttr.get("wenxinAI").get("secretKey")
wenxinModel=resulttr.get("wenxinAI").get("wenxin-model")
if proxy != "":
    os.environ["http_proxy"] = proxy

chatGLM_api_key = resulttr.get("chatGLM")
with open('config.json', 'r', encoding='utf-8') as f:
    data = yaml.load(f.read(), Loader=yaml.FullLoader)
config = data
try:
    mainGroup = int(config.get("mainGroup"))
except:
    logger.error("致命错误！mainGroup只能填写一个群的群号!")
    mainGroup = 0
botName = config.get("botName")
botqq = int(config.get("botQQ"))
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
voicegg = result.get("语音功能设置").get("voicegenerate")
friendsAndGroups = result.get("加群和好友")
trustDays = friendsAndGroups.get("trustDays")
glmReply = result.get("chatGLM").get("glmReply")
modelDefault = result.get("chatGLM").get("model")
privateGlmReply = result.get("chatGLM").get("privateGlmReply")
randomModelPriority = result.get("chatGLM").get("randomModel&&&&&Priority")
autoClearWhenError=result.get("chatGLM").get("AutoClearWhenError")
replyModel = result.get("chatGLM").get("model")
trustglmReply = result.get("chatGLM").get("trustglmReply")
maxPrompt = result.get("chatGLM").get("maxPrompt")
voiceLangType = str(result.get("语音功能设置").get("voiceLangType"))
allcharacters = result.get("chatGLM").get("bot_info")
maxTextLen = result.get("chatGLM").get("maxLen")
voiceRate = result.get("chatGLM").get("voiceRate")
speaker = result.get("语音功能设置").get("speaker")
withText = result.get("chatGLM").get("withText")
newLoop = asyncio.new_event_loop()
global chatGLMData
with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
    cha = yaml.load(f.read(), Loader=yaml.FullLoader)

chatGLMData = cha


async def loop_run_in_executor(executor, func, *args):
    try:
        r = await executor.run_in_executor(None, func, *args)
        logger.info(f"并发调用 | successfully running funcname：{func.__name__} result：{r.get('content')}")
        return [str(func.__name__), r]
    except Exception as e:
        # logger.error(f"Error running {func.__name__}: {e}")
        return [str(func.__name__), None]


# 运行异步函数
async def modelReply(senderName, senderId, text, modelHere=modelDefault, trustUser=None, imgurls=None,
                     checkIfRepFirstTime=False,noRolePrompt=False):
    global chatGLMData
    logger.info(modelHere)

    if senderName==None:
        senderName="指挥"
    try:
        if not noRolePrompt:
            if type(allcharacters.get(modelHere)) == dict:
                with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                    resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                meta1 = resy.get("chatGLM").get("bot_info").get(modelHere)
                meta1["user_name"] = senderName
                meta1["user_info"] = meta1.get("user_info").replace("【用户】", senderName).replace("【bot】",
                                                                                                  botName)
                meta1["bot_info"] = meta1.get("bot_info").replace("【用户】", senderName).replace("【bot】",
                                                                                                botName)
                meta1["bot_name"] = botName
                bot_in = meta1
            else:
                bot_in = str("你是" + botName + ",我是" + senderName + "," + allcharacters.get(
                    modelHere)).replace("【bot】",
                                        botName).replace("【用户】", senderName)
        else:
            bot_in = "请你按照我的要求进行接下来的工作，我的要求将在稍后提出。"
    except Exception as e:
        logger.error(e)
        logger.info(f"无法获取到该用户昵称 id：{senderId}")
        try:
            bot_in = str("你是" + botName + allcharacters.get(
                modelHere)).replace("【bot】",
                                    botName).replace("【用户】", "我")
        except:
            if checkIfRepFirstTime:
                return "模型不可用，请联系master重新设定模型", False
            else:
                return "模型不可用，请联系master重新设定模型"
    try:
        loop = asyncio.get_event_loop()

        if text == "" or text == " ":
            text = "在吗"

        if senderId in chatGLMData:
            prompt1 = chatGLMData.get(senderId)
            prompt1.append({"content": text, "role": "user"})
            firstRep = False
        else:
            prompt1 = [{"content": text, "role": "user"}]
            if modelHere == "anotherGPT3.5" or modelHere == "random":
                try:
                    rep = await loop.run_in_executor(None, anotherGPT35, [{"role": "user", "content": bot_in}],
                                                     senderId)
                except:
                    logger.error("初始化anotherGPT3.5失败")
            firstRep = True
        logger.info(f"{modelHere}  bot 接受提问：" + text)

        if modelHere == "random":
            prompt1 = copy.deepcopy(prompt1)  # 去重人设
            tasks = []
            logger.warning("请求所有模型接口")
            # 将所有模型的执行代码包装成异步任务，并添加到任务列表
            #    tasks.append(loop_run_in_executor(loop, cozeBotRep, CoziUrl, prompt1, proxy))# 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, kimi, prompt1, bot_in))              # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, qingyan, prompt1, bot_in))           # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, grop, prompt1, bot_in))              # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, lingyi, prompt1, bot_in))            # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, relolimigpt2, prompt1, bot_in))      # 2024-07-17测试无法解析API
            #    tasks.append(loop_run_in_executor(loop, stepAI, prompt1, bot_in))            # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, qwen, prompt1, bot_in))              # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, gptvvvv, prompt1, bot_in))           # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, gpt4hahaha, prompt1, bot_in))        # 2024-07-17测试无效
            #    tasks.append(loop_run_in_executor(loop, anotherGPT35, prompt1, senderId))    # 2024-07-17测试 初始化失败
            #    tasks.append(loop_run_in_executor(loop, xinghuo, prompt1, senderId))         # 2024-07-17测试无效
            #tasks.append(loop_run_in_executor(loop, Gemma, prompt1, bot_in))         # 2024-07-17测试通过
            tasks.append(loop_run_in_executor(loop, meta_llama, prompt1, bot_in))  # 2024-07-17测试通过
            tasks.append(loop_run_in_executor(loop, free_phi_3_5, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, free_gemini, prompt1, bot_in))  #2024-12-29测试通过
            #tasks.append(loop_run_in_executor(loop,alcexGpt4o,prompt1,bot_in))
            #    tasks.append(loop_run_in_executor(loop,freeGemini,prompt1,bot_in))           # 2024-07-17测试无效

            # tasks.append(loop_run_in_executor(loop,localAurona,prompt1,bot_in))
            # ... 添加其他模型的任务 ...
            aim = {"role": "user", "content": bot_in}
            prompt1 = [i for i in prompt1 if i != aim]
            # prompt1 = [i for i in prompt1 if not (i.get("role") == aim["role"] and i.get("content") == aim["content"])]
            aim = {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"}
            prompt1 = [i for i in prompt1 if i != aim]
            # prompt1 = [i for i in prompt1 if not (i.get("role") == aim["role"] and i.get("content") == aim["content"])]

            done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            reps = {}
            # 等待所有任务完成
            rep = None
            for task in done:
                result = task.result()[1]
                if result is not None:
                    if "content" not in result:
                        continue
                    if "无法解析" in result.get("content") or "reached your free usage limit" in result.get("content"):
                        continue
                    reps[task.result()[0]] = task.result()[1]
                    # reps.append(task.result())  # 添加可用结果

            # 如果所有任务都完成但没有找到非None的结果
            if len(reps) == 0:
                logger.warning("所有模型都未能返回有效回复")
                raise Exception
            # print(reps)
            modeltrans = {"gptX": "gptvvvv", "清言": "qingyan", "通义千问": "qwen", "anotherGPT3.5": "anotherGPT35",
                          "lolimigpt": "relolimigpt2", "step": "stepAI", "讯飞星火": "xinghuo", "猫娘米米": "catRep",
                          "沫沫": "momoRep"}
            for priority in randomModelPriority:
                if priority in modeltrans:
                    priority = modeltrans.get(priority)
                if priority in reps:
                    rep = reps.get(priority)
                    logger.info(f"random模型选择结果：{priority}: {rep}")
                    break
        elif modelHere == "gpt3.5":
            if openai_transit == "" or openai_transit == " ":
                rep = await loop.run_in_executor(None, gptOfficial, prompt1, gptkeys, proxy, bot_in, openai_model)
            else:
                rep = await loop.run_in_executor(None, gptUnofficial, prompt1, gptkeys, openai_transit, bot_in,
                                                 openai_model)
        elif modelHere=="腾讯元器":
            rep=await YuanQiTencent(prompt1,yuanqiBotId,yuanqiBotToken,senderId)
        elif modelHere == "binggpt4":
            # print(1)
            rep = await loop_run_in_executor(None, binggpt4, prompt1, bot_in)
            if type(rep) == list:
                return "模型不可用，请更换模型。"
        elif modelHere == "Gemini":
            r = await geminirep(ak=random.choice(geminiapikey), messages=prompt1, bot_info=bot_in,
                                GeminiRevProxy=GeminiRevProxy, model=geminimodel,imgurls=imgurls,proxy=proxy),
            # print(r,type(r))
            rep = {"role": "assistant", "content": r[0].replace(r"\n", "\n")}
        elif modelHere=="sparkAI" or modelHere=="讯飞星火":
            rep=await sparkAI(prompt1, bot_in,sparkAppKey,sparkAppSecret,sparkModel)
        elif modelHere=="wenxinAI" or modelHere=="文心一言":
            rep=await wenxinAI(prompt1,bot_in,wenxinAppKey,wenxinAppSecret,wenxinModel)
        elif type(allcharacters.get(modelHere)) == dict:
            if (str(senderId) not in trustUser and trustglmReply) and trustUser is not None:
                if checkIfRepFirstTime:
                    return "无模型使用权限！", False
                else:
                    return "无模型使用权限"
            else:
                r = await loop.run_in_executor(None, chatGLM, chatGLM_api_key, bot_in, prompt1)
                rep = {"role": "assistant", "content": r}
        prompt1.append(rep)
        # 超过10，移除第一个元素
        if len(prompt1) > maxPrompt:
            logger.warning(f"{modelHere} prompt超限，移除元素")
            del prompt1[0]
            del prompt1[0]
        chatGLMData[senderId] = prompt1
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        # print(rep.get('content'),type(rep.get('content')))
        # print(rep,type(rep))
        logger.info(f"{modelHere} bot 回复：" + rep.get('content'))
        if checkIfRepFirstTime:
            return rep.get("content"), firstRep
        else:
            return rep.get("content")
        # await tstt(rep.get('content'), event)
    except Exception as e:
        logger.error(e)
        if autoClearWhenError:
            try:
                chatGLMData.pop(senderId)
            except Exception as e:
                logger.error("清理用户prompt出错")
        if checkIfRepFirstTime:
            return "出错，请重试\n或联系master更换默认模型", False
        else:
            return "出错，请重试\n或联系master更换默认模型"


async def clearsinglePrompt(senderid):
    global chatGLMData
    try:
        chatGLMData.pop(senderid)
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        return "已清理近期记忆"
    except:
        logger.error("清理缓存出错，无本地对话记录")
        return "无本地对话记录"
async def clearAllPrompts():
    global chatGLMData
    try:
        chatGLMData = {"f": "hhh"}
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        # print(chatGLMData)
        return "已清除所有用户的prompt"
    except:
        return "清理缓存出错，无本地对话记录"
