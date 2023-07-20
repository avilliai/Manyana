<div align="center">
   <img width="160" src="config/Manyana.jpg" alt="logo"></br>

   

----


Manyana基于开源框架Mirai进行开发，其前身是于2021年立项的Yucca

这个项目的名字来源于
     <p>佛教中的末那识，它是介于意识(第六识)与阿赖耶识(第八识)之间的第七识</p>
     <p>它是当下的感官经验与更本原性的阿赖耶识——一切现象的种子之间的桥梁。这很抽象所以我用它做了新项目的名字</p>
</div>


# 目录介绍
## 文件
- config.json 是基础配置文件，你需要在里面填写bot的基础信息
- main.py是总控文件，准备好环境后启动它即可

## 文件夹
- config文件夹用于填写额外的配置文件
- data文件夹存放各种数据
- plugins文件夹实现具体功能
- run文件夹调用plugins中的对应文件
- vits文件夹实现语音合成

# 功能
## 图片相关
### 获取壁纸
```angular2html
@bot 5张壁纸      
满足如下正则表达式即可触发 r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"
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
导入模型：
    ![img.png](data/pictures/img.png)
    把pth文件和config.json文件放置在vits/voiceModel文件夹下，重启main.py即可
    
```


# 可选配置
## 设置api_key
打开config/api.yaml填写对应信息即可
## 戳一戳回复
打开config/nudgeReply.yaml即可
## 自定义回复相关
由于对config/settings.yaml读写比较频繁，所以这个文件的注释写在了这里

你可以对它进行修改，但一般建议使用默认设置
```angular2html
wReply:                    #这是自定义回复的内容
  banWords:                #设置自定义回复屏蔽词
  - 妈
  - 孙笑川
  replyRate: 5             #不艾特时的回复几率
  sizhi: false             #是否启用思知ai
  turnMessage: true        #是否开启私聊转发
  voiceRate: 20            #语音回复几率
# 下面这些你基本可以不用管，这些是自动的。
banGroups:                 #黑名单群
- 1235799
- 578904
banUser:                   #黑名单用户
- 91793712344
- 741927340
moderate:                  #审核
  banTime: 300             #禁言时长
  banWords:                #群聊敏感词撤回
    '60844343475':
    - 斯卡蒂
  groups:                  #涩图审核撤回
    '69945555439': 50
  threshold: 40            #基础撤回阈值


```
