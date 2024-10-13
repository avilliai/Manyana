import asyncio
from typing import Optional, Tuple, List, Dict, Any

from loguru import logger

from PicImageSearch import Ascii2D, Network, BaiDu, Copyseeker, Google, Iqdb, SauceNAO, Yandex
from PicImageSearch.model import Ascii2DResponse, BaiDuResponse, CopyseekerResponse, GoogleResponse, IqdbResponse, \
    SauceNAOResponse, YandexResponse
from PicImageSearch.sync import Ascii2D as Ascii2DSync
from PicImageSearch.sync import BaiDu as BaiDuSync


# proxies =
#proxies = "http://127.0.0.1:10809"

#url = "https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=CgoxODQwMDk0OTcyEhRIG9o5t_uwgsEQUyL4lGRnEDZCVhjlig4g_woo24jQxMuKiQMyBHByb2RQgL2jAQ&spec=0&rkey=CAESKBkcro_MGujoBSDPSkH77WdNctk4U08YL50QmBMLw88CPMwNfXTXTmw"
bovw = False  # Use feature search or not
verify_ssl = True  # Whether to verify SSL certificates or not
async def ascii2d_async(proxies,url):
    base_url = "https://ascii2d.net"
    async with Network(proxies=proxies, verify_ssl=verify_ssl) as client:
        ascii2d = Ascii2D(base_url=base_url, client=client, bovw=bovw)
        resp = await ascii2d.search(url=url)
        selected = next((i for i in resp.raw if i.title or i.url_list), resp.raw[0])
        return [resp.raw[0].thumbnail, f"标题：{selected.title}\n作者：{selected.author}\n{selected.author_url}\n链接：{selected.url}"]

async def baidu_async(proxies,url):
    async with Network(proxies=proxies) as client:
        baidu = BaiDu(client=client)
        resp = await baidu.search(url=url)
        #resp = await baidu.search(file=file)
        return [resp.raw[0].thumbnail, f"相关链接：{resp.raw[0].title}\n 百度识图：{resp.url}"]

async def Copyseeker_async(proxies,url):
    async with Network(proxies=proxies) as client:
        copyseeker = Copyseeker(client=client)
        resp = await copyseeker.search(url=url)
        #resp = await copyseeker.search(file=file)
        if resp.raw:
            return [resp.raw[0].thumbnail, f"相关链接：{resp.raw[0].url}\n 来源：{resp.raw[0].title}"]
    # logger.info(resp.visuallySimilarImages)
async def google_async(proxies,url):
    base_url = "https://www.google.co.jp"
    async with Network(proxies=proxies) as client:
        google = Google(client=client, base_url=base_url)
        resp = await google.search(url=url)
        #resp = await google.search(file=file)
        if resp:
            selected = next((i for i in resp.raw if i.thumbnail), resp.raw[0])
            return [selected.thumbnail, f"标题：{selected.title}\n 来源：{selected.url}"]

async def iqdb_async(proxies,url):
    async with Network(proxies=proxies) as client:
        iqdb = Iqdb(client=client)
        resp = await iqdb.search(url=url)
        #resp = await iqdb.search(file=file)
        return [resp.raw[0].thumbnail,f"相似度：{resp.raw[0].similarity}\niqdb\n 图片来源：{resp.raw[0].url}\n 其他图片来源：{resp.raw[0].other_source}\nSauceNAO Search Link: {resp.saucenao_url}\nAscii2d Search Link: {resp.ascii2d_url}\nTinEye Search Link: {resp.tineye_url}\nGoogle Search Link: {resp.google_url}\nNumber of Results with Lower Similarity: {len(resp.more)}"]

async def iqdb3D_async(proxies,url):
    async with Network(proxies=proxies) as client:
        iqdb = Iqdb(client=client, is_3d=True)
        resp = await iqdb.search(url=url)
        #resp = await iqdb.search(file=file)
        return [resp.raw[0].thumbnail,f"相似度：{resp.raw[0].similarity},\n源网站搜索：{resp.raw[0].content}\n图片来源：{resp.raw[0].url}"]


async def saucenao_async(proxies,url,api_key):
    async with Network(proxies=proxies) as client:
        saucenao = SauceNAO(client=client, api_key=api_key, hide=3)
        resp = await saucenao.search(url=url)
        #resp = await saucenao.search(file=file)
        return [resp.raw[0].thumbnail,f"相似度{resp.raw[0].similarity}\n标题：{resp.raw[0].title}\n作者：{resp.raw[0].author}\n{resp.raw[0].author_url}\n图片来源：{resp.raw[0].url}\n{resp.raw[0].source}"]
async def yandex_async(proxies,url):
    async with Network(proxies=proxies) as client:
        yandex = Yandex(client=client)
        resp = await yandex.search(url=url)
        #resp = await yandex.search(file=file)
        return [resp.raw[0].thumbnail,f"\n标题：{resp.raw[0].title}\n图片来源：{resp.raw[0].url}\n{resp.raw[0].source}"]






async def fetch_results(proxies: str, url: str,sauceno_api:str) -> Dict[str, Optional[List[Any]]]:
    async def _safe_call(func, *args, **kwargs) -> Tuple[str, Optional[List[Any]]]:
        try:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=60)
            return func.__name__, result
        except asyncio.TimeoutError:
            logger.warning(f"{func.__name__} 超时")
            return func.__name__, None
        except Exception as e:
            logger.error(f"{func.__name__} 出现错误: {e}")
            return func.__name__, None

    # 定义所有要并发执行的任务
    tasks = [
        _safe_call(ascii2d_async, proxies, url),
        _safe_call(baidu_async, proxies, url),
        _safe_call(Copyseeker_async, proxies, url),
        _safe_call(google_async, proxies, url),
        _safe_call(iqdb_async, proxies, url),
        _safe_call(iqdb3D_async, proxies, url),
        _safe_call(saucenao_async, proxies, url, sauceno_api),  # 替换为你的 API key
        _safe_call(yandex_async, proxies, url),
    ]

    # 并发执行所有任务并获取结果
    results = await asyncio.gather(*tasks)

    # 转换为字典形式，方便查看各任务结果
    return {name: result for name, result in results}

