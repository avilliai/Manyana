import asyncio

import httpx


async def screenshot_to_pdf_and_png(url, path, width=1024, height=9680):
    url = f"https://mini.s-shot.ru/{width}x{height}/PNG/1800/?{url}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    ''' 参数：网址
        功能: 保存网址截图
             解决了截图不全问题
             解决了懒加载问题
             保存俩种图片格式
    '''

    '''driver = webdriver.Firefox()
    # 6> 模仿手动滑动滚动条，解决懒加载问题
    try:
        driver.implicitly_wait(1)
        driver.get(link)

        # 模拟人滚动滚动条,处理图片懒加载问题
        js_height = "return document.body.clientHeight"
        driver.get(link)
        k = 1
        height = driver.execute_script(js_height)
        while True:
            if k * 500 < height:
                js_move = "window.scrollTo(0,{})".format(k * 500)
                #print(js_move)
                driver.execute_script(js_move)
                await sleep(0.2)
                height = driver.execute_script(js_height)
                k += 1
            else:
                break

        await sleep(1)

        # 7>  # 直接截图截不全，调取最大网页截图
        width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        #print(width, height)
        # 将浏览器的宽高设置成刚刚获取的宽高
        driver.set_window_size(width + 100, height + 100)
        await sleep(waitT)
        png_path = path

        # 截图并关掉浏览器
        driver.save_screenshot(png_path)
        driver.close()
        # png转pdf
        #image1 = Image.open(png_path)
        #im1 = image1.convert('RGB')
        #pdf_path = png_path.replace('.png', '.pdf')
        #im1.save(pdf_path)
        return png_path

    except Exception as e:
        print(e)'''


async def webScreenShot(url, path):
    url = f"https://mini.s-shot.ru/1080x980/PNG/2024/?{url}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)


if __name__ == '__main__':
    asyncio.run(webScreenShot("https://prts.wiki/w/波登可", "./test.png"))
    #asyncio.run(screenshot_to_pdf_and_png("https://prts.wiki/w/斯卡蒂", "./test.png"))

    #webScreenShoot("https://prts.wiki/w/w","test.png",1200,7500)
