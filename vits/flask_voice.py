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
    out=data["out"]
    try:
        speaker = data['speaker']
        modelSelect = data['modelSelect']
    except:
        speaker = 0
        modelSelect = ['voiceModel/amm/amamiyam.pth', 'voiceModel/amm/config.json']
    # 调用 voiceG() 函数
    await voiceGenerate(tex=text, out=out,speakerID=speaker,modelSelect=modelSelect)
    # 将生成的音频返回给客户端
    return out
    #return jsonify({'audio': audio.tolist()})
if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1', port=9080)