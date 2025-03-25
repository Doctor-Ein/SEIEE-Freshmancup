from spilt_chapters import split_chapters
import json

# 读取文本文件
filename = './data.txt'
with open(filename, 'r', encoding='utf-8') as file:
    text = file.read()

# 分割章节
chapters = split_chapters(text)

# 将结果字典转换为JSON格式
json_data = json.dumps(chapters, ensure_ascii=False, indent=4)

# 将JSON数据写入文件
output_filename = './chapters.json'
with open(output_filename, 'w', encoding='utf-8') as output_file:
    output_file.write(json_data)

print(f"章节数据已保存到 {output_filename}")