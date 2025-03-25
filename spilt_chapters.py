import re

def split_chapters(text):
    lines = text.split('\n')  # 将文本按行分割
    chapters = {}  # 初始化字典来保存章节标题和内容
    current_title = None  # 当前章节标题
    current_content = []  # 当前章节内容列表
    pattern = r"第.*?卷\(\d+--\d+章\)"  # 正则表达式模式

    for line in lines:
        line = line.strip()  # 去除行首尾的空白字符
        if re.match(pattern, line):  # 检查是否为新的章节标题
            if current_title:  # 如果已有章节标题，则保存当前章节内容
                chapters[current_title] = current_content  # 保存为原始格式
            current_title = line  # 更新当前章节标题
            current_content = []  # 重置当前章节内容列表
        else:
            current_content.append(line)  # 添加正文内容

    # 保存最后一个章节的内容
    if current_title:
        chapters[current_title] = current_content

    return chapters

if __name__ == "__main__":
    # 示例文本
    text = """
    第一卷(01--030章)第一回 甄士隐梦幻识通灵贾雨村风尘怀闺秀
        此开卷第一回也.作者自云:因曾历过一番梦幻之后,故将真事隐去...
    第二卷(031--060章)第二回 贾夫人仙逝扬州城冷子兴演说荣国府
        却说封肃因听见公差传唤...
    """

    # 分割章节
    chapters = split_chapters(text)

    # 打印结果
    for title, content in chapters.items():
        print(f"Chapter Title: {title}\nContent:\n{content}\n\n")