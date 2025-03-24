import BW
import concurrent.futures
import PromptEngine
import threading
from concurrent.futures import ThreadPoolExecutor
from TextInputApp import app
from PromptLab import promptlab
import os.path


class TextHandler():
    text = ""
    def __init__(self,bedrock_wrapper):
        self.bedrock_wrapper = bedrock_wrapper

def Mode1_PromptEngine():
    app.put_output("[Mode1]:PromptEngine")
    handler = TextHandler(BW.BedrockWrapper())
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            input_text = '\nQuestion: ' + app.get_input()[0]
            prompt = PromptEngine.AutoPromptRAG(input_text)
            # BW.printer(f'\n[INFO] prompt: {prompt}', 'info')
            request_text = TextHandler.text
            if len(input_text) != 0:
                request_text += input_text      # 这里前面就可以加载提示词了
                request_text += prompt          # 添加补充的知识点
                BW.printer(f'\n[INFO] request_text: {request_text}', 'info')

                # 将bedrock委托给线程池来处理，使用线程池异步调用 invoke_bedrock
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(handler.bedrock_wrapper.invoke_bedrock,request_text)
            TextHandler.text = promptlab["Mode1-B-2"]

def Mode2_RAG():
    from RAG_Module.QueryEngine import queryContext

    app.put_output("[Mode2]:RAG")
    handler = TextHandler(BW.BedrockWrapper())
    handler.text = promptlab["Mode2-Debug-1"]
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            input_text = app.get_input()[0]
            context = queryContext(input_text)
            input_text = '\nQuestion: ' + input_text
            # BW.printer(f'\n[INFO] prompt: {context}', 'info')
            request_text = TextHandler.text
            if len(input_text) != 0:
                request_text += input_text      # 这里前面就可以加载提示词了
                request_text += ''.join(context)         # 添加补充的知识点
                BW.printer(f'\n[INFO] request_text: {request_text}', 'info')

                # 将bedrock委托给线程池来处理，使用线程池异步调用 invoke_bedrock
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(handler.bedrock_wrapper.invoke_bedrock,request_text)
            TextHandler.text = promptlab["Mode2-Debug-1"]

def Mode3_Memory():
    app.put_output("[Mode3]:Memory")

    data = []
    history = []
    handler = TextHandler(BW.BedrockWrapper())
    TextHandler.text = promptlab["Mode3-Debug-1"]
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            input_text = app.get_input()[0]
            if len(input_text) != 0:
                request_text = handler.text + input_text
                BW.printer(f'\n[INFO] request_text: {request_text}', 'info')
                return_output = handler.bedrock_wrapper.invoke_bedrock(request_text,data,history) ## 不能在异步调用了，插入的顺序都乱了呜
                # history.append({"role":"user","content":[{ "type": "text","text": input_text}]})
                history.append({"role":"assistant","content":[{ "type": "text","text": return_output}]})
                print('-' * 10 + 'Debug List' + '-' * 10)
                print(history)

def Mode4_MultiModal():
    from knowledge_base import math_problems
    import base64

    app.put_output("[Mode4]:MultiModal")
    handler = TextHandler(BW.BedrockWrapper())
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            info = app.get_input()
            input_text = info[0]
            files = info[1]
            if files:
                data = []
                for file in files:
                    with open(file, 'rb') as f:
                        data.append([base64.b64encode(f.read()).decode(),os.path.splitext(file)[1]])
                input_text += "在阅读以下例题及解答的基础上，仿照其思维模式，认真读取并解答图中呈现的数学问题，要求给出逐步的思考过程和结果，并且在验证你的答案后给出最终答案，图片中可能包含Latex公式。\n" + str(math_problems) 
                BW.printer(f'\n[INFO] input_text: {input_text}', 'info')
                BW.printer(f'\n[INFO] files: {files}', 'info')

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(handler.bedrock_wrapper.invoke_bedrock,input_text,data)
                TextHandler.text = ""

def Mode5_MultiLanguage():
    import app_MultiLanguage

    """
    让用户选择语言，并返回对应的索引。
    """    
    app.put_output("[Mode5]:MultiLanguage")
    app.put_output("Please select a language:")    
    for i, prompt in enumerate(app_MultiLanguage.voicePromptList):        
        app.put_output(f"{i}: {prompt}")        
    while True:        
        try:            
            choice = int(app.get_input()[0])  
            if 0 <= choice < len(app_MultiLanguage.voiceLanguageList):                
                app_MultiLanguage.voiceIndex = choice
                break
            else:                
                app.put_output("Invalid choice. Please try again.")        
        except ValueError:            
            app.put_output("Invalid input. Please enter a number.")
    app_MultiLanguage.update_config()
    app.put_output("[Status]:Config Update Correctly!")
    app.put_output(app_MultiLanguage.info_text)
    try:
        app_MultiLanguage.loop.run_until_complete(app_MultiLanguage.MicStream().basic_transcribe())
    except:
        print("Runtime Error!")

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
    mode = app.get_input()[0]
    switcher[mode]() # 接下来就是直接调用

if __name__ == "__main__":
    BW.printInfo()
    thread = threading.Thread(target=ModeSelect_Script,daemon=True).start()
    app.root.mainloop()
    app._append_output(">?<")
    app.root.after(0,app.put_output,"[ModeSelect]:\n")
    app.get_input()[0]
