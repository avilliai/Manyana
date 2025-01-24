<div align="center">
  <img src="https://socialify.git.ci/avilliai/Manyana/image?description=1&descriptionEditable=mirai&font=Inter&forks=1&issues=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Favilliai%2FimgBed%2Fmaster%2Fimages%2F24202439348A04800FE5D98F76125113.png&name=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Light" alt="Manyana" /></br>
</div>

----
# 🎆鸣谢

- [Mirai](https://github.com/mamoe/mirai)
- [petpet](https://github.com/Dituon/petpet) 
- [CjangCjengh-MoeGoe](https://github.com/CjangCjengh/MoeGoe)
- [overflow](https://mirai.mamoe.net/topic/2565/overflow-%E5%B0%86-mirai-%E5%AE%9E%E7%8E%B0%E6%8D%A2%E6%88%90-onebot-%E6%9C%BA%E5%99%A8%E4%BA%BA%E7%9A%84%E5%8F%88%E4%B8%80%E4%B8%AA%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88?_=1712421277845) 
- [arona api](https://doc.arona.diyigemt.com/) 
- [star-rail-atlas](https://gitee.com/Nwflower/star-rail-atlas) 
- [Yiri-mirai](https://github.com/YiriMiraiProject/YiriMirai)
- [napcat](https://napneko.github.io/)
- [install_llob](https://github.com/super1207/install_llob)
- 如果遇到使用问题，请在QQ群251807019反馈

---

**本仓库将基本不再更新。如果您有意愿参与开发和维护，欢迎pr。<br>
目前开发的重心在[Eridanus](https://github.com/avilliai/Eridanus)。Eridanus旨在实现对Manyana的全面替代，功能更多，占用更低，功能之间的联动性更强。**

[阅读文档](https://doc.luxmix.top/)


> ❗️源码矢山警告⚠，本仓库一开始是我为了学习py而创建的，因此代码内容及项目规划有许多不够明智和成熟的地方，加上并没有很好地管理来自其他开发者的pr，源码杂乱无章，未来有时间会进行整体重构，现在……先凑合着吧
# 大前提: 部署一个onebot实现
项目的结构是onebot实现+overflow+Manyana，所以你需要一个onebot实现才能进行接下来的内容。<br>
下面我会给你列出一些选择<br>
- [napcat](https://napneko.github.io/)
- [llob](https://llonebot.github.io/zh-CN/guide/getting-started)

>还是太过复杂？没关系，下载windows整合包后，部署脚本.pdf 会教你完成napcat的部署，流程十分简单。

# 🚀windows部署
## 方法1：搭建工具部署(推荐)
**请使用此方案搭建**<br>
> 对于windows用户，存在两款启动器，分别是[Manyana1.x](https://github.com/avilliai/Manyana/releases) 和[Manyana_deploy](https://github.com/lux-QAQ/Manyana_deploy/releases) 你可以根据自己的喜好选择<br>

[Manyana1.x](https://github.com/avilliai/Manyana/releases) (啥都不懂你就用这个吧，别给自己上难度了)使用方式如下。
- 从[release](https://github.com/avilliai/Manyana/releases)下载最新整合包并解压
  - 如果下载过慢，你也可以从Q群251807019获得这个压缩包(最新版会先在这里发)
- 解压并阅读 部署文档.pdf

## 方法2：不使用搭建工具(极其不推荐，除非你有丰富bot搭建经验)
- 请确保py版本为3.9
- 请确保已安装[mirai-api-http](https://github.com/project-mirai/mirai-api-http) 并[正确配置](https://github.com/avilliai/wReply/blob/master/setting.yml)
### 如果你仍坚持不使用一键包
- 从[release](https://github.com/avilliai/wReply/releases/tag/yirimirai-Bot)下载python39_amd.exe并安装，(**安装python39的第一步一定要先勾选add to path**)
- 克隆本仓库。找一个你喜欢的目录(**不要带中文**)打开cmd或git bash执行
```
git clone --depth 1 https://github.com/avilliai/Manyana.git
或使用镜像源
git clone --depth 1 https://mirror.ghproxy.com/https://github.com/avilliai/Manyana
其他镜像源(推荐)
git clone --depth 1 https://github.moeyy.xyz/https://github.com/avilliai/Manyana
国内镜像(最快)
git clone --depth 1 https://www.gitlink.org.cn/lux-QAQ/Manyana
```
- 双击Manyana/一键部署脚本.bat即可
- 填写config.json(必做，填写方式见下方)

```
Manyana/config.json的填写示例如下。
{"botName": "机器人名字", "botQQ": "机器人QQ", "master": "你的QQ", "mainGroup": "你自己群的群号","vertify_key": "这里写你http-api的key,尖括号不用带", "port": "httpapi的ws运行端口"}
下面是一个config.json填写实例，如使用整合包，不要修改后两项
{"botName": "Manyana", "botQQ": "1283992481", "master": "1840094972","mainGroup": "623265372", "vertify_key": "1234567890", "port": "23456"}
```
`对于verify_key和port，如果你用了我上面给出的【正确配置】，那就不用动这两项。`
- 启动bot
  - 自行搭建：启动你自己的mirai或overflow，以及Manyana/启动脚本.bat

# 🚀linux部署
[linux部署脚本](https://github.com/lux-QAQ/Manyana_deploy)

---
# 🍩功能
一些功能不会很快同步到菜单(懒得开ps)，请以更新日志为准
#### 功能列表

搭建后在群内发送@bot 帮助 以查看功能列表。其他相关问题请查看[Manyana wiki](https://github.com/avilliai/Manyana/wiki)

<details markdown='1'><summary>图片版菜单</summary>

<div align="center">
   <img width="70%" height="70%" src="data/fonts/help1.png" alt="logo"></br>
   <img width="70%" height="70%" src="data/fonts/help2.png" alt="logo"></br>
   <img width="70%" height="70%" src="data/fonts/help3.png" alt="logo"></br>
   <img width="70%" height="70%" src="data/fonts/help4.png" alt="logo"></br>
   <img width="70%" height="70%" src="data/fonts/master.png" alt="logo"></br>
</div>

</details>


#### 未来更新计划
由于学业繁忙，下面这些可能要到明年才能开始了，如果您有意向参与开发，欢迎pr🏵
- [ ] 各大手游/端游数据查询
- [x] 词库优化
- [x] UI重制
- [x] 优化搭建引导
- [x] jmcomic对接
- [ ] [Eridanus](https://github.com/avilliai/Eridanus)


# 🎲可选配置
<details markdown='1'><summary>填写配置文件</summary>

有关配置文件的填写，config文件夹每个yaml文件基本都有注释，每个yaml文件几乎都是可供修改的，默认的记事本即可打开yaml文件，但对于windows用户尤其是不熟悉yaml用户结构的用户来说，我们强烈建议在launcher的UI中进行配置文件的修改，而不是通过记事本。

不规范地修改配置文件将破坏yaml文件结构并最终导致bot无法运行。

</details>

<details markdown='1'><summary>ai回复配置方式</summary>

请查看[Manyana wiki](https://github.com/avilliai/Manyana/wiki/%E8%AE%BE%E7%BD%AEai%E5%AF%B9%E8%AF%9D%E6%A8%A1%E5%9E%8B)

</details>

# 开源协议
由于 mirai 及 yirimirai 均采用了 AGPL-3.0 开源协议，本项目同样采用 AGPL-3.0 协议。<br>
请注意，AGPL-3.0 是传染性协议。如果你的项目引用了 Manyana，请在发布时公开源代码，并同样采用 AGPL-3.0 协议。不得歪曲、隐藏项目开源事实。<br>

严禁将本项目用于任何违反您所在地区相关法律法规的用途，请在使用本项目时遵循您所在地区的法律法规以及项目相关开源协议，本项目及相关作者不承担任何连带法律责任。
# 🎄最后
如果觉得项目还不错的话给个star喵，给个star谢谢喵
![Star History Chart](https://api.star-history.com/svg?repos=avilliai/Manyana&type=Date)

其他相关项目如下
- [Enkianthus_tts](https://github.com/avilliai/Enkianthus_tts) 简单易用的语音合成工具
- [Petunia](https://github.com/avilliai/Petunia/releases) 轻量版Manyana，无需搭建环境，已打包
- [Amaranth](https://github.com/avilliai/Amaranth) 欢迎关注我们的新版启动器
- [Eridanus](https://github.com/avilliai/Eridanus) Manyana直接对接onebot实现的版本，欢迎参与开发

感谢JetBrains为开源项目提供的license<br>
<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.png" alt="PyCharm logo." width="50">
<div align="center">
   <img width="70%" height="70%" src="https://moe-counter.glitch.me/get/@:manyana" alt="logo"></br>
</div>
