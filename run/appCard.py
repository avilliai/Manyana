# -*- coding: utf-8 -*-

from mirai import GroupMessage
from mirai import Image
from mirai.models import App

from plugins.extraParts import arkSign

u = []


def main(bot, logger):
    logger.info("卡片构建已启用")

    @bot.on(GroupMessage)
    async def arkbegin(event: GroupMessage):
        if str(event.message_chain) == "转卡片":
            await bot.send(event, "请发送图片(腾子限制，bot有可能获取不到你的图片)")
            u.append(event.sender.id)

    @bot.on(GroupMessage)
    async def arkkapian(event: GroupMessage):
        if event.message_chain.count(Image):
            if event.sender.id not in u:
                return
            logger.info("开始卡片签名....")
            try:
                lst_img = event.message_chain.get(Image)
                url1 = lst_img[0].url
                ark = await arkSign(url1)
                logger.info("签名完成")
                await bot.send(event, App(ark))
                u.remove(event.sender.id)
            except Exception as e:
                logger.error(e)
                await bot.send(event, "无法获取到卡片url，可能是被腾子针对了捏")
                u.remove(event.sender.id)
