import random
import urllib
import requests

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont, ImageFilter
from plugins.RandomStr import random_str
lucky = [
    "——中吉——\n天上有云飘过的日子，天气令人十分舒畅。\n工作非常顺利，连午睡时也会想到好点子。\n突然发现，与老朋友还有其他的共同话题…\n——每一天，每一天都要积极开朗地度过——",
    "——中吉——\n十年磨一剑，今朝示霜刃。\n恶运已销，身临否极泰来之时。\n苦练多年未能一显身手的才能，\n现今有了大展身手的极好机会。\n若是遇到阻碍之事，亦不必迷惘，\n大胆地拔剑，痛快地战斗一番吧。",
    "——大吉——\n会起风的日子，无论干什么都会很顺利的一天。\n周围的人心情也非常愉快，绝对不会发生冲突，\n还可以吃到一直想吃，但没机会吃的美味佳肴。\n无论是工作，还是旅行，都一定会十分顺利吧。\n那么，应当在这样的好时辰里，一鼓作气前进…",
    "——大吉——\n宝剑出匣来，无往不利。出匣之光，亦能照亮他人。\n今日能一箭射中空中的猎物，能一击命中守卫要害。\n若没有目标，不妨四处转转，说不定会有意外之喜。\n同时，也不要忘记和倒霉的同伴分享一下好运气哦。",
    "——大吉——\n失而复得的一天。\n原本以为石沉大海的事情有了好的回应，\n原本分道扬镳的朋友或许可以再度和好，\n不经意间想起了原本已经忘记了的事情。\n世界上没有什么是永远无法挽回的，\n今天就是能够挽回失去事物的日子。",
    "——大吉——\n浮云散尽月当空，逢此签者皆为上吉。\n明镜在心清如许，所求之事心想则成。\n合适顺心而为的一天，不管是想做的事情，\n还是想见的人，现在是行动起来的好时机。",
    "——吉——\n明明没有什么特别的事情，却感到心情轻快的日子。\n在没注意过的角落可以找到本以为丢失已久的东西。\n食物比平时更加鲜美，路上的风景也令人眼前一亮。\n——这个世界上充满了新奇的美好事物——",
    "——吉——\n枯木逢春，正当万物复苏之时。\n陷入困境时，能得到解决办法。\n举棋不定时，会有贵人来相助。\n可以整顿一番心情，清理一番家装，\n说不定能发现意外之财。",
    "——吉——\n一如既往的一天。身体和心灵都适应了的日常。\n出现了能替代弄丢的东西的物品，令人很舒心。\n和常常遇见的人关系会变好，可能会成为朋友。\n——无论是多寻常的日子，都能成为宝贵的回忆——",
    "——末吉——\n云遮月半边，雾起更迷离。\n抬头即是浮云遮月，低头则是浓雾漫漫。\n虽然一时前路迷惘，但也会有一切明了的时刻。\n现下不如趁此机会磨炼自我，等待拨云见皎月。",
    "——末吉——\n空中的云层偏低，并且仍有堆积之势，\n不知何时雷雨会骤然从头顶倾盆而下。\n但是等雷雨过后，还会有彩虹在等着。\n宜循于旧，守于静，若妄为则难成之。",
    "——末吉——\n平稳安详的一天。没有什么令人难过的事情会发生。\n适合和久未联系的朋友聊聊过去的事情，一同欢笑。\n吃东西的时候会尝到很久以前体验过的过去的味道。\n——要珍惜身边的人与事——",
    "——末吉——\n气压稍微有点低，是会令人想到遥远的过去的日子。\n早已过往的年轻岁月，与再没联系过的故友的回忆，\n会让人感到一丝平淡的怀念，又稍微有一点点感伤。\n——偶尔怀念过去也很好。放松心情面对未来吧——",
    "——凶——\n珍惜的东西可能会遗失，需要小心。\n如果身体有不适，一定要注意休息。\n在做出决定之前，一定要再三思考。",
    "——凶——\n隐约感觉会下雨的一天。可能会遇到不顺心的事情。\n应该的褒奖迟迟没有到来，服务生也可能会上错菜。\n明明没什么大不了的事，却总感觉有些心烦的日子。\n——难免有这样的日子——",
    "——大凶——\n内心空落落的一天。可能会陷入深深的无力感之中。\n很多事情都无法理清头绪，过于钻牛角尖则易生病。\n虽然一切皆陷于低潮谷底中，但也不必因此而气馁。\n若能撑过一时困境，他日必另有一番作为。"
]

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
        if response.getcode() == 200:
            with open(filename, "wb") as f:
                f.write(response.read()) # 将内容写入图片
            return filename
    except:
        return "failed"
async def userAvatarDownLoad(url):
    fileName = dict_download_img(url, dirc="data/pictures/avatars")
    #logger.info("头像路径：" + fileName)
    touxiang = Image.open(fileName)
    fad = touxiang.resize((450, 450), Image.BICUBIC)
    fad.save(fileName)
    return fileName

async def check_image_size():
    try:
        #logger.info("获取签到背景图片")
        image_path = pic()

        return image_path
    except Exception as e:
        image_path = "data/pictures/new_sign_Image/9bFIzYz.png"
        return image_path

async def signPicMaker(url, ids, weather, nowTime, times, exp, startTime):
    # Load the background image
    bg_path = await check_image_size()
    bg = Image.open(bg_path)

    # Apply blur to the entire background image
    blurred_bg = bg.filter(ImageFilter.GaussianBlur(7))
    margin = 50
    # 创建一个新的内部清晰部分图像，根据原始宽高比计算新尺寸
    # 首先计算缩放比例，确保宽度和高度都不会超过背景的一半减去边距
    scale_factor = min((bg.width // 1.6 - margin) / bg.width, (bg.height - margin) / bg.height)
    new_width = int(bg.width * scale_factor)
    new_height = int(bg.height * scale_factor)

    # 使用LANCZOS采样方法进行调整大小，并保持原有宽高比
    inner_clear = bg.resize((new_width, new_height), resample=Image.LANCZOS)

    # 计算内部图片的粘贴位置，确保它居中于背景的一边
    paste_x = (bg.width - new_width - int(bg.width * 0.05))
    paste_y = ((bg.height - new_height) // 2) - int(bg.height * 0.05)
    # 使用LANCZOS采样方法进行调整大小

    # 创建一个灰色的矩形填充区域
    gray_color = (169, 169, 169, 40)  # 灰色，128为半透明的alpha值
    draw = ImageDraw.Draw(blurred_bg, 'RGBA')
    left_fill_width = bg.width // 3  # 你可以调整这个宽度
    # 绘制一个半透明的灰色矩形
    draw.rectangle([(0, 0), (left_fill_width, bg.height)], fill=gray_color)

    # Prepare shadow effect
    shadow_width = 10  # Shadow width
    shadow_color = (0, 0, 0, 80)  # Shadow color and transparency
    # Create a shadow image that is larger than the inner clear part to accommodate the shadow
    shadow_image = Image.new('RGBA', (new_width + shadow_width * 2, new_height + shadow_width * 2), shadow_color)
    # Blur the shadow image to create the shadow effect
    shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(shadow_width / 2))

    # Calculate position to paste the shadow
    shadow_x = paste_x - shadow_width
    shadow_y = paste_y - shadow_width

    # Paste the shadow onto the blurred background
    # 使用阴影的透明度通道作为掩码
    blurred_bg.paste(shadow_blurred, (shadow_x, shadow_y), shadow_blurred.split()[3])

    # Paste the inner clear part onto the blurred background with the shadow
    # 如果inner_clear是RGBA模式，使用它的透明度通道作为掩码
    if inner_clear.mode == 'RGBA':
        mask = inner_clear.split()[3]
    else:
        mask = None
    blurred_bg.paste(inner_clear, (paste_x, paste_y), mask)
    # 接下来开始增加图片
    fileName = await userAvatarDownLoad(url)
    # 制底图
    layer = Image.open(fileName)
    layer = layer.resize((int(bg.width * 0.1), int(bg.width * 0.1)), resample=Image.LANCZOS)
    blurred_bg.paste(layer, (int(bg.width * 0.02), int(bg.width * 0.02)))
    tp = blurred_bg
    draw = ImageDraw.Draw(tp)
    wi = int(bg.width * 0.02)
    font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', int(bg.width * 0.02))
    draw.text((wi, int(bg.height * 0.25)), (ids.replace("-", "a")), (12, 0, 6), font=font)
    font = ImageFont.truetype('data/fonts/zpix.ttf', int(bg.width * 0.015))
    draw.text((wi, int(bg.height * 0.35)), "天气：" + weather, (12, 0, 6), font=font)
    draw.text((wi, int(bg.height * 0.45)), "当前时间：" + nowTime, (12, 0, 6), font=font)
    draw.text((wi, int(bg.height * 0.55)), "签到次数：" + times, (12, 0, 6), font=font)
    draw.text((wi, int(bg.height * 0.65)), "注册日：" + startTime, (12, 0, 6), font=font)
    font = ImageFont.truetype('data/fonts/zpix.ttf', int(bg.width * 0.013))
    draw.text((int(bg.width * 0.015), int(bg.height * 0.75)), random.choice(lucky), (12, 3, 6), font=font)
    # Save the final image
    final_image_path = "data/pictures/cache/" + random_str() + ".png"
    blurred_bg.save(final_image_path)

    return final_image_path

def pic():
    ranpath = random_str()
    try:
        url = "https://api.iw233.cn/api.php?sort=pc"
        # url+="tag=萝莉|少女&tag=白丝|黑丝"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
            "Referer": "https://weibo.com/"}
        r = requests.get(url, headers=headers).content
        with open("data/pictures/new_sign_Image/" + ranpath + ".png", mode="wb") as f:
            f.write(r)  # 图片内容写入文件
        image_path = "data/pictures/new_sign_Image/" + ranpath + ".png"
        layer = Image.open(image_path)
        layer = layer.resize((1920, 1080), resample=Image.LANCZOS)
        layer.save(image_path)
        return "data/pictures/new_sign_Image/" + ranpath + ".png"
    except Exception as e:
        pass
        #logger.error(e)
        #logger.info("使用二号接口")
    try:
        url = "https://t.mwm.moe/pc"
        # url+="tag=萝莉|少女&tag=白丝|黑丝"
        r = requests.get(url).content
        with open("data/pictures/new_sign_Image/" + ranpath + ".png", mode="wb") as f:
            f.write(r)  # 图片内容写入文件
        image_path = "data/pictures/new_sign_Image/" + ranpath + ".png"
        layer = Image.open(image_path)
        layer = layer.resize((1920, 1080), resample=Image.LANCZOS)
        layer.save(image_path)
        return "data/pictures/new_sign_Image/" + ranpath + ".png"
    except Exception as e:
        pass
    try:
        url = 'https://api.yimian.xyz/img'
        params = {
            'type': 'moe',
            'size': '1920x1080'
        }
        res = requests.get(url, params=params)
        r = requests.get(res.url).content
        with open("data/pictures/new_sign_Image/" + ranpath + ".png", mode="wb") as f:
            f.write(r)  # 图片内容写入文件
        image_path = "data/pictures/new_sign_Image/" + ranpath + ".png"
        layer = Image.open(image_path)
        layer = layer.resize((1920, 1080), resample=Image.LANCZOS)
        layer.save(image_path)
        return "data/pictures/new_sign_Image/" + ranpath + ".png"
    except Exception as e:
        image_path = "data/pictures/new_sign_Image/9bFIzYz.png"
        return image_path

def get_user_image_url(qqid):
    return f'https://q4.qlogo.cn/g?b=qq&nk={qqid}&s=640'

if __name__ == '__main__':
    dict_download_img('https://tvax3.sinaimg.cn/large/ec43126fgy1gwjqtn8f6bj229c38wnpk.jpg')