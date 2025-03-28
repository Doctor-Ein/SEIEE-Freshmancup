import concurrent.futures
import threading
import os.path

from BedrockWrapper import BedrockWrapper_text
from TextInputApp import app # app 图形化输入输出窗口的控制对象
from PE_Package.PromptLab import promptlab # promptlab 存放调试的提示词


class TextHandler():
    text = ""
    def __init__(self,bedrock_wrapper):
        self.bedrock_wrapper = bedrock_wrapper

def Mode1_PromptEngine():
    import PE_Package.PromptEngine as PromptEngine # PromptEngine 搜索和处理知识库

    app.put_output("[Mode1]:PromptEngine")
    handler = TextHandler(BedrockWrapper_text.BedrockWrapper()) # 初始化文本处理器，负责调用模型
    TextHandler.text = promptlab["Mode1-B-2"] # TextHandler.text是预制的提示词

    while True:
        if not handler.bedrock_wrapper.is_speaking():
            input_text = '\nQuestion: ' + app.get_input()[0] # 阻塞式等待获取输入框的内容

            prompt = PromptEngine.AutoPromptRAG(input_text) # 使用提示词引擎

            request_text = TextHandler.text # request_text即是真实传递的调用文本 
            if len(input_text) != 0:
                request_text += input_text      # 连接输入的文本
                request_text += prompt          # 添加补充的知识点
                BedrockWrapper_text.printer(f'\n[INFO] request_text: {request_text}', 'info')

                # 将bedrock委托给线程池来处理，使用线程池异步调用 invoke_bedrock
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(handler.bedrock_wrapper.invoke_bedrock,request_text)

def Mode2_RAG():
    from RAG_Package.QueryEngine import queryContext
    
    app.put_output("[Mode2]:RAG")
    handler = TextHandler(BedrockWrapper_text.BedrockWrapper()) # 初始化文本处理器，负责调用模型
    handler.text = promptlab["Mode2-Debug-1"] # TextHandler.text是预制的提示词

    while True:
        if not handler.bedrock_wrapper.is_speaking():
            input_text = app.get_input()[0] # 阻塞式等待获取输入框的内容

            context = queryContext(input_text) # 使用queryContext，传入提问内容查询相关上下文

            request_text = TextHandler.text # request_text即是真实传递的调用文本 
            if len(input_text) != 0:
                request_text += input_text 
                request_text += ''.join(context)  # 添加上下文内容
                BedrockWrapper_text.printer(f'\n[INFO] request_text: {request_text}', 'info')

                # 将bedrock委托给线程池来处理，使用线程池异步调用 invoke_bedrock
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(handler.bedrock_wrapper.invoke_bedrock,request_text)

def Mode3_Memory():
    app.put_output("[Mode3]:Memory")

    history = [] # 存储对话历史的列表
    handler = TextHandler(BedrockWrapper_text.BedrockWrapper()) 
    TextHandler.text = promptlab["Mode3-Debug-1"]
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            input_text = app.get_input()[0] # 阻塞式等待获取输入框的内容

            if len(input_text) != 0:
                request_text = TextHandler.text + input_text
                BedrockWrapper_text.printer(f'\n[INFO] request_text: {request_text}', 'info')

                return_output = handler.bedrock_wrapper.invoke_bedrock(request_text,history=history) ## 为了不混乱对话历史的顺序，不能异步调用噜

                history.append({"role":"user","content":[{ "type": "text","text": input_text}]}) # 向对话历史中，插入用户输入（取出了提示词）
                history.append({"role":"assistant","content":[{ "type": "text","text": return_output}]}) # 向对话历史中，插入模型回复

def Mode4_MultiModal():
    from PE_Package.knowledge_base import math_problems
    import base64

    app.put_output("[Mode4]:MultiModal")
    handler = TextHandler(BedrockWrapper_text.BedrockWrapper())
    TextHandler.text = promptlab['Mode4-Debug-1']
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            info = app.get_input() # 阻塞式等待用过乎提交输入

            input_text = info[0] # 获取输入框的内容
            files = info[1] # 获取提交的图片文件

            if files:
                data = [] # data存放base64编码后的图像数据
                for file in files:
                    with open(file, 'rb') as f:
                        data.append([base64.b64encode(f.read()).decode(),os.path.splitext(file)[1]]) # 图像编码
                
                request_text = input_text + TextHandler.text + str(math_problems)
                BedrockWrapper_text.printer(f'\n[INFO] input_text: {input_text}', 'info')
                BedrockWrapper_text.printer(f'\n[INFO] files: {files}', 'info')

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(handler.bedrock_wrapper.invoke_bedrock,input_text,data)

def Mode5_MultiLanguage():
    from BedrockWrapper import BedrockWrapper_audio

    """
    让用户选择语言，并返回对应的索引。
    """    
    app.put_output("[Mode5]:MultiLanguage")
    app.put_output("Please select a language:")    
    for i, prompt in enumerate(BedrockWrapper_audio.voicePromptList):        
        app.put_output(f"{i}: {prompt}")        
    while True:        
        try:            
            choice = int(app.get_input()[0])  
            if 0 <= choice < len(BedrockWrapper_audio.voiceLanguageList):                
                BedrockWrapper_audio.voiceIndex = choice
                break
            else:                
                app.put_output("Invalid choice. Please try again.")        
        except ValueError:            
            app.put_output("Invalid input. Please enter a number.")
    BedrockWrapper_audio.update_config()
    app.put_output("[Status]:Config Update Correctly!")
    app.put_output(BedrockWrapper_audio.info_text)
    try:
        BedrockWrapper_audio.loop.run_until_complete(BedrockWrapper_audio.MicStream().basic_transcribe())
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
    BedrockWrapper_text.printInfo()
    thread = threading.Thread(target=ModeSelect_Script,daemon=True).start()
    app.root.mainloop()
    app._append_output(">?<")
    app.root.after(0,app.put_output,"[ModeSelect]:\n")
    app.get_input()[0]
