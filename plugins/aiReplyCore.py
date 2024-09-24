# -*- coding: utf-8 -*-
import asyncio
import os
import random
import re
import copy
# 注释
import yaml

from plugins.ReplyModels import gptOfficial, gptUnofficial, kimi, qingyan, lingyi, stepAI, qwen, gptvvvv, grop, \
    gpt4hahaha, anotherGPT35, chatGLM, relolimigpt2, xinghuo, Gemma, binggpt4, alcex_GPT3_5, freeGemini, catRep, \
    momoRep, sparkAI, wenxinAI, YuanQiTencent
from plugins.googleGemini import geminirep
from plugins.toolkits import newLogger,random_str,translate
from plugins.vitsGenerate import voiceGenerate, superVG
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
randomModelPriority = result.get("chatGLM").get("randomModel&&&Priority")
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
async def modelReply(sender_name, sender_id, text, model_here=modelDefault, trust_user=None, imgurls=None,
                     check_if_rep_first_time=False):
    global chatGLMData
    logger.info(model_here)
    if sender_name==None:
        sender_name= "指挥"
    try:
        if type(allcharacters.get(model_here)) == dict:
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                resy = yaml.load(f.read(), Loader=yaml.FullLoader)
            meta1 = resy.get("chatGLM").get("bot_info").get(model_here)
            meta1["user_name"] = sender_name
            meta1["user_info"] = meta1.get("user_info").replace("【用户】", sender_name).replace("【bot】",
                                                                                               botName)
            meta1["bot_info"] = meta1.get("bot_info").replace("【用户】", sender_name).replace("【bot】",
                                                                                             botName)
            meta1["bot_name"] = botName
            bot_in = meta1
        else:
            bot_in = str("你是" + botName + ",我是" + sender_name + "," + allcharacters.get(
                model_here)).replace("【bot】",
                                     botName).replace("【用户】", sender_name)
    except Exception as e:
        logger.error(e)
        logger.info(f"无法获取到该用户昵称 id：{sender_id}")
        try:
            bot_in = str("你是" + botName + allcharacters.get(
                model_here)).replace("【bot】",
                                     botName).replace("【用户】", "我")
        except:
            if check_if_rep_first_time:
                return "模型不可用，请联系master重新设定模型", False
            else:
                return "模型不可用，请联系master重新设定模型"
    try:
        loop = asyncio.get_event_loop()

        if text == "" or text == " ":
            text = "在吗"

        if sender_id in chatGLMData:
            prompt1 = chatGLMData.get(sender_id)
            prompt1.append({"content": text, "role": "user"})
            firstRep = False
        else:
            prompt1 = [{"content": text, "role": "user"}]
            if model_here == "anotherGPT3.5" or model_here == "random":
                try:
                    rep = await loop.run_in_executor(None, anotherGPT35, [{"role": "user", "content": bot_in}],
                                                     sender_id)
                except:
                    logger.error("初始化anotherGPT3.5失败")
            firstRep = True
        logger.info(f"{model_here}  bot 接受提问：" + text)

        if model_here == "random":
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
            tasks.append(loop_run_in_executor(loop, Gemma, prompt1, bot_in))  # 2024-07-17测试通过
            tasks.append(loop_run_in_executor(loop, alcex_GPT3_5, prompt1, bot_in))  # 2024-07-17测试通过
            tasks.append(loop_run_in_executor(loop, catRep, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, momoRep, prompt1, bot_in))
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
                    if "无法解析" in result.get("content") or "账户余额不足" in result.get(
                            "content") or "令牌额度" in result.get(
                        "content") or "敏感词汇" in result.get("content") or "request id" in result.get(
                        "content") or "This model's maximum" in result.get(
                        "content") or "solve CAPTCHA to" in result.get("content") or "输出错误请联系站长" in result.get(
                        "content") or "接口失败" in result.get("content") or "psot格式请求" in result.get(
                        "content") or "第三方响应错误" in result.get(
                        "content") or "access the URL on this server" in result.get(
                        "content") or "正常人完全够用" in result.get("content") or "请到我们的官方群" in result.get("content"):
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
        elif model_here == "gpt3.5":
            if openai_transit == "" or openai_transit == " ":
                rep = await loop.run_in_executor(None, gptOfficial, prompt1, gptkeys, proxy, bot_in, openai_model)
            else:
                rep = await loop.run_in_executor(None, gptUnofficial, prompt1, gptkeys, openai_transit, bot_in,
                                                 openai_model)
        elif model_here== "腾讯元器":
            rep=await YuanQiTencent(prompt1, yuanqiBotId, yuanqiBotToken, sender_id)
        elif model_here == "binggpt4":
            # print(1)
            rep = await loop_run_in_executor(None, binggpt4, prompt1, bot_in)
            if type(rep) == list:
                return "模型不可用，请更换模型。"
        elif model_here == "Gemini":
            r = await geminirep(ak=random.choice(geminiapikey), messages=prompt1, bot_info=bot_in,
                                GeminiRevProxy=GeminiRevProxy, model=geminimodel,imgurls=imgurls),
            # print(r,type(r))
            rep = {"role": "assistant", "content": r[0].replace(r"\n", "\n")}
        elif model_here== "sparkAI" or model_here== "讯飞星火":
            rep=await sparkAI(prompt1, bot_in,sparkAppKey,sparkAppSecret,sparkModel)
        elif model_here== "wenxinAI" or model_here== "文心一言":
            rep=await wenxinAI(prompt1,bot_in,wenxinAppKey,wenxinAppSecret,wenxinModel)
        elif type(allcharacters.get(model_here)) == dict:
            if (str(sender_id) not in trust_user and trustglmReply) and trust_user is not None:
                if check_if_rep_first_time:
                    return "无模型使用权限！", False
                else:
                    return "无模型使用权限"
            else:
                r = await loop.run_in_executor(None, chatGLM, chatGLM_api_key, bot_in, prompt1)
                rep = {"role": "assistant", "content": r}
        prompt1.append(rep)
        # 超过10，移除第一个元素
        if len(prompt1) > maxPrompt:
            logger.warning(f"{model_here} prompt超限，移除元素")
            del prompt1[0]
            del prompt1[0]
        chatGLMData[sender_id] = prompt1
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        # print(rep.get('content'),type(rep.get('content')))
        # print(rep,type(rep))
        logger.info(f"{model_here} bot 回复：" + rep.get('content'))
        if check_if_rep_first_time:
            return rep.get("content"), firstRep
        else:
            return rep.get("content")
        # await tstt(rep.get('content'), event)
    except Exception as e:
        logger.error(e)
        if autoClearWhenError:
            try:
                chatGLMData.pop(sender_id)
            except Exception as e:
                logger.error("清理用户prompt出错")
        if check_if_rep_first_time:
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



async def direct_sending_to_model(sender_name, sender_id, text, model_here=modelDefault, trust_user=None, imgurls=None,
                                  check_if_rep_first_time=False):

    logger.info(model_here)

    try:
        # 尝试总结传入文本 text
        loop = asyncio.get_event_loop()

        logger.info(f"aiReplyCore # {model_here}  received request... request by: {sender_id}")

        if not text.strip():  # Handle empty text
            logger.warning(
                f"ChatSummarizer # Empty text param for summarization! If this is abnormal, please check the database and/or calling functions.")
            return "奇怪，没有接收到文本，似乎传入部分出错了？多次出现请联系管理员检查后台"
        if model_here == "random":
            tasks = []
            logger.warning("请求所有模型接口")

            tasks.append(loop_run_in_executor(loop, Gemma, [{"content": text, "role": "user"}], sender_name))
            tasks.append(loop_run_in_executor(loop, alcex_GPT3_5, [{"content": text, "role": "user"}], sender_name))
            tasks.append(loop_run_in_executor(loop, catRep, [{"content": text, "role": "user"}], sender_name))
            tasks.append(loop_run_in_executor(loop, momoRep, [{"content": text, "role": "user"}], sender_name))

            done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            reps = {}
            # 等待所有任务完成
            rep = None
            for task in done:
                result = task.result()[1]
                if result is not None:
                    if "content" not in result:
                        continue
                    if "无法解析" in result.get("content") or "账户余额不足" in result.get(
                            "content") or "令牌额度" in result.get(
                        "content") or "敏感词汇" in result.get("content") or "request id" in result.get(
                        "content") or "This model's maximum" in result.get(
                        "content") or "solve CAPTCHA to" in result.get("content") or "输出错误请联系站长" in result.get(
                        "content") or "接口失败" in result.get("content") or "psot格式请求" in result.get(
                        "content") or "第三方响应错误" in result.get(
                        "content") or "access the URL on this server" in result.get(
                        "content") or "正常人完全够用" in result.get("content") or "请到我们的官方群" in result.get("content"):
                        continue
                    reps[task.result()[0]] = task.result()[1]
                    # reps.append(task.result())  # 添加可用结果

            if not reps:
                logger.warning("所有模型都未能返回有效回复")
                raise Exception

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

        elif model_here == "gpt3.5":
            if openai_transit.strip():
                rep = await loop.run_in_executor(None, gptUnofficial, [{"content": text, "role": "user"}], gptkeys,
                                                 openai_transit, sender_name, openai_model)
            else:
                rep = await loop.run_in_executor(None, gptOfficial, [{"content": text, "role": "user"}], gptkeys, proxy,
                                                 sender_name, openai_model)

        elif model_here == "腾讯元器":
            rep = await YuanQiTencent([{"content": text, "role": "user"}], yuanqiBotId, yuanqiBotToken, sender_id)

        elif model_here == "binggpt4":
            rep = await loop_run_in_executor(None, binggpt4, [{"content": text, "role": "user"}], sender_name)
            if isinstance(rep, list):
                return "binggpt4 模型不可用，请更换模型。"

        elif model_here == "Gemini":
            r = await geminirep(ak=random.choice(geminiapikey), messages=[{"content": text, "role": "user"}],
                                bot_info=sender_name, GeminiRevProxy=GeminiRevProxy, model=geminimodel, imgurls=imgurls)
            rep = {"role": "assistant", "content": r[0].replace(r"\n", "\n")}

        elif model_here == "sparkAI" or model_here == "讯飞星火":
            rep = await sparkAI([{"content": text, "role": "user"}], sender_name, sparkAppKey, sparkAppSecret,
                                sparkModel)

        elif model_here == "wenxinAI" or model_here == "文心一言":
            rep = await wenxinAI([{"content": text, "role": "user"}], sender_name, wenxinAppKey, wenxinAppSecret,
                                 wenxinModel)

        elif isinstance(allcharacters.get(model_here), dict):
            if (str(sender_id) not in trust_user and trustglmReply) and trust_user is not None:
                if check_if_rep_first_time:
                    return "无模型使用权限！", False
                else:
                    return "无模型使用权限"
            else:
                r = await loop.run_in_executor(None, chatGLM, chatGLM_api_key, sender_name,
                                               [{"content": text, "role": "user"}])
                rep = {"role": "assistant", "content": r}

        # 檢查 rep 内容並返回對應回復信息
        if rep is None:
            logger.error(f"Received None instead of a valid response for {model_here} bot.")
            return "An error occurred: No response from the bot."
        else:
            logger.info(f"{model_here} bot 回复：" + rep.get('content', ''))
            if check_if_rep_first_time:
                return rep.get("content", "No content available")
            else:
                return rep.get("content", "No content available")



    except Exception as e:
        logger.error(e)
        if autoClearWhenError:
            chatGLMData.pop(sender_id, None)
        if check_if_rep_first_time:
            return "出错，请重试\n或联系master更换默认模型", False
        else:
            return "出错，请重试\n或联系master更换默认模型"





##################################################################
##### Refactored codes, better readability and extendability #####
#####  解耦合后的代码，具有更好的可阅读性和拓展性                     #####
##################################################################


async def direct_sending_to_model_refactored(sender_name, sender_id, text, model_here=None, trust_user=None, img_urls=None,
                                  check_if_rep_first_time=False):
    """
    Main function to handle sending text to various models and return their responses.
    """
    model_here = model_here or modelDefault  # Use default model if none provided
    logger.info(f"Model: {model_here}, Request by: {sender_id}")

    try:
        # Handle empty text
        if not text.strip():
            logger.warning("LLM core received empty text")
            return "奇怪，语言模型没有收到任何文本，联系管理员检查一下后台？"

        # Select the appropriate model handler
        if model_here == "random":
            rep = await handle_random_model(sender_name, text)
        else:
            rep = await handle_specific_model(sender_name, sender_id, text, model_here, img_urls, img_urls, trust_user)

        # If no response was generated, log an error
        if not rep:
            logger.error(f"No valid response from {model_here}.")
            return "奇怪，语言模型似乎没有正确回应，联系管理员检查一下后台？"

        # Log and return the response
        logger.info(f"{model_here} bot 回复: {rep.get('content', 'No content')}")
        return rep.get("content", "No content available")

    except Exception as e:
        logger.error(f"Error in {model_here}: {e}")
        # Clear prompts if auto-clear is enabled
        if autoClearWhenError:
            chatGLMData.pop(sender_id, None)
        return "出错啦，请重试！\n如果频繁出错的话，请联系master更换默认模型~"


async def handle_random_model(sender_name, text):
    """
    Handle sending the request to multiple models and selecting one at random.
    """

    loop = asyncio.get_event_loop()

    tasks = [
        loop_run_in_executor(loop, Gemma, [{"content": text, "role": "user"}], sender_name),
        loop_run_in_executor(loop, alcex_GPT3_5, [{"content": text, "role": "user"}], sender_name),
        loop_run_in_executor(loop, catRep, [{"content": text, "role": "user"}], sender_name),
        loop_run_in_executor(loop, momoRep, [{"content": text, "role": "user"}], sender_name)
    ]

    # Wait for all tasks to complete
    done, _ = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    # Process the responses and select one based on priority
    responses = {task.result()[0]: task.result()[1] for task in done if task.result()[1]}
    if not responses:
        logger.warning("No valid responses from any model.")
        return None

    # Select the response based on the model priority
    return select_response_by_priority(responses)


def select_response_by_priority(responses):
    """
    Select a response based on predefined priority.
    """
    model_priority_map = {
        "gptX": "gptvvvv", "清言": "qingyan", "通义千问": "qwen", "anotherGPT3.5": "anotherGPT35",
        "lolimigpt": "relolimigpt2", "step": "stepAI", "讯飞星火": "xinghuo", "猫娘米米": "catRep",
        "沫沫": "momoRep"
    }

    for priority in randomModelPriority:
        model = model_priority_map.get(priority, priority)
        if model in responses:
            logger.info(f"Selected model: {model} response.")
            return responses[model]

    logger.warning("No models matched the priority list.")
    return None


async def handle_specific_model(loop, sender_name, sender_id, text, model_here, img_urls, trustUser):
    """
    Handle sending the request to a specific model.
    """
    logger
    model_mapping = {
        "gpt3.5": handle_gpt35,
        "腾讯元器": handle_yuanqi,
        "binggpt4": handle_binggpt4,
        "Gemini": handle_gemini,
        "sparkAI": handle_sparkAI,
        "wenxinAI": handle_wenxinAI,
    }

    # If modelHere matches a key in model_mapping, call the corresponding function
    handler = model_mapping.get(model_here)
    if handler:
        return await handler(sender_name, sender_id, text, img_urls)

    # Default behavior for custom models
    return await handle_custom_model(sender_name, sender_id, text, model_here, trustUser)


async def handle_gpt35(sender_name, sender_id, text, imgurls):
    """
    Handle requests for GPT-3.5.
    """
    loop = asyncio.get_event_loop()

    if openai_transit.strip():
        rep = await loop.run_in_executor(None, gptUnofficial, [{"content": text, "role": "user"}], gptkeys,
                                         openai_transit, sender_name, openai_model)
    else:
        rep = await loop.run_in_executor(None, gptOfficial, [{"content": text, "role": "user"}], gptkeys, proxy,
                                         sender_name, openai_model)


async def handle_yuanqi(sender_name, sender_id, text, imgurls):
    """
    Handle requests for 腾讯元器.
    """
    return await YuanQiTencent([{"content": text, "role": "user"}], yuanqiBotId, yuanqiBotToken, sender_id)


async def handle_binggpt4(sender_name, sender_id, text, imgurls):
    """
    Handle requests for BingGPT4.
    """
    response = await loop_run_in_executor(binggpt4, [{"content": text, "role": "user"}], sender_name)
    if isinstance(response, list):
        logger.error("BingGPT4 model is unavailable.")
        return None
    return response


async def handle_gemini(sender_name, sender_id, text, imgurls):
    """
    Handle requests for Gemini model.
    """
    response = await geminirep(ak=random.choice(geminiapikey), messages=[{"content": text, "role": "user"}],
                               bot_info=sender_name, GeminiRevProxy=GeminiRevProxy, model=geminimodel, imgurls=imgurls)
    return {"role": "assistant", "content": response[0].replace(r"\n", "\n")}


async def handle_sparkAI(sender_name, sender_id, text, imgurls):
    """
    Handle requests for sparkAI (讯飞星火).
    """
    return await sparkAI([{"content": text, "role": "user"}], sender_name, sparkAppKey, sparkAppSecret, sparkModel)


async def handle_wenxinAI(sender_name, sender_id, text, imgurls):
    """
    Handle requests for 文心一言 (wenxinAI).
    """
    return await wenxinAI([{"content": text, "role": "user"}], sender_name, wenxinAppKey, wenxinAppSecret, wenxinModel)


async def handle_custom_model(senderName, senderId, text, modelHere, trustUser):
    """
    Handle requests for custom chatGLM-based models.
    """
    if isinstance(allcharacters.get(modelHere), dict):
        if str(senderId) not in trustUser and trustglmReply:
            logger.warning(f"User {senderId} does not have permission to use model {modelHere}.")
            return None
        return await loop_run_in_executor(chatGLM, chatGLM_api_key, senderName, [{"content": text, "role": "user"}])

    return None
