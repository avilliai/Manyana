import asyncio


from PicImageSearch import Network, TraceMoe, Ascii2D, Iqdb, Google, EHentai
from PicImageSearch.model import Ascii2DResponse, IqdbResponse, TraceMoeResponse, GoogleResponse, EHentaiResponse




proxies = "http://127.0.0.1:1080"
#proxies = None
url = 'https://i.pixiv.re/img-master/img/2023/06/22/18/18/45/109241038_p0_master1200.jpg'


async def test(url,proxies):
    async with Network(proxies=proxies) as client:
        tracemoe = TraceMoe(client=client, mute=False, size=None)
        resp = await tracemoe.search(url=url)
        #resp = await tracemoe.search(file=file)
        sf="相似度："+str(resp.raw[0].similarity)+"\n名称："+str(resp.raw[0].title_romaji)+"/"+str(resp.raw[0].title_english)+"/"+str(resp.raw[0].title_chinese)+"\n源文件："+str(resp.raw[0].filename)+"\n链接1："+str(resp.raw[0].image)+"\n链接2:"+str(resp.raw[0].video)
        #返回数据与封面
        return sf,str(resp.raw[0].cover_image)
async def test1(url,proxies):
    bovw = False  # 是否使用特征检索
    verify_ssl = True  # 是否校验 SSL 证书
    async with Network(proxies=proxies,verify_ssl=verify_ssl) as client:
        ascii2d = Ascii2D(client=client, bovw=bovw)
        resp = await ascii2d.search(url=url)
        #resp = await ascii2d.search(file=file)
        #show_result(resp)
        selected = next((i for i in resp.raw if i.title or i.url_list), resp.raw[0])
        # logger.info(selected.origin)
        #print("================")
        fs="标题："+str(selected.title)+"\n作者:"+str(selected.author)+"\n作者链接:"+str(selected.author_url)+"\n作品页:"+str(selected.url)
        #print(fs)
        return fs,selected.thumbnail


async def superSearch(url,proxies):
    async with Network(proxies=proxies) as client:
        iqdb = Iqdb(client=client)
        resp = await iqdb.search(url=url)
        #resp = await iqdb.search(file=file)
        fs=f"模式: {resp.raw[0].content}"+"\n"+f"来源地址: {resp.raw[0].url}"+"\n"+f"相似度: {resp.raw[0].similarity}"+"\n"+f"图片大小: {resp.raw[0].size}"+"\n"+f"图片来源: {resp.raw[0].source}"+"\n"+f"其他图片来源: {resp.raw[0].other_source}"+"\n"+f"SauceNAO搜图链接: {resp.saucenao_url}"+"\n"+f"Ascii2d搜图链接: {resp.ascii2d_url}"+"\n"+f"TinEye搜图链接: {resp.tineye_url}"+"\n"+f"Google搜图链接: {resp.google_url}"
        #print(fs)
        return fs,str(resp.raw[0].thumbnail)

async def test2(url,proxies,cookies):
    #cookies = 'ipb_session_id=bc4e5da825b5ad5325688bd5d6d5c21d; ipb_member_id=7584785; ipb_pass_hash=8e9aa8e90a14b059ba8ee70075120c17; sk=mua8zab26lmwo63gkcydsht8kslv'  # 注意：如果要使用 EXHentai 搜索，需要提供 cookies
    #cookies='ipb_member_id=7584785; ipb_pass_hash=8e9aa8e90a14b059ba8ee70075120c17; ipb_coppa=0; sk=mua8zab26lmwo63gkcydsht8kslv; ipb_session_id=538204ee280a418b7caa0a089a673f56'
    ex = True  # 是否使用 EXHentai 搜索，推荐用 bool(cookies) ，即配置了 cookies 就使用 EXHentai 搜索
    timeout = 60  # 尽可能避免超时返回空的 document
    async with Network(proxies=proxies, cookies=cookies, timeout=timeout) as client:
        ehentai = EHentai(client=client)
        resp = await ehentai.search(url=url, ex=ex)
        #resp = await ehentai.search(file=file, ex=ex)

    fs="标题："+str(resp.raw[0].title)+"\n"+"链接："+str(resp.raw[0].url)+"分类："+str(resp.raw[0].type)+"\n日期："+str(resp.raw[0].date)
    print(fs)
    return fs,resp.raw[0].thumbnail





if __name__ == "__main__":
    asyncio.run(test2())

