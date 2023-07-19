import re

# 定义一个正则表达式，匹配包含"壁纸"或者"图"或者"pic"和一个数字的字符串，并捕获数字
pattern = r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"

# 定义一个函数，使用正则表达式检查字符串是否符合条件，并提取数字
def get_number(string):
    # 使用re.match方法，返回匹配的结果对象
    match = re.match(pattern, string)
    # 如果结果对象不为空，返回捕获的数字，否则返回None
    if match:
        # 如果第二个分组有值，返回第二个分组，否则返回第三个分组
        if match.group(2):
            return match.group(2)
        else:
            return match.group(3)
    else:
        return None

# 测试一些字符串
strings = ["@1213342 6张壁纸", "/pic3", "三张图", "壁纸5", "pic5", "图5"]
for string in strings:
    print(get_number(string))
