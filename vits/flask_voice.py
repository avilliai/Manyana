import asyncio
import json

from flask import Flask, request, jsonify

from MoeGoe import voiceGenerate

app = Flask(__name__)

@app.route('/synthesize', methods=['POST'])
async def synthesize():
    # 解析请求中的参数
    data = request.get_json()
    data=json.loads(data)
    text = data['text']
    out="../"+data["out"]
    try:
        speaker = data['speaker']
        modelSelect = data['modelSelect']
    except:
        speaker = 2
        modelSelect = ['voiceModel/nene/1374_epochsm.pth','voiceModel/nene/config.json']

        #with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            #result = yaml.load(f.read(), Loader=yaml.FullLoader)
        #speaker = result.get("vits").get("speaker")
        #modelSelect = result.get("vits").get("modelSelect")
    # 调用 voiceG() 函数
    if modelSelect[0].endswith("I.pth"):
        text=text.replace("[JA]","").replace("[ZH]","")
    await voiceGenerate(tex=text, out=out,speakerID=speaker,modelSelect=modelSelect)
    # 将生成的音频返回给客户端
    return out
    #return jsonify({'audio': audio.tolist()})
if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1', port=9081)