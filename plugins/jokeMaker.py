# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import random
from plugins.jokes import soviet_jokes, america_jokes, french_jokes, jokes


def get_joke(joke_tp):
    if joke_tp == '法国':
        return random.choice(french_jokes)
    elif joke_tp == '美国':
        return random.choice(america_jokes)
    elif joke_tp == '苏联':
        return random.choice(soviet_jokes)
    else:
        if joke_tp == '':
            joke_tp = 'yiris'
        return random.choice(jokes).replace('%name%', joke_tp)