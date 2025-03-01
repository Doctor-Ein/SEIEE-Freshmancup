import json

class PromptTemplate:
    def __init__(self, role, background, objective, instruction, response, workflow, examples, history):
        self.role = role  # 角色，可以加一些形容词
        self.background = background  # 背景，和角色紧密联系
        self.objective = objective  # 目标
        self.instruction = instruction  # 指令
        self.response = response  # 响应格式
        self.workflow = workflow  # 工作流，用于指导模型的思考链
        self.examples = examples  # 例子的列表
        self.history = history  # 对话的历史，以 Q，A 对应的字典

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["role"],
            data["background"],
            data["objective"],
            data["instruction"],
            data["response"],
            data["workflow"],
            data["examples"],
            data["history"]
        )

    def to_dict(self):
        return {
            "role": self.role,
            "background": self.background,
            "objective": self.objective,
            "instruction": self.instruction,
            "response": self.response,
            "workflow": self.workflow,
            "examples": self.examples,
            "history": self.history
        }

class PromptEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PromptTemplate):
            return o.to_dict()
        return super().default(o)

class PromptDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dict_data):
        if "role" in dict_data:
            return PromptTemplate.from_dict(dict_data)
        return dict_data

def save_prompt_template_to_json(prompt_template: PromptTemplate, json_file_path: str):
    """
    将 PromptTemplate 对象保存到 JSON 文件，支持中文编码。
    """
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(prompt_template, f, cls=PromptEncoder, indent=4, ensure_ascii=False)

def load_prompt_template_from_json(json_file_path: str) -> PromptTemplate:
    """
    从 JSON 文件中加载 PromptTemplate 对象。
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        loaded_prompt_template = json.load(f, cls=PromptDecoder)
    return loaded_prompt_template