import urllib

from plugins.RandomStr import random_str


def dict_download_img(url,dirc):
    img_url = url
    api_token = "fklasjfljasdlkfjlasjflasjfljhasdljflsdjflkjsadljfljsda"
    header = {"Authorization": "Bearer " + api_token} # 设置http header
    request = urllib.request.Request(img_url, headers=header)
    try:
        response = urllib.request.urlopen(request)
        ranpath = random_str()
        if str(url).endswith('.gif') or str(url).endswith('.GIF'):
            img_name = ranpath + ".gif"
        else:
            img_name = ranpath+".jpg"
        filename = dirc+"/"+ img_name
        if (response.getcode() == 200):
            with open(filename, "wb") as f:
                f.write(response.read()) # 将内容写入图片
            return filename
    except:
        return "failed"


if __name__ == '__main__':
    dict_download_img('https://tvax3.sinaimg.cn/large/ec43126fgy1gwjqtn8f6bj229c38wnpk.jpg')