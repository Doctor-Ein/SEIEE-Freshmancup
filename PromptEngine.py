from knowledge_base import Knowledges as Ks

tags = ["数据结构","数组","链表","栈","队列","储存结构","场景"]

def ScreenLabels(user_input:str): #从输入的文本中直接字符串匹配，获得目标labels
    labels = []
    for tag in tags:
        if tag in user_input:
            labels.append(tag)
    return labels

def ScreenItem(labels:list): # 以目标labels筛选合适的
    res = []
    for item in Ks:
        for tag in item["label"]:
            if tag in labels:
                res.append(item)
    return res

def item2prompt(res:list):
    prompt = "\n<Konwledge>\n"
    for item in res:
        prompt += "input:"+str(item["input"])+":\t"
        prompt += "output:"+str(item["output"])+"\n"
    prompt+= "</Knowledge>\n"
    return prompt

def AutoPromptRAG(user_input:str):
    labels = ScreenLabels(user_input)
    res = ScreenItem(labels)
    prompt = item2prompt(res)
    return prompt



if __name__ == "__main__":
    user_input = "什么是数据结构中的储存结构，它有什么样的应用场景"
    print(AutoPromptRAG(user_input)) # 离谱嵌套调用

# import json

# class Knowledge:
#     def __init__(self, input_str, output_str, label):
#         self.input = input_str
#         self.output = output_str
#         self.label = label

#     @classmethod
#     def from_dict(cls, data):
#         return cls(
#             data["input"],
#             data["output"],
#             data["label"]
#         )

#     def to_dict(self):
#         return {
#             "input": self.input,
#             "output": self.output,
#             "label": self.label
#         }

# class KnowledgeEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, Knowledge):
#             return o.to_dict()
#         return super().default(o)

# class KnowledgeDecoder(json.JSONDecoder):
#     def __init__(self, *args, **kwargs):
#         super().__init__(object_hook=self.object_hook, *args, **kwargs)

#     def object_hook(self, dict_data):
#         if "input" in dict_data and "output" in dict_data and "label" in dict_data:
#             return Knowledge.from_dict(dict_data)
#         return dict_data

# def save_knowledge_base_to_json(knowledge_base: list, json_file_path: str):
#     """
#     将 Knowledge 对象列表保存到 JSON 文件，支持中文编码。
#     """
#     with open(json_file_path, 'w', encoding='utf-8') as f:
#         json.dump(knowledge_base, f, cls=KnowledgeEncoder, indent=4, ensure_ascii=False)

# def load_knowledge_base_from_json(json_file_path: str) -> list:
#     """
#     从 JSON 文件中加载 Knowledge 对象列表。
#     """
#     with open(json_file_path, 'r', encoding='utf-8') as f:
#         loaded_knowledge_base = json.load(f, cls=KnowledgeDecoder)
#     return loaded_knowledge_base

# # 示例用法
# if __name__ == "__main__":
#     # 创建 Knowledge 对象列表
#     knowledge_base = [
#         Knowledge("什么是数据结构？", "数据结构是某一数据对象的所有数据成员之间的关系,记为:Data_Structure={D,S}。其中,D是某一数据对象,即数据元素的有限集合,S是该对象中所有数据成员之间的关系的有限集合。", ["数据结构"]),
#         Knowledge("链表的核心特点有哪些？", "链表通过指针域实现动态存储分配,分为单链表(单向遍历)、双向链表(双向遍历)和循环链表(首尾相连)三类型,支持O(1)时间复杂度的插入/删除操作。", ["链表"]),
#         Knowledge("队列与栈的本质区别是什么？", "队列遵循先进先出(FIFO)原则,栈遵循后进先出(LIFO)原则,二者操作受限的线性结构特性决定其应用场景差异。", ["栈", "队列"])
#     ]

#     # 保存到 JSON 文件
#     save_knowledge_base_to_json(knowledge_base, "knowledge_base.json")

#     # 从 JSON 文件加载
#     loaded_knowledge_base = load_knowledge_base_from_json("knowledge_base.json")

#     # 打印加载的数据
#     for knowledge in loaded_knowledge_base:
#         print(f"Input: {knowledge.input}")
#         print(f"Output: {knowledge.output}")
#         print(f"Label: {knowledge.label}")
#         print()