import os

import yaml


def modelLoader():
    a = os.listdir('vits/voiceModel')
    models={}
    for i in a:
        if os.path.isdir('vits/voiceModel/' + i):
            configPath = 'vits/voiceModel/' + i + '/config.json'
            with open(configPath, 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
                speakers = data['speakers']
                text_cleaners = data["data"]['text_cleaners']
            modelPath = ''
            for ass in os.listdir('vits/voiceModel/' + i):
                if ass.endswith('.pth'):
                    modelPath = 'vits/voiceModel/' + i + '/' + ass
            models[str(speakers)]={"speakers":speakers,'modelPath':modelPath,'configPath':configPath,'text_cleaners':text_cleaners}
    return models