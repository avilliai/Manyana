import json

from mirai import At
from mirai import GroupMessage

from plugins.toolkits import send_like, delete_msg


def main(bot,logger,master):
    @bot.on(GroupMessage)
    async def like(event: GroupMessage):
        if str(event.message_chain) == '赞我':
            try:
                res = await send_like(event.sender.id)
                if res == '':
                    await bot.send(event,'已赞你',True)
                else:
                    await bot.send(event,res,True)
            except:
                await bot.send(event,'赞失败',True)
        elif str(event.message_chain).startswith('赞'):
                for element in event.message_chain:
                    if isinstance(element, At):
                        target_qq = element.target
                        res = await send_like(target_qq)
                        if res == '':
                            await bot.send(event,['已赞',At(target_qq)],True)
                        else:
                            await bot.send(event,res,True)
    
    @bot.on(GroupMessage)
    async def chehui(event: GroupMessage):
        if '撤回' in str(event.message_chain) and event.sender.id == master:
            msg = event.json()
            event_dict = json.loads(msg)
            has_quote = any(element.get('type') == 'Quote' for element in event_dict.get('message_chain', []))
            if has_quote:
                quote_id = next((element['id'] for element in event_dict['message_chain']
                                if element.get('type') == 'Quote'), None)
                try:
                    await delete_msg(quote_id)
                except:
                    await bot.send(event,'撤回失败',True)

        
                
                
                
                
