from selenium import webdriver
def webScreenShoot(url,path,width=1200,height=7500):

    driverfile_path = r'plugins/msedgedriver.exe'


    browser = webdriver.Edge(executable_path=driverfile_path)
    url = url
    browser.set_window_size(width,height)
    browser.get(url)

    browser.save_screenshot(path)
    browser.close()
