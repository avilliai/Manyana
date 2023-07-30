<div align="center">
   <img width="160" src="config/Manyana.jpg" alt="logo"></br>

   

----


Manyana基于[Mirai框架](https://github.com/mamoe/mirai) ，使用了[YiriMirai](https://github.com/YiriMiraiProject/YiriMirai) 以进行更便捷的开发。

封面图片来源于[stella](https://www.pixiv.net/artworks/109772665) ,很漂亮的ai绘画。

项目的名字来源于
     <p>佛教中的末那识，它是介于意识(第六识)与阿赖耶识(第八识)之间的第七识</p>
     <p>它是当下的感官经验与更本原性的阿赖耶识——一切现象的种子之间的桥梁。这很抽象所以我用它做了新项目的名字</p>

</div>

- 项目使用了CjangCjengh的[MoeGoe](https://github.com/CjangCjengh/MoeGoe) 以及他的语音模型
- 基于[Yiri-mirai](https://github.com/YiriMiraiProject/YiriMirai) 实现
- 请确保py版本为3.9
- 请确保已安装[[fireFox浏览器](https://www.firefox.com.cn/)
- 请确保已安装[mirai-api-http](https://github.com/project-mirai/mirai-api-http) 并[正确配置](https://github.com/avilliai/wReply/blob/master/setting.yml)
- 可选安装[mirai-login-solver-sakura](https://github.com/KasukuSakura/mirai-login-solver-sakura)
- 可选安装[Mirai点歌插件](https://github.com/khjxiaogu/MiraiSongPlugin)
- 可选安装[PetPet](https://github.com/Dituon/petpet)

# 部署
- 从release下载setUps.rar并解压，依次安装，一般默认下一步就行(**安装python的第一步一定要先勾选add to path**)。apk安装到手机。
- 特别地，对于watt Toolkit，开始加速前一定要勾选上加速github。不过你既然都到这里了，想必也用不到它。
- 克隆本仓库。找一个你喜欢的目录(**不要带中文**)打开cmd或git bash执行
```
git clone https://github.com/avilliai/Manyana.git
```
- 解压release中的site-packages.rar，打开cmd输入where python查看你的python安装目录
- 进入python安装目录，找到Lib/site-packages，用release的site-packages替换它
- 填写config.json与config/api.yaml，完成后运行main.py即可。

# 功能
发送@bot 帮助 以查看功能列表
## 图片相关
### 获取壁纸
```angular2html
@bot [数量]张[tag]             #获取[数量]张标签为[tag]的图，可传r18参数但可能发不出    
2张(壁纸|图)            # 区别于上一个指令，这里不用艾特且出图完全随机。满足如下正则表达式即可触发 r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"
```
### 图片评级(成人指数)
```angular2html
ping[图片]
```
### 搜图
```angular2html
搜图[图片]
```
## 自定义回复
```angular2html
开始添加            #此指令用于开始词库添加
删除#关键词         #例如　删除＃孙笑川　
导入词库　　　　　　　#从config/词库.xlsx导入词库
nameXXX           #设定bot对你的特殊称谓为XXX，例如 name吴彦祖　
```
除此之外，你也可以打开config/词库.xlsx进行修改，完成后在群内发送 导入词库

你可以添加语音回复，但回复本身就有一定几率转为语音回复。
## vits语音合成
使用sp查看所有可用角色，或@bot 可用角色
```angular2html
xx说 yourText             # 通过角色名，指定一个角色模型
xx中文yourText            # 此模式下输出为中文
xx日文yourText            #输入日文，输出日文
你也可以不带角色名直接@bot 说 或者使用其他两个指令
```
### 导入模型：
在vits/voiceModel文件夹下新建一个文件夹放置.pth文件和config.json文件，重启main.py即可

![img.png](data/pictures/img.png)
## 信息查询
### 碧蓝档案wiki
```angular2html
ba查询[角色名]      # ba查询优香 查询一个角色信息
```
### 战双wiki
```js
战双查询[角色名]
```
### 历史上的今天
```angular2html
@bot 历史上的今天      # 满足正则表达式 r".*史.*今.*|.*今.*史.*" 即可触发
```
### 天气查询
```angular2html
查询cityName         #例如查询郑州
```
### 新闻
```js
@bot 新闻
```
### 摸鱼人日历
```js
@bot 摸鱼
```
### nasa每日天文
```js
@bot 天文
```

## 好友与加群管理
### 加好友与加群
```angular2html
群内发送 签到     #跟随指引完成签到后大概一分钟后可添加好友，签到2天后可邀请bot加群
```
这将需要你的城市信息，仅用于获取天气信息以完善签到图片
### 群管
#### 关键词审核
````angular2html
添加违禁词XXX
删除违禁词XXX
@bot 查看违禁词
````
#### 涩图审核撤回
```angular2html
/moderate       #开启/关闭本群涩图审核
/阈值50          #设置撤回阈值为50，越涩的图对应的数值越高。阈值越小越容易撤回图片
```
## 定时任务
```js

```
## 小功能
```js
截图#url     #打开指定网页并截图
meme         #抽取一张meme图
运势          #是阿喵喵版本的运势卡
今日塔罗       #塔罗牌
/苏联笑话      #还有/法国笑话 等类似指令
/cp user1 user2   # xxs最喜欢的cp文，但有一说一文笔真不咋地(不是我写的)
干员生成        #我超，粥
原神，启动       # 原神抽签
@bot 诗经      #获取一篇诗经
@bot 周易     #高科技算命
```
## master指令
```
设定角色#角色名   #为语音功能设置一个默认的角色
授权#qq号       #给一个用户授权(群内发送)
退群#群号       #退出指定群
/bl add qq号   #拉黑一个用户
/bl remove qq号   #取消拉黑
/blgroup add 群号
/blgroup remove 群号
notice         # 群发通知用
```
# 可选配置
## 设置api_key
打开config/api.yaml填写对应信息即可，有道必须填，其他的你随意。
## 戳一戳回复
打开config/nudgeReply.yaml即可
```
BeatNudge:         #戳一戳反击的第一条消息
- 生气了哦！
BeatNudge1:       #戳一戳反击后的消息
- 你是笨蛋吗
chineseVoiceRate: 30    #中文回复几率
defaultModel:         #默认语音模型
  modelSelect:        
  - voiceModel/nene/1374_epochsm.pth
  - voiceModel/nene/config.json
  speaker: 2
nudgedReply:        #正常戳一戳的回复
- 呜哇，好害羞啊……不过……
- en?
prob: 9            #反击几率
voiceReply: 50    # 戳一戳转语音几率

```
## 自定义回复相关
由于对config/settings.yaml读写比较频繁，所以这个文件的注释写在了这里
你可以对它进行修改，但一般建议使用默认设置
```angular2html
defaultModel:      #默认语音模型
  modelSelect:       # 模型与配置文件路径
  - voiceModel/nene/1374_epochsm.pth
  - voiceModel/nene/config.json
  speaker: 2          # 默认的speaker，一般单角色语音模型默认为0
wReply:
  banWords:          # 自定义回复敏感词
  - 妈
  chineseVoiceRate: 30  #自定义回复语音使用中文的几率
  replyRate: 3          # 自定义回复不艾特的触发几率
  sizhi: false         # 是否开启思知ai，(没太大必要有一说一)
  turnMessage: true    #是否开启私聊转发，打开bot会把收到的私聊转发给你，很吵建议关闭
  voiceRate: 30      #语音回复几率
```
# 最后
如果觉得项目还不错的话给个star喵，给个star谢谢喵
