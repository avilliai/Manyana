import re


def wontrep(noeRes1, text, logger):
    p1 = noeRes1.get("noResMatch")
    text = text.replace("壁纸", "").replace("涩图", "").replace("色图", "").replace("图",
                                                                                    "").replace(
        "r18", "")
    for i in p1:
        if text == i:
            logger.warning(f"与屏蔽词 {i} 匹配，不回复")
            return False
    p2 = noeRes1.get("startswith")
    for i in p2:
        if str(text).startswith(i):
            logger.warning(f"与屏蔽词 {i} 匹配，不回复")
            return False
    p2 = noeRes1.get("endswith")
    for i in p2:
        if str(text).endswith(i):
            logger.warning(f"与屏蔽词 {i} 匹配，不回复")
            return False
    p2 = noeRes1.get("Regular")
    for i in p2:
        match1 = re.search(i, text)
        if match1:
            logger.warning(f"与表达式 {i} 匹配，不回复")
            return False
    return True
