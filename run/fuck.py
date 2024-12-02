from mirai import GroupMessage 
import random
from mirai import At

auto_fuck = False
fuck_group = [947612763,920218299]
auto_fuck1 = True
fuck_people = [3252385403,2086184939]

def main(bot, master, logger):  
    logger.info("开始骂人功能")
    
    allow_fuck = [master,2569885855]
    not_renjied = [master]
    
    @bot.on(GroupMessage)     #监听群内事件
    async def fuck(event: GroupMessage): 
        fucking_index = ['sb','史','若只','玩原神玩的','勾八','人机','jb','杂鱼'] 
        if event.sender.id in allow_fuck and "骂" in str(event.message_chain):
            try:
                message_content = event.message_chain
                for element in message_content:
                    if isinstance(element, At):
                        target_qq = element.target
                        await bot.send_group_message(event.group.id, [At(target_qq), f" {random.choice(fucking_index)}"])
            except Exception as e:
                print(f"发生错误: {e}")
                
    @bot.on(GroupMessage)
    async def renji(event: GroupMessage):
        global auto_fuck
        if (auto_fuck == True and event.group.id in fuck_group) or (event.sender.id in fuck_people and auto_fuck1 == True):
            try:
                if random.randint(0, 5) <= 1 and event.sender.id not in not_renjied:
                    logger.info("renji")
                    await bot.send_group_message(event.group.id, [At(event.sender.id), ' 你个仁济'])
                else:
                    logger.info("not_renji")
                    pass
            except Exception as e:
                print(f"发生错误: {e}")