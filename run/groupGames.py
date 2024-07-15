# -*- coding:utf-8 -*-
import random

import yaml
from mirai import GroupMessage

Roulette = {}


def main(bot, logger):
    with open('config/GroupGameSettings.yaml', 'r', encoding='utf-8') as file:
        ggs = yaml.load(file, Loader=yaml.FullLoader)
    RouletteGGS = ggs.get("RouletteGame")

    @bot.on(GroupMessage)
    async def startRoulette(event: GroupMessage):

        if str(event.message_chain).startswith("/赌 "):
            if event.group.id in Roulette:
                await bot.send(event, random.choice(RouletteGGS.get("prohibited")))
                return
            else:
                try:
                    bullet = int(str(event.message_chain).replace("/赌 ", ""))
                except:
                    await bot.send(event, "无效的指令，请发送/赌 数字 开启赌局，例如 /赌 4")
                    return
                if bullet < 7:
                    magazine = []
                    while len(magazine) < 6:
                        while len(magazine) < bullet:
                            magazine.append(1)
                        magazine.append(0)
                    Roulette[event.group.id] = magazine
                    logger.info(str(magazine))
                    await bot.send(event, "装填弹药" + str(bullet) + "\n请发送s参与游戏")
                else:
                    await bot.send(event, "数值不合法，需求：bullet<7")

    @bot.on(GroupMessage)
    async def runningRoulette(event: GroupMessage):
        if str(event.message_chain) == "s" and event.group.id in Roulette:
            a = random.choice(Roulette.get(event.group.id))
            logger.info("===========")
            logger.info(a)
            logger.info(Roulette.get(event.group.id))
            if a == 1:
                logger.info("禁言")

                try:
                    await bot.mute(target=event.sender.group.id, member_id=event.sender.id,
                                   time=RouletteGGS.get("bantime"))
                    await bot.send(event, random.choice(RouletteGGS.get("muteWord")))
                except:
                    await bot.send(event, random.choice(RouletteGGS.get("muteFailed")))
            else:
                logger.info("不禁言")
                await bot.send(event, random.choice(RouletteGGS.get("unmute")))
            lia = Roulette.get(event.group.id)
            try:
                lia.remove(a)
            except:
                pass
            logger.info(lia)

            if len(lia) < 1 or not lia.count(1):
                Roulette.pop(event.group.id)
                # print("赌局结束")
                await bot.send(event, "赌局结束")
                return
            Roulette[event.group.id] = lia
