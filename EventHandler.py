import BW
import concurrent.futures
import PromptEngine
import threading
from concurrent.futures import ThreadPoolExecutor
from TextInputApp import app
from PromptLab import promptlab

class TextHandler():
    text = promptlab["Mode1-B-1"]

    def __init__(self,bedrock_wrapper):
        self.bedrock_wrapper = bedrock_wrapper

def Mode1_PromptEngine():
    handler = TextHandler(BW.BedrockWrapper())
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            input_text = '\nQuestion: ' + app.get_input()
            prompt = PromptEngine.AutoPromptRAG(input_text)
            BW.printer(f'\n[INFO] prompt: {prompt}', 'info')
            request_text = TextHandler.text
            if len(input_text) != 0:
                request_text += input_text      # 这里前面就可以加载提示词了
                request_text += prompt          # 添加补充的知识点
                BW.printer(f'\n[INFO] request_text: {request_text}', 'info')

                # 将bedrock委托给线程池来处理，使用线程池异步调用 invoke_bedrock
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(handler.bedrock_wrapper.invoke_bedrock,request_text,mode = 1)
            TextHandler.text = promptlab["Mode1-B-2"]

def Mode2_RAG():
    return

def Mode3_Memory():
    return

def Mode4_MultiModal():
    return

def Mode5_MultiLanguage():
    return

switcher ={
        "1":Mode1_PromptEngine,
        "2":Mode2_RAG,
        "3":Mode3_Memory,
        "4":Mode4_MultiModal,
        "5":Mode5_MultiLanguage
    }

def ModeSelect_Script():
    app.put_output("[Mode Select]:选择展示的模块（输入数字选择）")
    app.put_output("1. 提示词工程")
    app.put_output("2. RAG")
    app.put_output("3. 上下文记忆")
    app.put_output("4. 多模态")
    app.put_output("5. 多语言") # 主要是为了语音部分
    mode = app.get_input()
    app.put_output("[Mode1]:提示词工程\n")
    switcher[mode]() # 接下来就是直接调用

if __name__ == "__main__":
    BW.printInfo()
    thread = threading.Thread(target=ModeSelect_Script,daemon=True).start()
    app.root.mainloop()
    app._append_output(">?<")
    app.root.after(0,app.put_output,"[ModeSelect]:\n")
    app.get_input()