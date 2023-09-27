# -*- coding: utf-8 -*-
import datetime
import json
import random
import re
import shutil
import sys

import os
from asyncio import sleep

import httpx
import requests
import yaml
from fuzzywuzzy import process
from mirai import Mirai, FriendMessage, WebSocketAdapter, GroupMessage, Startup
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str
from plugins.imgDownload import dict_download_img
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate
from plugins.wReply.mohuReply import mohuaddReplys, mohudels, mohuadd
from plugins.wReply.superDict import outPutDic, importDict


def main(bot,config,sizhiKey,app_id, app_key,logger):
    logger.info("启动自定义词库")
    logger.info("自定义词库读取配置文件")
    #读取配置文件
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    global blUser
    blUser=result.get("banUser")
    global blGroup
    blGroup = result.get("banGroups")
    with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
        noRes1 = yaml.load(f.read(), Loader=yaml.FullLoader)
        noRes=noRes1.get("noRes")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    trustDays=result.get("trustDays")
    gptReply=result.get("gptReply")
    glmReply = result.get("chatGLM").get("glmReply")
    trustglmReply = result.get("chatGLM").get("trustglmReply")
    global yamlData
    yamlData = result.get("wReply")
    global chineseVoiceRate
    chineseVoiceRate = yamlData.get("chineseVoiceRate")
    global voiceRate
    voiceRate = yamlData.get("voiceRate")
    MaxAllowableLength=yamlData.get("MaxAllowableLength")
    AutoCreatLexicon=yamlData.get("AutoCreatLexicon")
    global osa
    osa=os.listdir("data/autoReply/lexicon")
    # 过滤词库
    global ban
    ban = yamlData.get("banWords")
    # 不艾特回复的几率
    global likeindex
    likeindex = yamlData.get("replyRate")
    global groupLexicon
    groupLexicon=yamlData.get("groupLexicon")
    global sizhi
    sizhi = yamlData.get("sizhi")
    global turnMess
    turnMess = yamlData.get("turnMessage")
    global colorfulCharacter
    colorfulCharacter=yamlData.get("colorfulCharacter")
    colorfulCharacterList=os.listdir("data/colorfulAnimeCharacter")

    with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
        result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMapikeys
    chatGLMapikeys = result222

    with open('config/chatGLMSingelUser.yaml', 'r', encoding='utf-8') as f:
        result224 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMsingelUserKey
    chatGLMsingelUserKey=result224

    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    chatglm = result.get("chatGLM")

    logger.info("读取词库文件中")
    importDict()
    logger.info("读取完成")
    file = open('config/superDict.txt', 'r')
    jss = file.read()
    file.close()

    global superDict
    superDict = json.loads(jss)
    global transLateData
    with open('data/autoReply/transLateData.yaml', 'r',encoding='utf-8') as file:
        transLateData = yaml.load(file, Loader=yaml.FullLoader)

    with open('data/userData.yaml', 'r',encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    global userdict
    userdict = data
    trustUser = []
    for i in userdict.keys():
        data = userdict.get(i)
        times = int(str(data.get('sts')))
        if times > trustDays:
            trustUser.append(str(i))

    logger.info('已读取信任用户' + str(len(trustUser)) + '个')

    #修改为你bot的名字
    global botName
    botName = config.get('botName')
    #你的QQ
    global master
    master=int(config.get('master'))

    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result232 = yaml.load(f.read(), Loader=yaml.FullLoader)

    global modelSelect
    global speaker
    speaker = result232.get("defaultModel").get("speaker")
    modelSelect = result232.get("defaultModel").get("modelSelect")

    logger.info("当前语音模型设定："+str(speaker)+"\n模型"+str(modelSelect))
    global models
    global characters
    models, default, characters = modelLoader()  # 读取模型
    global lock
    lock=False

    @bot.on(GroupMessage)
    async def setDefaultModel(event: GroupMessage):
        if event.sender.id == master and str(event.message_chain).startswith("设定角色#"):
            global speaker
            global modelSelect
            if str(event.message_chain).split("#")[1] in characters:
                speaker1 = str(event.message_chain).split("#")[1]
                speaker = int(characters.get(speaker1)[0])
                modelSelect = characters.get(speaker1)[1]

    #下面的是一堆乱七八糟的变量


    global process1
    process1={}
    global inprocess1
    inprocess1={}

    @bot.on(GroupMessage)
    async def autoCreatNewLexion(event:GroupMessage):
        global osa
        global superDict
        if AutoCreatLexicon==True and str(event.group.id)+".xlsx" not in osa:
            await bot.send(event, "正在创建本群专有词库")
            shutil.copyfile('data/autoReply/lexicon/init.xlsx',
                            'data/autoReply/lexicon/' + str(event.group.id) + ".xlsx")
            logger.info("读取词库文件中")
            importDict()
            logger.info("读取完成")
            file = open('config/superDict.txt', 'r')
            jss = file.read()
            file.close()
            superDict = json.loads(jss)
            osa.append(str(event.group.id) + ".xlsx")
            logger.warning("创建专有词库中：" + str(event.group.id) + ".xlsx")
            await bot.send(event, '已创建本群专有词库\n发送 开始添加 即可进行添加')



    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        global superDict
        if str(event.message_chain) == '开始添加' or str(event.message_chain) == '*开始添加':
            #str(event.sender.id) in trustUser or
            if (event.sender.id==master) or event.sender.id not in blUser:
                global process1
                if str(event.sender.group.id) not in superDict.keys():
                    await bot.send(event,"正在创建本群专有词库")
                    shutil.copyfile('data/autoReply/lexicon/init.xlsx',
                                    'data/autoReply/lexicon/' + str(event.group.id) + ".xlsx")
                    logger.info("读取词库文件中")
                    importDict()
                    logger.info("读取完成")
                    file = open('config/superDict.txt', 'r')
                    jss = file.read()
                    file.close()

                    superDict = json.loads(jss)

                    logger.warning("创建专有词库中："+str(event.group.id) + ".xlsx")
                    await bot.send(event, '已创建本群专有词库')
                await bot.send(event, '请输入关键词')
                if str(event.message_chain) == '*开始添加':
                    if str(event.sender.id) in trustUser:

                        await bot.send(event,"请注意，本次添加的回复将被添加到所有群")
                        process1[event.sender.id] = {"process": 1, "global": True}
                    else:

                        await bot.send(event,"用户信任等级不足，无权操作全局词库。添加内容将仅在本群生效")
                        process1[event.sender.id] = {"process": 1}
                else:
                    process1[event.sender.id] = {"process": 1}
            else:
                await bot.send(event,event.sender.member_name+'没有添加的权限哦....')


    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        global ban
        global process1
        if event.sender.id in process1 and process1.get(event.sender.id).get("process") == 1 and str(event.message_chain)!="over":
            '''if event.message_chain.count(Image) == 1:
                lst_img = event.message_chain.get(Image)
                mohukey = str(lst_img[0].url)
                print(mohukey)
                await bot.send(event, '已记录关键词,请发送回复(发送over结束添加)')
                mohustatus = 2
            checkResult=await checkIfOk(str(event.message_chain),event)
            if checkResult==False:
                await bot.send(event,"检测到违禁词")
            else:'''
            await bot.send(event, '已记录关键词,请发送回复(发送over结束添加)\n文本回复前缀 语音 可以设置为语音回复')
            if "global" in process1.get(event.sender.id):
                process1[event.sender.id] = {"process": 2, "mohukey": str(event.message_chain),
                                             "groupId": event.group.id,"global":True}
            else:
                process1[event.sender.id] = {"process": 2, "mohukey": str(event.message_chain),"groupId":event.group.id}


    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        global ban
        global process1
        if event.sender.id in process1 and process1.get(event.sender.id).get("process") == 2:
            if event.sender.id in process1 and str(event.message_chain)!="over":
                '''checkResult = await checkIfOk(str(event.message_chain),event)
                if checkResult == False:
                    await bot.send(event, "检测到违禁词")
                else:'''
                if 1:
                    if str(event.message_chain).startswith("语音"):
                        logger.info("增加语音回复")
                        ranpath = random_str()
                        path ='../data/autoReply/voiceReply/' + ranpath + '.wav'
                        text = await translate(str(event.message_chain)[2:], app_id, app_key)
                        tex = '[JA]' + text + '[JA]'
                        await voiceGenerate({"text":tex,"out":path,"speaker":speaker,"modelSelect":modelSelect})
                        value = ranpath + '.wav'
                    elif event.message_chain.count(Image) == 1:
                        logger.info("增加图片回复")
                        lst_img = event.message_chain.get(Image)
                        url = lst_img[0].url
                        imgname = dict_download_img(url,"data/autoReply/imageReply")
                        value = imgname.replace("data/autoReply/imageReply/","")
                        value=value.split(".")[0]+".jpg"


                    else:
                        logger.info("增加文本回复")
                        value = str(event.message_chain)
                    global superDict
                    value=value.replace("#","yu")
                    addStr = '添加' + process1.get(event.sender.id).get("mohukey") + '#' + value
                    if "global" in process1.get(event.sender.id):
                        superDict = mohuaddReplys(addStr, str(event.group.id),mode=1)
                    else:
                        superDict = mohuaddReplys(addStr,str(event.group.id))
                    await bot.send(event, '已添加至词库')


                    #outPutDic(str(event.group.id))

    @bot.on(GroupMessage)
    async def init(event: GroupMessage):
        global process1
        if event.sender.id in process1 and str(event.message_chain) == "over":
            process1.pop(event.sender.id)
            await bot.send(event,"结束添加")
            logger.info("读取词库文件中")
            importDict()
            logger.info("读取完成")
            file = open('config/superDict.txt', 'r')
            jss = file.read()
            file.close()
            global superDict
            superDict = json.loads(jss)



    # 模糊词库触发回复
    @bot.on(GroupMessage)
    async def mohu(event: GroupMessage):
        global superDict,botName,likeindex,temp,sizhi,transLateData,trustuser,chatGLMapikeys,chatGLMsingelUserKey
        if (random.randint(0,100)<groupLexicon or At(bot.qq) in event.message_chain) and gptReply==False:
            if At(bot.qq) in event.message_chain:
                if gptReply==True or glmReply==True or (trustglmReply==True and str(event.sender.id) in trustUser):
                    return
                elif event.group.id in chatGLMapikeys:
                    return
                elif str(event.group.id)==str(config.get("mainGroup")) and chatglm!="sdfafjsadlf;aldf":
                    return
                elif event.sender.id in chatGLMsingelUserKey.keys():
                    return
                for i in noRes:
                    if i in str(event.message_chain):
                        return
                getStr = str(event.message_chain).replace("@"+str(bot.qq)+" ", '')
            else:
                getStr = str(event.message_chain)

            if sizhi==True and At(bot.qq) in event.message_chain:

                if random.randint(0,100)<colorfulCharacter:
                    logger.info("彩色小人，启动！")
                    c=random.choice(colorfulCharacterList)
                    await bot.send(event,Image(path="data/colorfulAnimeCharacter/"+c))
                    return
                else:
                    sess = requests.get('https://api.ownthink.com/bot?spoken=' + getStr + '&appid='+random.choice(sizhiKey))
                    answer = sess.text
                    try:
                        answer = json.loads(answer)
                    except:
                        logger.warning("在调用思知ai时出现了一个问题，但似乎又没啥问题，请忽略")
                        return
                    logger.info("ASK:"+getStr)
                    logger.info("bot(思知):" + answer.get("data").get("info").get("text"))
                    replyssssss=answer.get("data").get("info").get("text")

            else:
                #筛选，不是艾特bot就不匹配
                if event.message_chain.count(At) and At(bot.qq) not in event.message_chain:
                    return
                #优先从专有词库匹配
                elif str(event.group.id) in superDict.keys():
                    #获取专有词库所有key
                    keys1=superDict.get(str(event.group.id)).keys()

                    lock=0
                    lenth1 = 0
                    replyssssss = ""
                    for i in keys1:
                        pat=i.split("/")
                        pattern=""

                        for patts in pat:
                            pattern+=".*"+patts
                        pattern+=".*"
                        match = re.search(pattern, getStr)
                        if match:
                            logger.warning("成功匹配正则表达式：" + pattern)
                            if len(getStr)>len(pat)*MaxAllowableLength:
                                logger.warning("源字符总长过长，为提高匹配准确度不进行匹配")
                                continue
                            if len(pat)>lenth1:
                                lenth1=len(pat)
                                try:
                                    replyssssss=random.choice(superDict.get(str(event.group.id)).get(str((i))))
                                    lock = 1
                                except:
                                    logger.error("当前关键词回复为空")
                                    continue
                    #专有词库没有匹配到，匹配共有词库
                    if lock==0:
                        keys2 = superDict.get("publicLexicon").keys()
                        lock1 = 0
                        lenth1 = 0
                        replyssssss = ""
                        for i in keys2:
                            pat = i.split("/")
                            pattern = ""

                            for patts in pat:
                                pattern += ".*" + patts
                            pattern += ".*"
                            match = re.search(pattern, getStr)
                            if match:
                                logger.warning("成功匹配正则表达式：" + pattern)
                                if len(getStr) > len(pat) * MaxAllowableLength:
                                    logger.warning("源字符总长过长，为提高匹配准确度不进行匹配")
                                    continue
                                if len(pat) > lenth1:
                                    lenth1 = len(pat)
                                    try:
                                        replyssssss = random.choice(
                                            superDict.get(str("publicLexicon")).get(str((i))))
                                        lock1 = 1
                                    except:
                                        logger.error("当前关键词回复为空")
                                        continue
                        if lock1==0:
                            #正则匹配失败，尝试从public.xlsx获取回复
                            if At(bot.qq) in event.message_chain:
                                best_matches = process.extractBests(getStr, superDict.get("public").keys(), limit=3)
                                logger.info("获取匹配结果：key:" + getStr + "|" + str(best_matches))
                                if int((best_matches)[0][1])<50:
                                    logger.warning("匹配相似度过低，不发送")
                                    return
                                replyssssss = random.choice(superDict.get("public").get(str((best_matches)[0][0])))
                elif At(bot.qq) in event.message_chain:
                    best_matches = process.extractBests(getStr, superDict.get("public").keys(), limit=3)
                    logger.info("获取匹配结果：key:" + getStr + "|" + str(best_matches))
                    if int((best_matches)[0][1]) < 50:
                        logger.warning("匹配相似度过低，不发送")
                        return
                    replyssssss = random.choice(superDict.get("public").get(str((best_matches)[0][0])))
                else:
                    return

            try:
                if replyssssss=="":
                    return
            except:
                return
            try:
                logger.info("key:："+getStr+" 选择回复：" + replyssssss)
            except:
                logger.error("回复出现异常，请忽略")
                return
            if random.randint(0, 100) < colorfulCharacter:
                logger.info("彩色小人，启动！")
                c = random.choice(colorfulCharacterList)
                await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                return
            try:
                if str(replyssssss).endswith('.png') or str(replyssssss).endswith('.jpg'):
                    await bot.send(event, Image(path='data/autoReply/imageReply/' + replyssssss))
                elif str(replyssssss).endswith('.wav'):
                    await bot.send(event, Voice(path='data/autoReply/voiceReply/' + replyssssss))
                else:

                    replyssssss = replyssssss.replace("{me}", botName).replace("yucca", botName).replace("小思",  botName).replace("{segment}", ',')

                    if str(event.sender.id) not in userdict:
                        replyssssss = replyssssss.replace("name", str(event.sender.member_name)).replace("{name}", str(event.sender.member_name)).replace("哥哥", str(event.sender.member_name)).replace("您", str(event.sender.member_name))
                    else:

                        setName = userdict.get(str(event.sender.id)).get("userName")
                        if setName==None:
                            setName=event.sender.member_name
                        replyssssss = replyssssss.replace("name", setName).replace("{name}", setName).replace("哥哥", setName).replace("您", setName)

                    if random.randint(1, 100) > voiceRate:
                        await bot.send(event, replyssssss)
                    else:
                        replyssssss = replyssssss.replace(botName, "我")

                        path = '../data/voices/' + random_str() + '.wav'
                        if random.randint(1,100)>chineseVoiceRate:
                            if replyssssss in transLateData:
                                text=transLateData.get(replyssssss)
                            else:
                                text=await translate(str(replyssssss), app_id, app_key)
                                transLateData[replyssssss]=text
                                with open('data/autoReply/transLateData.yaml', 'w', encoding="utf-8") as file:
                                    yaml.dump(transLateData, file, allow_unicode=True)
                                logger.info("写入参照数据:"+replyssssss+"| "+text)
                            tex = '[JA]' + text + '[JA]'
                        else:
                            tex="[ZH]"+replyssssss+"[ZH]"
                        logger.info("启动文本转语音：text: "+tex+" path: "+path[3:])
                        await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})

                        await bot.send(event,Voice(path=path[3:]))
            except:
                logger.error("发送失败，群号"+str(event.group.id)+"关键词："+getStr+" 回复："+replyssssss)
    # 开启和关闭思知ai
    @bot.on(GroupMessage)
    async def sizhiOpener(event:GroupMessage):
        if str(event.message_chain)=="sizhi" and event.sender.id==master:
            global sizhi
            if sizhi==0:
                sizhi=1
                await bot.send(event,"已开启思知ai")
            else:
                sizhi=0
                await bot.send(event,"关闭思知ai")

    # 取消注释开放私聊
    @bot.on(FriendMessage)
    async def mohu(event: FriendMessage):
        global superDict
        global botName
        global sizhi
        global chatGLMsingelUserKey
        #if event.sender.id in blUser:
            #return
        #开启信任用户回复，且为信任用户
        if trustglmReply == True and str(event.sender.id) in trustUser:
            return
        #配置了自己的apiKey
        elif event.sender.id in chatGLMsingelUserKey.keys():
            return
        getStr=str(event.message_chain)
        if sizhi==True:
            if str(event.message_chain)=="[图片]":
                c = random.choice(colorfulCharacterList)
                await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))
                return
            sess = requests.get(
                'https://api.ownthink.com/bot?spoken=' + getStr + '&appid='+random.choice(sizhiKey))

            answer = sess.text
            try:
                answer = json.loads(answer)
            except:
                logger.warning("在调用思知ai时出现了一个问题，但似乎又没啥问题，请忽略")
                return
            logger.info("ASK:"+getStr)
            logger.info("bot(私聊):" + answer.get("data").get("info").get("text"))
            replyssssss = answer.get("data").get("info").get("text")
        else:

            if event.sender.id==bot.qq:
                return
            best_matches = process.extractBests(getStr, superDict.get("public").keys(), limit=3)
            logger.info("获取匹配结果：key:" + getStr + "|" + str(best_matches))
            replyssssss = random.choice(superDict.get("public").get(str((best_matches)[0][0])))
            logger.info("key:：" + getStr + " 选择回复：" + replyssssss)

        if str(replyssssss).endswith('.png') or str(replyssssss).endswith('.jpg'):
            await bot.send(event, Image(path='data/autoReply/imageReply/' + replyssssss))
        elif str(replyssssss).endswith('.wav'):
            return
        else:
            replyssssss = replyssssss.replace("小思", botName).replace("{me}", botName).replace("yucca", botName).replace("{segment}", ',')
            if str(event.sender.id) not in userdict:
                replyssssss=replyssssss.replace("name", str(event.sender.nickname)).replace("{name}", str(event.sender.nickname)).replace("哥哥", str(event.sender.nickname))
            else:
                setName=userdict.get(str(event.sender.id)).get("userName")
                if setName==None:
                    setName=event.sender.nickname
                replyssssss=replyssssss.replace("name", setName).replace("{name}", setName).replace("哥哥", setName)

            logger.info('接收私聊消息,来自' + str(event.sender.get_name()) + ' | ' + str(
                event.sender.id) + '内容：' + event.message_chain)
            global turnMess
            if turnMess == True and event.sender.id != master:
                await bot.send_friend_message(master,'接收私聊消息\n来自：' + str(event.sender.get_name()) + '\nQQ:' + str(event.sender.id) + '\n内容：' + event.message_chain + '\n用--> ' + replyssssss + ' <--回复了')
            else:
                pass
            await bot.send(event, replyssssss)


    @bot.on(FriendMessage)
    async def banTurnMess(event: FriendMessage):
        global turnMess
        if str(event.sender.id)==str(master):
            if str(event.message_chain)=='关闭转发':
                await bot.send(event,'已关闭转发')
                logger.info("关闭私聊转发")
                turnMess=False
            elif str(event.message_chain)=='开启转发':
                logger("开启私聊转发")
                await bot.send(event, '已开启转发')
                turnMess=True

    # 删除模糊回复value
    @bot.on(GroupMessage)
    async def dele(event: GroupMessage):
        if str(event.message_chain).startswith('删除#'):
            global superDict
            #str(event.sender.id) in trustUser or
            if event.sender.id==master or str(event.sender.group.id) in superDict.keys():
                logger.warning("准备删除")
                s1 = str(event.message_chain).split('#')
                aimStr = s1[1]
                lis1=[]

                if aimStr in superDict.get(str(event.group.id)).keys():
                    replyMes = superDict.get(str(event.group.id)).get(aimStr)
                    number = 0
                    for i in replyMes:

                        if i.endswith('.png'):
                            await bot.send(event, ('编号:' + str(number),Image(path='data/autoReply/imageReply/' + i)))
                        elif i.endswith('.wav'):
                            await bot.send(event, '编号:' + str(number))
                            await bot.send(event, Voice(path='data/autoReply/voiceReply/' + i))
                        else:
                            await bot.send(event, '编号:' + str(number)+"\n"+i)
                        number += 1
                    global inprocess1
                    inprocess1[event.sender.id]={"delStr":aimStr,"step":1}
                    await bot.send(event, '请发送要删除的序号')

            else:
                await bot.send(event, event.sender.member_name + '似乎没有删除的权限呢...')

    @bot.on(GroupMessage)
    async def delKeyAndValue(event:GroupMessage):
        global superDict
        if str(event.message_chain).startswith("del#"):
            aim1=str(event.message_chain).split("#")[1]
            if aim1 in superDict.get(str(event.group.id)).keys():
                dicss=mohudels(aim1,str(event.group.id))
                superDict=dicss
                await bot.send(event,"已移除关键词")
                logger.info("导出词库中")
                outPutDic()
                logger.info("导出词库完成")
            else:
                await bot.send(event,"没有该关键词")

    @bot.on(GroupMessage)
    async def delKeyAndValue(event: GroupMessage):
        global superDict
        if str(event.message_chain).startswith("*del#"):
            aim1 = str(event.message_chain).split("#")[1]
            logger.info("尝试删除关键词："+aim1)
            if aim1 in superDict.get("publicLexicon").keys():
                dicss = mohudels(aim1, "publicLexicon")
                sasf=1
                superDict = dicss
            else:
                await bot.send(event,"没有该关键词")
                logger.error("无关键词:"+aim1)
                return
            if sasf==1:
                logger.info("导出词库中")
                outPutDic()
                logger.info("导出词库完成")
                await bot.send(event,"删除成功")
            else:
                logger.info("没有关键词"+aim1)
                await bot.send(event,"没有关键词"+aim1)
    # 删除指定下标执行部分
    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        global superDict
        global inprocess1
        if event.sender.id in inprocess1 and inprocess1.get(event.sender.id).get("step") == 1:
                replyMes = superDict.get(str(event.group.id)).get(inprocess1.get(event.sender.id).get("delStr"))
                try:
                    logger.warning("执行自定义回复删除操作")
                    '''i=replyMes[int(str(event.message_chain))]
                    if i.endswith('.png'):
                        path='data/autoReply/imageReply/' + i
                    elif i.endswith('.wav'):
                        path='data/autoReply/voiceReply/' + i'''
                    del replyMes[int(str(event.message_chain))]
                    #os.remove(path)
                    superDict = mohuadd(inprocess1.get(event.sender.id).get("delStr"), replyMes,str(event.group.id))
                    logger.info("完成删除回复操作")
                    await bot.send(event, '已删除')
                except:
                    await bot.send(event, '下标不合法')
                await bot.send(event,"正在更新词库，请稍候")
                inprocess1.pop(event.sender.id)
                logger.info("导出词库中")
                outPutDic()
                logger.info("导出词库完成")




    @bot.on(GroupMessage)
    async def restarts(event: GroupMessage):
        if str(event.message_chain)=='导入词库' and str(event.sender.id)==str(master):
            logger.info("读取词库文件中")
            importDict()
            logger.info("读取完成")
            file = open('config/superDict.txt', 'r')
            jss = file.read()
            file.close()
            global superDict
            superDict = json.loads(jss)

            logger.info('已读取模糊匹配字典')
            await bot.send(event, '已导入')

    @bot.on(GroupMessage)
    async def accessGiver(event: GroupMessage):
        if str(event.message_chain).startswith("授权群#") and event.sender.id == master:
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                result98 = yaml.load(f.read(), Loader=yaml.FullLoader)
            trustG = result98.get("trustGroups")
            try:
                trustG.append(int(str(event.message_chain).split("#")[1]))
                result98["trustGroups"] = trustG
                with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(result98, file, allow_unicode=True)
                await bot.send(event, "授权群完成")
            except:
                logger.warning("不合规的授权")
                await bot.send(event, "不合规的授权，请严格按照指令格式，例如 授权群#699455559")
            if str(event.message_chain).split("#")[1] + ".xlsx" in os.listdir("data/autoReply/lexicon"):
                await bot.send(event, "已有词库，不再进行创建")
            else:
                await bot.send(event, "正在创建群专有词库.....")
                shutil.copyfile('data/autoReply/lexicon/init.xlsx',
                                'data/autoReply/lexicon/' + str(event.message_chain).split("#")[1] + ".xlsx")
                await bot.send(event, "创建词库完成，即将执行自动更新，期间请勿进行词库添加操作")
                logger.info("读取词库文件中")
                importDict()
                logger.info("读取完成")
                file = open('config/superDict.txt', 'r')
                jss = file.read()
                file.close()
                global superDict
                superDict = json.loads(jss)

                logger.info('已读取模糊匹配字典')
                await bot.send(event, '词库更新完成')


    @bot.on(GroupMessage)
    async def restarts(event: GroupMessage):
        if str(event.message_chain) == '导出词库' and str(event.sender.id) == str(master):
            logger.info("导出词库中")
            outPutDic()
            logger.info("导出词库完成")
            await bot.send(event, '已导出')
    @bot.on(Startup)
    async def updadd(event:Startup):
        while True:
            await sleep(60)
            with open('config/chatGLMSingelUser.yaml', 'r', encoding='utf-8') as f:
                result224 = yaml.load(f.read(), Loader=yaml.FullLoader)
            global chatGLMsingelUserKey
            chatGLMsingelUserKey = result224
    @bot.on(Startup)
    async def updateData(event: Startup):
        while True:
            await sleep(360)
            with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
                result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
            global chatGLMapikeys
            chatGLMapikeys = result222
            logger.info("开始更新数据")
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            global blUser
            blUser = result.get("banUser")
            global blGroup
            blUser = result.get("banGroups")
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            global yamlData
            yamlData = result.get("wReply")
            global voiceRate
            voiceRate = yamlData.get("voiceRate")
            # 过滤词库
            global ban
            ban = yamlData.get("banWords")
            # 不艾特回复的几率
            global likeindex
            likeindex = yamlData.get("replyRate")
            global sizhi
            sizhi = yamlData.get("sizhi")
            global turnMess
            turnMess = yamlData.get("turnMessage")
            logger.info("读取词库文件中")
            importDict()
            logger.info("读取完成")
            file = open('config/superDict.txt', 'r')
            jss = file.read()
            file.close()
            global superDict
            superDict = json.loads(jss)
            with open('config/chatGLMSingelUser.yaml', 'r', encoding='utf-8') as f:
                result224 = yaml.load(f.read(), Loader=yaml.FullLoader)
            global chatGLMsingelUserKey
            chatGLMsingelUserKey = result224
            with open('data/userData.yaml', 'r',encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            global trustUser
            global userdict
            userdict = data
            trustUser = []
            for i in userdict.keys():
                data = userdict.get(i)
                times = int(str(data.get('sts')))
                if times > trustDays:
                    trustUser.append(str(i))

            logger.info('已读取信任用户' + str(len(trustUser)) + '个')
    @bot.on(GroupMessage)
    async def nameChangeOperatot(event:GroupMessage):
        global userdict
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^name\s*(\w+)\s*$', msg.strip())
        if m:
            # 取出指令中的地名
            name = m.group(1)
            for i in ban:
                if i in name:
                    await bot.send(event,"检测到违禁词汇,操作中止")
                    return
            if str(event.sender.id) in userdict:
                data=userdict.get(str(event.sender.id))
                data["userName"]=name
                userdict[str(event.sender.id)]=data
                with open('data/userData.yaml', 'w',encoding="utf-8") as file:
                    yaml.dump(userdict, file, allow_unicode=True)
                logger.info(str(event.sender.id)+"更改了称谓："+name)
                await bot.send(event,"对您的称呼已变更为："+name)
            else:
                await bot.send(event,str(event.sender.member_name)+"还不是用户...发送 签到 试试吧")


    async def checkIfOk(str1,event):
        if event.group.id in blGroup:
            return False
        if event.sender.id in blUser:
            return False
        for i in ban:
            if i in str1:
                return False
        return True




