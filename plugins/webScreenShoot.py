from selenium import webdriver
def webScreenShoot(url,path,width=1200,height=7500):
    browser = webdriver.Firefox()
    url = url
    browser.set_window_size(width,height)
    browser.get(url)

    browser.save_screenshot(path)
    browser.close()
if __name__ == '__main__':

    webScreenShoot("https://wiki.biligame.com/zspms/21%E5%8F%B7%C2%B7XXI","test.png",1200,5800)