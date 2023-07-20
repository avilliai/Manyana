msg = "".join(map(str, event.message_chain[Plain]))
# 匹配指令
m = re.match(r'^查询\s*(\w+)\s*$', msg.strip())
if m:
    # 取出指令中的地名
    city = m.group(1)
