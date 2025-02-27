### LLM-Teacher:第一个简单的版本

### 实现的功能特性（2.27 ， version 0.1）
- 基础的text-to-text实现了（以一种混乱无序的代码，之后安排重构）
- 基础的预置提示词功能（暂时硬编码在代码里面，查找`FirstPrePrompt`,`SecondPrePrompt`即可跳转过去哦
- 关闭了后台执行器打断模型输出的功能（因为存在两个方法竞争标准输入，出现冲突，试图解决但是失败QWQ‘
- 其他功能没有改动，完成了一些更精细的函数功能测试，没有使用的语音模块语句注释掉了

### 使用方法
- 创建并激活一个conda环境：
    - ```conda create --name LLM-Teacher python=3.11.11```（相同的配置可以避免不少问题，大概……）
    - ```conda activate LLM-Teacher```
    - ```pip3 install -r requirements.txt```
- 配置环境变量：AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY （这个方法windows直接看培训视频，不过你们应该都已经做好永久的配置了，这个是一个常出问题的点，**要记得全大写和加AWS，呜呜**）
- ```python3 app.py```

### 其他注意
- 若要使用语音功能，请查看最后5行代码，可以将try块中两行替换（一个注释，一个保留）
```python
loop = asyncio.get_event_loop()
try:
    # loop.run_until_complete(MicStream().basic_transcribe())
    loop.run_until_complete(text2text())
except (KeyboardInterrupt, Exception) as e:
    print("RuntimeError:",e.__class__.__name__,str(e))
```