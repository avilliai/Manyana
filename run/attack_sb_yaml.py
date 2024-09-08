# -*- coding: utf-8 -*-
import os
import random

import yaml
import re
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage, Shutdown,MessageChain


class YamlManager:
    def __init__(self, file_path, initial_data=None):
        """
        初始化YAML管理器，接受YAML文件的路径和可选的初始数据。
        如果YAML文件不存在，则使用初始数据创建文件。
        """
        self.file_path = file_path
        if initial_data is None:
            initial_data = {}
        # 初始化 YAML 文件
        self.initialize_yaml(initial_data)

    def initialize_yaml(self, initial_data):
        """初始化 YAML 文件，若文件不存在则创建并写入初始数据"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                yaml.dump(initial_data, file)
        else:
            # 如果文件存在，但初始数据没有写入，则合并数据
            data = self.read_yaml()
            data.update(initial_data)
            self.write_yaml(data)

    def read_yaml(self):
        """读取 YAML 文件并返回数据"""
        with open(self.file_path, 'r') as file:
            return yaml.safe_load(file) or {}

    def write_yaml(self, data):
        """将数据写入 YAML 文件"""
        with open(self.file_path, 'w') as file:
            yaml.dump(data, file)

    def get_variable(self, var_name):
        """获取变量值，如果变量不存在则返回 0"""
        data = self.read_yaml()
        return data.get(var_name, 0)

    def set_variable(self, var_name, value):
        """设置变量值，如果文件中没有该变量则新增"""
        data = self.read_yaml()
        data[var_name] = value
        self.write_yaml(data)

    def modify_variable(self, var_name, new_value):
        """修改已存在的变量值，如果变量不存在则新增"""
        self.set_variable(var_name, new_value)

    def add_new_variables(self, variables):
        """批量新增或修改变量"""
        data = self.read_yaml()
        data.update(variables)
        self.write_yaml(data)
    
    def clear_yaml(self):
        """清空 YAML 文件内容"""
        self.write_yaml({})  # 将空字典写入文件，相当于清空文件

#随机读取yaml文件内容
def random_yaml_get(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text_list = yaml.safe_load(file)
    return random.choice(text_list)

#攻击无效化的时候保留特定变量，删除其余所有变量
def delete_and_remain(file_path, specific_keys):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    filtered_data = {key: value for key, value in data.items() 
                     if key.startswith("white_list") or key in specific_keys}
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(filtered_data, file, allow_unicode=True)
def main(bot, logger):
    @bot.on(GroupMessage)
    async def Reread_yaml(event: GroupMessage):
        
        #获取master信息
        with open('config.json', 'r', encoding='utf-8') as f:
            data = yaml.load(f.read(), Loader=yaml.FullLoader)
        config = data
        botName = str(config.get('botName'))
        master = int(config.get('master'))
        mainGroup = int(config.get("mainGroup"))
        
        
        
        #初始化文件
        initial_data = {'attack_group_switch': 1, 'limit_of_times': 3, "white_list_"+str(master): 1}
        manager = YamlManager('config/attack_sb_list.yaml', initial_data)
        # 读取群聊变量
        group_id=str(event.group.id)
        group_id_judge=int(manager.get_variable(str(group_id)))
        
        #若列表没有该群，则新增该群变量
        #attack_name_id是被攻击者，attack_state是攻击状态，attack_member是发起者id
        if group_id_judge != 1:
            manager.add_new_variables({str(group_id): 1, 'attack_name_id_'+str(group_id): 404, 'attack_name_id2_'+str(group_id): 404, 'attack_state_'+str(group_id): 0, 'attack_member_'+str(group_id): 404, 'times_'+str(group_id): 0})
            group_id_judge=int(manager.get_variable(str(group_id)))
            
        #测试用，不用管,获取群号和对应变量
        if '测试' in str(event.message_chain) :
            attack_name_id=str(manager.get_variable('attack_name_id_'+str(group_id)))
            attack_state=str(manager.get_variable('attack_state_'+str(group_id)))
            attack_member=str(manager.get_variable('attack_member_'+str(group_id)))
            times=str(manager.get_variable('times_'+str(group_id)))
            white_list_state=str(manager.get_variable("white_list_"+str(attack_name_id)))
            await bot.send(event, "group_id："+str(group_id)+"\n"+"group_id_judge："+str(group_id_judge)+"\n"+'attack_name_id_'+str(group_id)+"："+str(attack_name_id)+"\n"+'attack_state_'+str(group_id)+"："+str(attack_state)+"\n"+'attack_member_'+str(group_id)+"："+str(attack_member)+"\n"+"white_list_state："+str(white_list_state)+"\nmaingroup:"+str(mainGroup))
        
        if str(event.message_chain) == "初始化":
            # 初始化变量，如果报错大概率初始化一下就就好了
            manager.clear_yaml()
            initial_data = {'attack_group_switch': 1, 'limit_of_times': 3, "white_list_"+str(master): 1}
            manager = YamlManager('config/attack_sb_list.yaml', initial_data)
            await bot.send(event, "初始化完成~")
            
            
        #若在bot群内发送攻击无效化则解除被攻击者的攻击状态
        if event.group.id == 674822468 and str(event.message_chain) == "攻击无效化":
            file_path = 'config/attack_sb_list.yaml'
            specific_keys = ['attack_group_switch', 'limit_of_times']  # 保留特定元素的键
            delete_and_remain(file_path, specific_keys)
            await bot.send(event, '已经解除你的攻击状态啦')
            
            
        # 被攻击者白名单，以防有人滥用
        if '攻击白名单' in str(event.message_chain) and int(event.sender.id) == master:
            context=str(event.message_chain)
            name_id_number=re.search(r'\d+', context)
            if name_id_number:
                name_id_number = int(name_id_number.group())
                if '添加' in str(event.message_chain) in event.message_chain:
                    manager.add_new_variables({"white_list_"+str(name_id_number): 1})
                    await bot.send(event, "成功添加")
                if '删除' in str(event.message_chain) in event.message_chain:
                    manager.add_new_variables({"white_list_"+str(name_id_number): 0})
                    await bot.send(event, "成功删除")
        elif '攻击白名单' in str(event.message_chain) and int(event.sender.id) != master:
            await bot.send(event, "非master不可以操作哟")
            
            
        #若列表有该群，则获取其变量值
        if group_id_judge == 1:
            attack_name_id=int(manager.get_variable('attack_name_id_'+str(group_id)))
            attack_name_id2=int(manager.get_variable('attack_name_id2_'+str(group_id)))
            attack_name_id2=attack_name_id
            attack_state=int(manager.get_variable('attack_state_'+str(group_id)))
            attack_member=int(manager.get_variable('attack_member_'+str(group_id)))
            times=int(manager.get_variable('times_'+str(group_id)))
            limit_of_times=int(manager.get_variable('limit_of_times'))
            



        #指定人攻击模块
        #这里的是会等待被攻击者回复并一直攻击的
        if str(event.message_chain).startswith("开始攻击") :
            #获取被攻击者的id
            context=str(event.message_chain)
            attack_name_id=re.search(r'\d+', context)
            attack_member=int(event.sender.id)
            manager.modify_variable('attack_member_'+str(group_id), int(attack_member))
            
            
            if attack_name_id:
                attack_name_id = int(attack_name_id.group())
                manager.modify_variable('attack_name_id_'+str(group_id), str(attack_name_id))
                attack_name_id=int(manager.get_variable('attack_name_id_'+str(group_id)))
                white_list_state=int(manager.get_variable("white_list_"+str(attack_name_id)))
                if attack_name_id == master :
                    await bot.send(event, 'bot不可以攻击主人喵~')
                    manager.modify_variable('attack_state_'+str(group_id), "0")
                elif white_list_state == 1 :
                    await bot.send(event, str(botName)+'不会攻击好孩子的喵~')
                    manager.modify_variable('attack_state_'+str(group_id), "0")
                else:
                        
                        if attack_name_id == master :
                            await bot.send(event, 'bot不可以攻击主人喵~')
                            
                        else:
                            if attack_name_id2 == attack_name_id and attack_state==1:
                                await bot.send(event, str(botName)+'从刚才就一直监听到现在了喵！')
                            if attack_name_id2 != attack_name_id and attack_state==1:
                                manager.modify_variable('times_'+str(group_id), "0")
                                await bot.send(event, str(botName)+'收到！正在转移目标！')
                            if attack_state==0:
                                name_nickname = str(event.sender.member_name)
                                await bot.send(event, "@"+str(name_nickname)+" "+"收到！！即刻开始攻击！！！")
                                manager.modify_variable('times_'+str(group_id), "0")
                                manager.modify_variable('attack_state_'+str(group_id), "1")
                                manager.modify_variable('attack_name_id2_'+str(group_id), int(attack_name_id))
        if str(event.message_chain).startswith("停止攻击"):
            if event.sender.id == attack_name_id :
                #await bot.send(event, "被攻击的孩子不可以自己取消哦，请到bot群："+str(mainGroup)+" 内发送“攻击无效化”哦")
                pass
            else:
                manager.modify_variable('attack_state_'+str(group_id), "0")
                name_nickname = str(event.sender.member_name)
                await bot.send(event, "@"+str(name_nickname)+" "+'好的主人，这就先放他一马')
        if str(event.message_chain) == "查询攻击状态":
            if attack_state ==0:
                await bot.send(event, str(botName)+'正在休息喵')
            if attack_state ==1:
                await bot.send(event, str(botName)+'正在等待目标发言并攻击')







        #判断并发送攻击文本
        if event.sender.id == attack_name_id and attack_state == 1 :
            attack_state=int(manager.get_variable('attack_state_'+str(group_id)))
            attack_name_id=int(event.sender.id)
            white_list_state=int(manager.get_variable("white_list_"+str(attack_name_id)))
            rnum1=random.randint(1,100)
            if str(event.message_chain).startswith("停止攻击") :
                await bot.send(event, "被攻击的孩子不可以自己取消哦，请到bot群："+str(mainGroup)+" 内发送“攻击无效化”哦")
            else:
                if '漫朔' in str(event.message_chain) or 'manshuo' in str(event.message_chain) or'漫溯' in str(event.message_chain) or'漫说' in str(event.message_chain) or'慢说' in str(event.message_chain):
                    await bot.send(event, "不可以欺负漫朔哥哥哦~~")
                                    
                elif white_list_state == 1 :
                    manager.modify_variable('attack_state_'+str(group_id), "0")
                    await bot.send(event, str(botName)+'不会攻击好孩子的喵~')
                    
                else:
                    if rnum1 < 51:
                        if times > limit_of_times:
                            times=times+1
                            manager.modify_variable('times_'+str(group_id), int(times))
                            limits=limit_of_times+3
                            if times < limits:
                                await bot.send(event, "攻击次数太多啦，"+str(botName)+"要做个好孩子喵~", True)
                        else:
                            file_path = 'config/attack_elements.yaml'
                            attack_context = random_yaml_get(file_path)
                            await bot.send_group_message(event.sender.group.id, [At(attack_name_id), " "+str(attack_context)])
                            times=times+1
                            manager.modify_variable('times_'+str(group_id), int(times))
            
            
        
        
        
        #这里的是只会攻击一次的
        if str(event.message_chain).startswith("攻击") :
            context=str(event.message_chain)
            name_id_number=re.search(r'\d+', context)
            if name_id_number:
                number = int(name_id_number.group())
                white_list_state=int(manager.get_variable("white_list_"+str(number)))
                
                if number == master :
                    await bot.send(event, "不可以攻击master哦~~")
                                    
                elif white_list_state == 1 :
                    manager.modify_variable('attack_state_'+str(group_id), "0")
                    await bot.send(event, str(botName)+'不会攻击好孩子的喵~')
                else:
                    file_path = 'config/attack_elements.yaml'
                    attack_context = random_yaml_get(file_path)
                    await bot.send_group_message(event.sender.group.id, [At(number), " "+str(attack_context)])
