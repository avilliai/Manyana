# -*- coding:utf-8 -*-
from itertools import repeat
from time import sleep

import asyncio
import datetime
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosed
from websockets import connect

import os
import random
import shutil
import sys
import json

from asyncio import sleep as sleep1, exceptions

# 下面的两行是launcher启动必要设置，勿动。
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mirai.models import ForwardMessageNode, Forward
import yaml
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage, Shutdown, MessageChain

from plugins.toolkits import newLogger, random_str, get_system_info


# 为了实现黑名单和群开关功能，继承webSocketAdapter类
class MyWebSocketAdapter(WebSocketAdapter):
    def __init__(self, verify_key, host, port, result, qq):
        super().__init__(verify_key=verify_key, host=host, port=port)
        self.result = result
        self.qq = qq  # 添加 QQ 号

    async def _connect(self):
        """重写 _connect 方法，添加重连逻辑并传递额外的头信息"""
        headers = {
            'verifyKey': self.verify_key or '',
            'qq': str(self.qq),
        }
        while True:
            try:
                self.connection = await connect(self.host_name, extra_headers=headers)
                logger.info(f"WebSocket 连接成功：{self.host_name}")
                break
            except Exception as e:
                logger.error(f"WebSocket 连接失败，5 秒后重试：{e}")
                await asyncio.sleep(5)

    async def _receiver(self):
        """重写 _receiver 方法，处理连接关闭异常，尝试自动重连。"""
        await self._connect()
        while True:
            try:
                response = await self.connection.recv()
                data = json.loads(response)
                sync_id = data.get('syncId', '-1')
                self._recv_dict[sync_id].append(data['data'])
            except KeyError:
                logger.error(f'[WebSocket] 收到不正确的数据：{response}')
            except asyncio.CancelledError:
                logger.info('接收器任务已取消。')
                break
            except (websockets.exceptions.ConnectionClosed, ConnectionResetError) as e:
                logger.error(f"WebSocket 连接关闭，原因：{e}")
                # 尝试重新连接
                await self._connect()
            except Exception as e:
                logger.error(f"接收消息时发生异常：{e}")
                await asyncio.sleep(5)

    async def _recv(self, sync_id: str = '-1', timeout: int = 600) -> dict:
        """接收并解析 websocket 数据。"""
        timer = range(timeout) if timeout > 0 else repeat(0)
        for _ in timer:
            if self._recv_dict[sync_id]:
                data = self._recv_dict[sync_id].popleft()
                # print(data)
                if data.get('code', 0) != 0:
                    pass
                    # raise exceptions.ApiError(data)
                try:
                    if "messageChain" in data:
                        if data["sender"]["id"] in self.result["banuser"] or data["sender"]["group"]["id"] in \
                                self.result["botoff"]:
                            pass
                        else:
                            return data
                    else:
                        return data
                except:
                    return data
                # 如果没有对应同步 ID 的数据，则等待 websocket 数据
                # 目前存在问题：如果 mah 发回的数据不含 sync_id，
                # 这里就会无限循环……
                # 所以还是限制次数好了。
            await asyncio.sleep(0.1)
        raise TimeoutError(
            f'[WebSocket] mirai-api-http 响应超时，可能是由于调用出错。同步 ID：{sync_id}。'
        )


if __name__ == '__main__':
    import sys  # 确保导入 sys 模块
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = resulttr.get("proxy")
    if proxy != "":
        os.environ["http_proxy"] = proxy
    counter = 0  # 初始化计数器
    while counter <= 20:
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                data = yaml.load(f.read(), Loader=yaml.FullLoader)

            config = data
            qq = int(config.get('botQQ'))
            key = str(config.get("vertify_key"))
            port = int(config.get("port"))
            global autoSettings
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                autoSettings = yaml.load(f.read(), Loader=yaml.FullLoader)
            bot = Mirai(qq, adapter=MyWebSocketAdapter(
                verify_key=key,
                host='localhost',
                port=port,
                result=autoSettings,
                qq=qq  # 传递 QQ 号
            ))
            botName = config.get('botName')
            master = int(config.get('master'))
            # 芝士logger
            logger = newLogger()

          

            with open('config/controller.yaml', 'r', encoding='utf-8') as f:
                controller = yaml.load(f.read(), Loader=yaml.FullLoader)
            FordMesmenu = controller.get("bot自身设置").get("FordMesMenu")
            nailongSetting = controller.get("检测")
            try:
                if 1:
                    from run import nailong_get
                    nailong_get.main(bot, logger)
            except Exception as e:
                logger.warning(e)
                logger.warning("奶龙检测依赖未安装，如有需要，请使用更新代码-6 安装奶龙检测必要素材")

            bot.run(asgi_server=None)
        except SystemExit as e:
            logger.error(e)
            logger.info(f"发生错误，重新开始执行，重试次数：{counter + 1}")
            counter += 1
            if counter > 10:
                logger.error("重试次数超过 10 次，程序退出")
                sys.exit()
            else:
                # 等待一段时间再重试，避免过于频繁
                sleep(5)
                continue  # 重新开始循环
        except Exception as e:
            logger.error(e)
            logger.info(f"发生错误，重新开始执行，重试次数：{counter + 1}")
            counter += 1
            if counter > 10:
                logger.error("重试次数超过 10 次，程序退出")
                sys.exit()
            else:
                sleep(5)
                continue  # 重新开始循环
