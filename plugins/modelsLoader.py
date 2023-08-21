import datetime
import os

from vits import utils

def modelLoader():
    global modelDll
    modelDll = {}
    a = os.listdir('vits/voiceModel')
    # print(type(a))
    ind = 0

    global CHOISE
    CHOISE = {}

    for i in a:
        # print(i)

        if os.path.isdir('vits/voiceModel/' + i):
            # 内层循环遍历取出模型文件
            file = os.listdir('vits/voiceModel/' + i)
            for ass in file:
                if ass.endswith('.pth'):
                    hps_ms = utils.get_hparams_from_file('vits/voiceModel/' + i + '/config.json')
                    speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
                    muspeakers = {}
                    for id, name in enumerate(speakers):
                        muspeakers[str(id)] = name
                        CHOISE[name] = [str(id), ['voiceModel/' + i + '/' + ass, 'voiceModel/' + i + '/config.json']]

                    modelDll[str(ind)] = ['voiceModel/' + i + '/' + ass, 'voiceModel/' + i + '/config.json', muspeakers]
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    modelSelect = ['voiceModel/' + i + '/' + ass, 'voiceModel/' + i + '/config.json', muspeakers]

                    #print(time + '| 已读取' + 'voiceModel/' + i + '文件夹下的模型文件' + str(muspeakers))
                    ind += 1
            else:
                pass
        else:
            pass
    #print(modelDll)
    return modelDll,modelSelect,CHOISE