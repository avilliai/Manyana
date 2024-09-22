import os
import random
import platform

import psutil
import requests
import yaml
import logging
import httpx
import colorlog
from io import BytesIO
from PIL import Image

try:
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        apiYaml = yaml.load(f.read(), Loader=yaml.FullLoader)
    from lanzou.api import LanZouCloud
    lzy = LanZouCloud()
    cookie = {'ylogin': str(apiYaml.get("蓝奏云").get("ylogin")), 'phpdisk_info': apiYaml.get("蓝奏云").get("phpdisk_info")}
    code=lzy.login_by_cookie(cookie)
except:
    print("无效的蓝奏云登录操作")
def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers
def fileToUrl(file_path,proxy):
    url = "https://file.io"
    files = {"file": open(file_path, "rb")}
    if proxy=="" or proxy==" " or proxy==None:
        response = requests.post(url, files=files,headers=get_headers())
    else:
        proxies = {
            "http://": proxy,
            "https://": proxy
        }
        response = requests.post(url, files=files,proxies=proxies,headers=get_headers())
    data = response.json()
    return data.get("link")
def lanzouFileToUrl(path):
    url=""
    def show_progress(file_name, total_size, now_size):
        percent = now_size / total_size
        bar_len = 40  # 进度条长总度
        bar_str = '>' * round(bar_len * percent) + '=' * round(bar_len * (1 - percent))
        print('\r{:.2f}%\t[{}] {:.1f}/{:.1f}MB | {} '.format(
            percent * 100, bar_str, now_size / 1048576, total_size / 1048576, file_name), end='')
        if total_size == now_size:
            print('')  # 下载完成换行

    def handler(fid, is_file):
        nonlocal url  # 声明要修改外部函数的url变量
        r=lzy.get_durl_by_id(fid)
        url=r.durl
    lzy.upload_file(path, -1, callback=show_progress,uploaded_handler=handler)
    return url
async def translate(text, mode="ZH_CN2JA"):
    try:
        URL = f"https://api.pearktrue.cn/api/translate/?text={text}&type={mode}"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(URL)
            #print(r.json()["data"]["translate"])
            return r.json()["data"]["translate"]
    except:
        print("文本翻译接口1失效")
        if mode != "ZH_CN2JA":
            return text
    try:
        url = f"https://findmyip.net/api/translate.php?text={text}&target_lang=ja"
        r = requests.get(url=url, timeout=10)
        return r.json()["data"]["translate_result"]
    except:
        print("翻译接口2调用失败")
    try:
        url = f"https://translate.appworlds.cn?text={text}&from=zh-CN&to=ja"
        r = requests.get(url=url, timeout=10, verify=False)
        return r.json()["data"]
    except:
        print("翻译接口3调用失败")
    return text
def random_str(random_length=7, chars='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789@$#_%'):
    """
    生成随机字符串作为验证码
    :param random_length: 字符串长度,默认为6
    :return: 随机字符串
    """
    string = ''

    length = len(chars) - 1
    # random = Random()
    # 设置循环每次取一个字符用来生成随机数
    for i in range(random_length):
        string += (chars[random.randint(0, length)])
    return string
def random_session_hash(random_length):
    # 给gradio一类的api用，生成随机session_hash,避免多任务撞车导致推理出错。这里偷懒套个娃（bushi
    return random_str(random_length, "abcdefghijklmnopqrstuvwxyz1234567890")
def createLogger():
    # 创建一个logger对象
    logger = logging.getLogger("Manayana")
    # 设置日志级别为DEBUG，这样可以输出所有级别的日志
    logger.setLevel(logging.DEBUG)
    # 创建一个StreamHandler对象，用于输出日志到控制台
    console_handler = logging.StreamHandler()
    # 设置控制台输出的日志格式和颜色
    logger.propagate = False
    console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_colors = {
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
    console_handler.setFormatter(console_formatter)
    # 将控制台处理器添加到logger对象中
    logger.addHandler(console_handler)
    # 使用不同级别的方法来记录不同重要性的事件
    '''logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')'''
    return logger
logger=createLogger()
def newLogger():
    return logger
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


# 定义一个函数，获取并返回系统信息
def get_system_info():
    # 创建一个空列表，用于存储系统信息
    system_info = ["=" * 6 + "System Info" + "=" * 6 + "\n"]
    # 获取系统信息
    uname = platform.uname()
    system_info.append(f"System: {uname.system}\n")
    system_info.append(f"Node Name: {uname.node}\n")
    system_info.append(f"Release: {uname.release}\n")
    system_info.append(f"Version: {uname.version}\n")
    system_info.append(f"Machine: {uname.machine}\n")
    system_info.append(f"Processor: {uname.processor}\n")
    # 获取CPU信息
    system_info.append("=" * 6 + "CPU Info" + "=" * 6 + "\n")
    # 核心数
    system_info.append(f"Physical cores: {psutil.cpu_count(logical=False)}\n")
    system_info.append(f"Total cores: {psutil.cpu_count(logical=True)}\n")
    # CPU频率
    cpufreq = psutil.cpu_freq()
    system_info.append(f"Max Frequency: {cpufreq.max:.2f}Mhz\n")
    system_info.append(f"Min Frequency: {cpufreq.min:.2f}Mhz\n")
    system_info.append(f"Current Frequency: {cpufreq.current:.2f}Mhz\n")
    # CPU使用率
    system_info.append("CPU Usage Per Core:\n")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        system_info.append(f"Core {i}: {percentage}%\n")
    system_info.append(f"Total CPU Usage: {psutil.cpu_percent()}%\n")
    '''# CPU温度
    system_info.append("CPU Temperature:")
    sensors_temperatures = psutil.sensors_temperatures()
    for name, entries in sensors_temperatures.items():
        system_info.append(f"{name}:")
        for entry in entries:
            system_info.append(f"    {entry.label or 'N/A'}: {entry.current}°C")'''
    # 获取内存信息
    system_info.append("=" * 6 + "Memory Info" + "=" * 6 + "\n")
    # 获取内存总量，使用量，空闲量和使用百分比
    svmem = psutil.virtual_memory()
    system_info.append(f"Total: {get_size(svmem.total)}\n")
    system_info.append(f"Available: {get_size(svmem.available)}\n")
    system_info.append(f"Used: {get_size(svmem.used)}\n")
    system_info.append(f"Percentage: {svmem.percent}%\n")
    # 获取当前网络接口的IO统计
    system_info.append("=" * 6 + "NetWork IO" + "=" * 6 + "\n")
    net_io = psutil.net_io_counters()
    system_info.append(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}\n")
    system_info.append(f"Total Bytes Received: {get_size(net_io.bytes_recv)}\n")
    # 获取硬盘信息
    system_info.append("=" * 6 + "Disk Info" + "=" * 6 + "\n")
    system_info.append(f"=== Disk IO===\n")
    disk_io = psutil.disk_io_counters()
    system_info.append(f"Total read: {get_size(disk_io.read_bytes)}\n")
    system_info.append(f"Total write: {get_size(disk_io.write_bytes)}\n")
    # 获取网络信息
    '''system_info.append("="*6 + "Network Information" + "="*6)
    # 获取所有网络接口的详细信息
    system_info.append("All network interfaces and their details:")
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            system_info.append(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                system_info.append(f"  IP Address: {address.address}")
                system_info.append(f"  Netmask: {address.netmask}")
                system_info.append(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                system_info.append(f"  MAC Address: {address.address}")
                system_info.append(f"  Netmask: {address.netmask}")
                system_info.append(f"  Broadcast MAC: {address.broadcast}")'''

    # 获取硬盘分区和使用情况
    system_info.append("Partitions and Usage:\n")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        system_info.append(f"=== Device: {partition.device} ===\n")
        system_info.append(f"  Mountpoint: {partition.mountpoint}\n")
        system_info.append(f"  File system type: {partition.fstype}\n")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # 这可能是由于没有访问权限造成的
            continue
        system_info.append(f"  Total Size: {get_size(partition_usage.total)}\n")
        system_info.append(f"  Used: {get_size(partition_usage.used)}\n")
        system_info.append(f"  Free: {get_size(partition_usage.free)}\n")
        system_info.append(f"  Percentage: {partition_usage.percent}%\n")
    # 获取硬盘总的IO统计

    # 返回系统信息列表
    return system_info
async def screenshot_to_pdf_and_png(url, path, width=1024, height=9680):
    url = f"https://mini.s-shot.ru/{width}x{height}/PNG/1800/?{url}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        return path

async def webScreenShot(url, path):
    url = f"https://mini.s-shot.ru/1080x980/PNG/2024/?{url}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
async def picDwn(url, path):
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        return path
