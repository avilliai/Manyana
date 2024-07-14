# -*- coding:utf-8 -*-
import os.path

from mirai import GroupMessage
from mirai import Image


def main(bot, logger):
    if os.path.exists("./data/star-rail-atlas"):
        logger.info("星穹铁道查询功能启用")
        from plugins.starrailSearch import getxinqiuPath
    else:
        logger.error("缺少星穹铁道图片素材，如需要请执行 更新脚本.bat 下载对应图片素材")
        return

    @bot.on(GroupMessage)
    async def searchImgStarRail(event: GroupMessage):
        if str(event.message_chain).startswith("/星铁查询 "):
            try:
                aim = str(event.message_chain).replace("/星铁查询 ", "")
                p = getxinqiuPath(aim)
                await bot.send(event, Image(path=p))
            except:
                logger.info("没有对应角色")
                await bot.send(event, "没有对应角色")
