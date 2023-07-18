import requests
import json
import numpy as np

# 定义请求参数

data = {'text': '[JA]先生,ちょっとお時間..いただけますか1?[JA]', 'out': 'voices/12121d.wav'}

# 将请求参数转换为 JSON 格式
json_data = json.dumps(data)

# 向本地 API 发送 POST 请求
url = 'http://localhost:9080/synthesize'
response = requests.post(url, json=json_data)
print(response.text)
