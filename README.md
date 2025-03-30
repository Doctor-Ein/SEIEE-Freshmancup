# FreshmanCup
# 🌍 大模型虚拟教师应用

![GitHub stars](https://img.shields.io/github/stars/Doctor-Ein/SEIEE-Freshmancup?style=social)
![GitHub forks](https://img.shields.io/github/forks/Doctor-Ein/SEIEE-Freshmancup?style=social)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

<!-- 🚀 **基于Amazon Bedrock平台及配套Claude-3模型**，在 **多模态、RAG、多语言对话、记忆、提示词工程** 等方面做了强化性微调与提升。 -->

---

## 📖 **项目简介**
本项目是一个功能强大的 **大语言模型应用**，主要特性包括：
- ✅ **多模态**（Multimodal）：支持文本和图像的混合输入以及音频等多种输入形式
- ✅ **检索增强生成**（Retrieval-augmented Generation，RAG）：结合向量化知识库进行相关性比对分析和Rerank，提高回答的准确性
- ✅ **多语言对话**（Multilingual）：支持中、英、日、韩等多种语言的交流对话
- ✅ **记忆**（Memory）：支持短期记忆，允许临时的话题切换和重拾，提高对话连贯性
- ✅ **提示词工程**（Prompt Engineering）：针对不同目标话题优化提示词，提高生成质量

📌 **主程序文件**：`main.py`

---

## 📝 **各文件用途**
| 文件名                       | 作用                                           |
| ---------------------------- | ---------------------------------------------- |
| `main.py`                    | **主程序入口**，协调各模块，执行核心逻辑       |
| `TextInputApp.py`            | 提供 Terminal/GUI 交互的图形化输入输出         |
| `PE_Package/PromptEngine.py` | 处理提示词优化，提高 LLM 生成质量              |
| `PE_Package/PromptLab.py`    | 提示词测试的平台，存放调试好的提示词           |
| `knowledge_base.py`          | 数据结构知识和数学的例题库，用于优化提示词工程 |
| `RAG_Package/QueryEngine.py` | 处理查询请求，使用基于 RAG 的知识库检索        |
| `RAG_Package/Reranker.py`    | 重新排序检索结果，提高 RAG 生成质量            |
| `Embedding.py`               | 处理文本嵌入，将向量化的数据保存到Milvus       |
| `chapters.json`              | 红楼梦文本 `data.txt` 分割处理后的主要数据     |
| `api_request_schema.py`      | 由 Amazon 提供的许可模型及其配置表             |
| `BedrockWrapper_text.py`     | 处理文本输入，集成了 Bedrock 的调用逻辑        |
| `BedrockWrapper_audio.py`    | 处理音频输入，实现实时语音输出                 |


## 🛠 **安装与使用**
### 环境依赖
- *python 3.10* 版本，内置库和第三方库（参见`requirements.txt`），稳定的、可使用Claude的IP地域和网络环境
- 可选的嵌入模型和重排模型，可在[huggingface.co](https://huggingface.co) 下载
- *Docker* 本地部署或其他方式的 *Milvus* 向量数据库

### 安装方法
推荐使用 `conda` 管理项目环境，便于隔离库环境
安装 anaconda3 并在终端执行以下命令以创建环境
- `conda create --name LLM-Teacher python=3.11.11`
启用创建的conda环境，并在其中下载依赖库
- `conda activate LLM-Teacher`
- `pip install -r requirements.txt`
设置AWS的访问账户为环境变量，便于程序读取进行许可验证
- `AWS_ACCESS_KEY_ID`，`AWS_SECRET_ACCESS_KEY`
安装模型到与项目主文件夹下（与`main.py`同级）在 `models/` 中下载对应模型
- `bge-large-zh-v1.5`
- `bge-reranker-large`
在每次使用时
- 在终端切换到程序根目录，执行`conda activate LLM-Teacher`启用环境
- 通过 *Docker* 启动本地 *Milvus* 服务（详见[Milvus](https://github.com/milvus-io/milvus)，代码支持2.5.x 版本）
- 如果需要替换`data.txt`，替换后请执行`python3 Dataset/Embedding.py`完成数据嵌入
- 执行`python3 main.py`，启动我们的图形化输入输出，体验能力增强后的 LLM-Teacher 🎉🎉🎉

---

## 🎯 **功能详解**
### 🧠 1.记忆（Memory）
- **短期记忆**：保持对话上下文，提高连贯性
- 存储对话历史的列表 ***history***
- 每次调用将先后插入用户输入和模型回复
- 然后在构造 ***body*** 时，将 ***history*** 插入到 ***message*** 中。

---

###  :smile: 2.提示词工程（Prompt Engineering）
- 优化 LLM 提示词，提高生成质量
- 输入的内容通过提示词引擎查找相关知识点（关键词匹配）
- 将提示词和输入文本连接

---

### 🌍 3.多语言对话（Multilingual）
支持 **多种语言**，实现流畅的跨语言交流。
- 用户输入语音，使用 ***Amazon Transcribe*** 服务转录（Speech To Text）
- 调用模型内容生成 (Text To Text)
- 应用通过语音反馈，使用 ***Amazon Polly*** 服务（Text To Speech）
- 配置 ***LanguageCode*** 和 ***VoiceID*** 两部分，提供用户选择语言的代码来实现不同语言对话
- 结果：实现中文、英文、日语、韩语等对话。

---

### 📚 4. RAG（检索增强生成）
结合知识库，提高回答的准确性和信息性。
#### 前期准备
- 原始数据的分割分块处理
- 使用嵌入模型将分块的数据向量化，并存储到向量数据库 ***Milvus*** 中
#### 查询阶段
- 获取输入将`input_text`传入`queryContext`中
- 将输入的文本转化为向量（分割只获取第一个句子，而不包括后续的指令）
  - e.g. "贾宝玉和林黛玉初次见面时发生了什么？请根据原著描述回答。" ➡️ "贾宝玉和林黛玉初次见面时发生了什么？"
- 使用 ***Milvus*** 查询与输入向量最近的`top_n`个向量
- 对上述搜索到向量组，通过Rerank模型，获取其中相似度分数最高的`top_k`个
- 将获取到的最终向量，连接输入，调用模型

---

### 🎨 5. 多模态（Multimodal）
支持 **文本、图片、音频** 等多种输入类型，实现更丰富的 AI 交互。
- 多模态基于`Claude-3-sonnet`的图像识别能力
- 将图像以 ***base64*** 格式编码，插入`body['message']`中
- 保证不同输入流之间的协调

---

## 🚀 **加入我们**
📢 **关注最新动态，欢迎支持！**

## 🌟 *致谢*
感谢以下个人和团队对项目的贡献：
- [Meteor728](https://github.com/Meteor728)：感谢你为项目开发了*Multilingual*以及RAEDME的编写，代码很棒，文档也超用心，还有认真地管理了比赛的事项以及火锅非常好吃和开心😋~（这里夸夸是我写的😃 Orz
- [StarDust](https://github.com/Rewind2Nowhere)：感谢你为项目开发*MultiModal*，并且在项目部分思路构建和Debug方面做出了卓越贡献（不是指1.5h修复4行代码🤣 Orz
- [bleem](https://github.com/bleem？)：感谢你为项目进行了全面的测试，为每个模块调整适配有效的提示词，确保了项目的稳定性！伟大的提示词工程师！所有思想和努力都看到啦☺️，Orz
- [Doctor-Ein](https://github.com/Doctor-Ein)：感谢自己没有哭哦~（来自队友的碎碎念：其实xlx commit了整个项目超过60%的代码，完成了从Milvus数据库构建到异步执行处理再到项目重构的大量工作，做出了巨大的贡献、巨大的牺牲和巨大的carry）
