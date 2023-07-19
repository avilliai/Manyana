import requests

url = 'https://api.ennead.cc/buruaka/'
response = requests.get(url)
print(response.text)

pointCharacter='https://api.ennead.cc/buruaka/character/ミノリ?region=japan'#指定角色信息
response=requests.get(pointCharacter)
print(response.text,type(response.text))
'''roles='https://api.ennead.cc/buruaka/character?region=japan'#所有角色
response=requests.get(roles)
print(response.text,type(response.text))'''

gacha='https://api.ennead.cc/buruaka/banner?region=japan'#当前卡池信息
response=requests.get(gacha)
print(response.text,type(response.text))

raid='https://api.ennead.cc/buruaka/raid?region=japan'#总力战