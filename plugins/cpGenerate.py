# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import random
import json
def get_cp_mesg(gong, shou):
    with open('data/autoReply/cp.json', "r", encoding="utf-8") as f:
        cp_data = json.loads(f.read())
    return random.choice(cp_data['data']).replace('<攻>', gong).replace('<受>', shou)