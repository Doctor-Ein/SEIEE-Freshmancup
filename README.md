# FreshmanCup
# 🌍 大模型虚拟教师应用

![GitHub stars](https://img.shields.io/github/stars/Doctor-Ein/SEIEE-Freshmancup?style=social)
![GitHub forks](https://img.shields.io/github/forks/Doctor-Ein/SEIEE-Freshmancup?style=social)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

<!-- 🚀 **基于Bedrock**，在 **多模态、RAG、多语言对话、记忆、提示词工程** 等方面做了强化微调与提升。 -->

---

## 📖 **项目简介**
本项目是一个功能强大的 **大语言模型应用**，主要特性包括：
- ✅ **多模态**（Multimodal）：支持文本、图像、音频等多种数据输入
- ✅ **RAG（检索增强生成）**：结合知识库提高回答的准确性
- ✅ **多语言对话**（Multilingual）：支持多种语言的交流对话
- ✅ **记忆**（Memory）：支持短期记忆，提高对话连贯性
- ✅ **提示词工程**（Prompt Engineering）：优化提示词，提高生成质量

**📌 主程序文件**：`main.py`（核心控制逻辑）

---

## 📝 **各文件用途**
| 文件名                       | 作用                                           |
| ---------------------------- | ---------------------------------------------- |
| `main.py`                    | **主程序入口**，协调各模块，执行核心逻辑       |
| `TextInputApp.py`            | 提供终端/GUI 交互的图形化输入输出              |
| `PE_Package/PromptEngine.py` | 处理提示词优化，提高 LLM 生成质量              |
| `PE_Package/PromptLab.py`    | 提示词测试的平台，存放调试好的提示词           |
| `knowledge_base.py`          | 数据结构、数学的例题知识库，用于优化提示词工程 |
| `RAG_Package/QueryEngine.py` | 处理查询、知识库检索（RAG）                    |
| `RAG_Package/Reranker.py`    | 重新排序检索结果，提高 RAG 生成质量            |
| `Embedding.py`               | 处理文本嵌入，将向量化的数据保存到Milvus       |
| `chapters.json`              | `data.txt`分割处理后的主要数据                 |
| `api_request_schema.py`      | 定义各模型的配置                               |
| `BedrockWrapper_text.py`     | 处理文本输入，集成 Bedrock 的调用逻辑          |
| `BedrockWrapper_audio.py`    | 处理音频输入，实现实时对话的模式               |


## 🛠 **安装与使用**
### 环境依赖
- *python* 版本和第三方库（`requirements.txt`）
- 嵌入模型和重排模型（可选）-> 可在![huggingface.co]https://huggingface.co 上下载
- *Docker* 本地部署或其他方式的 *Milvus* 向量数据库

### 安装方法
我们推荐使用 `conda` 管理项目环境，安装 anaconda 并执行
- `conda create --name LLM-Teacher python=3.11.11`
- `conda activate LLM-Teacher`
下载依赖库: `pip install -r requirements.txt`
设置AWS的访问账户，`AWS_ACCESS_KEY_ID`，`AWS_SECRET_ACCESS_KEY`
安装模型到与项目主文件夹下（与`main.py`同级）在 `models/` 中下载对应模型
- `bge-large-zh-v1.5`
- `bge-reranker-large`
*Docker* 启动本地 *Milvus* 服务（详见![Milvus]https://github.com/milvus-io/milvus，代码支持2.5.x 版本）
执行`python3 Dataset/Embedding.py`将数据嵌入，也可替换`data.txt`为您准备的数据
执行`python3 main.py`，启动我们的图形化输入输出，体验增强能力的 LLM-Teacher 🎉🎉🎉
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


---

## 🚀 **加入我们**
📢 **关注最新动态，欢迎支持！**

## 🌟 *致谢*
感谢以下个人和团队对项目的贡献：

- [Meteor728](https://github.com/Meteor728)：感谢你为项目开发了*Multilingual*以及RAEDME的编写，代码很棒，文档也超用心~（这里夸夸不是她写的😃 Orz
- [StarDust](https://github.com/StarDust?)：感谢你为项目开发*MultiModal*，并且在Debug方面做出了卓越贡献（不是指1.5h修复4行代码🤣 Orz
- [bleem](https://github.com/bleem？)：感谢你为项目进行了全面的测试，确保了项目的稳定性！伟大的提示词工程师！所有思想和努力都看到啦☺️，Orz
- [Doctor-Ein](https://github.com/bleem？)：感谢自己没有哭哦~