### LLM-Teacher-0.5

### 使用方法
- *这里环境部分和原来是一样的，但是还是要再操作一下，毕竟是一个新的文件夹（工作区）~*
- 创建并激活一个conda环境：
    - ```conda create --name LLM-Teacher python=3.11.11```（相同的配置可以避免不少问题，大概……）
    - ```conda activate LLM-Teacher```
    - ```pip3 install -r requirements.txt```
- 配置环境变量：AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY （这个方法windows直接看培训视频，不过你们应该都已经做好永久的配置了，这个是一个常出问题的点，**要记得全大写和加AWS，呜呜**）
- 在终端启动命令```python3 EventHandler.py```后，会弹出一个GUI窗口界面，在这里完成交互~不过VScode的终端中还是会输出一些调试的信息，可以参考~

### 功能特性
- 提示词-知识库体系，`knowledge_base.py`是以一个python列表，存储的单条知识（python字典形式）
- GUI窗口输入输出，快来试试我们的快捷键`Command + Enter`,`Control + Enter`,`Shift + Enter`用于提交输入，非常棒的防误触设计（自豪~）支持多行输入输出，和`Control + 方向键`快捷跳转首尾
- 使用`'anthropic.claude-3-sonnet-20240229-v1:0'`，这个时代的次顶级(pro)模型，并且即将支持多模态！