# LLM-Teacher-0.7

#### contributors: bleem StarDust Meteor雨 TheEin

### Congratulations! We've got 3 modules completed!

### 功能特性
- 知识库体系，`knowledge_base.py`是以一个python列表，存储的单条知识（python字典形式）可以定制化装载专业领域或私有知识库~（致谢 bleem的工作和维护~orz
- 提示词库`PromptLab.py`是一个python字典，统一管理和更新不同的提示词，便于维护和项目分割（致谢 bleem的工作和维护~orz
- GUI窗口输入输出，快来试试我们的快捷键`Command + Enter`,`Control + Enter`,`Shift + Enter`用于提交输入，非常棒的防误触设计（自豪~）支持多行输入输出，和`Control + 方向键`快捷跳转首尾等……体验最人性化的交互式输入！
- 使用`'anthropic.claude-3-sonnet-20240229-v1:0'`，这个时代的次顶级(pro)模型，并且支持多模态~点击即可添加图片！（致谢 Stardust的工作~orz
- 借助亚马逊的polly和transcrible服务，实现了多种语言的实时交互！（致谢 Meteor雨 的工作~orz

---

### 使用方法
- *这里环境部分和原来是一样的，但是还是要再操作一下，毕竟是一个新的文件夹（工作区）~*
- 创建并激活一个conda环境：
    - ```conda create --name LLM-Teacher python=3.11.11```（相同的配置可以避免不少问题，大概……）
    - ```conda activate LLM-Teacher```
    - ```pip3 install -r requirements.txt```
- 配置环境变量：AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY （这个方法windows直接看培训视频，不过你们应该都已经做好永久的配置了，这个是一个常出问题的点，**要记得全大写和加AWS，呜呜**）
- 在终端启动命令```python3 EventHandler.py```后，会弹出一个GUI窗口界面，在这里完成交互~不过VScode的终端中还是会输出一些调试的信息，可以参考~

---
### 后续更新计划
- LLM-Teacher-0.8 预计在3.22交付！实现RAG功能，使用核心框架LlamaIndex和Milvus向量数据库
- LLM-Teacher-0.9 预计在3.23交付！实现记忆功能，使用历史上下文 + 门控的方案~
- LLM-Teacher 迈向1.0 将在第六周持续优化，以期在29日获得最佳的展示效果！加油加油加油！