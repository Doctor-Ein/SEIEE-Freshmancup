import os
from transformers import AutoModel, AutoTokenizer

# 设置镜像源
os.environ["HF_HUB_URL"] = "https://hf-mirror.com"

# 指定模型名称和保存路径
model_name = "BAAI/bge-large-zh-v1.5"
save_path = "../models"

# 下载并保存模型和分词器
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=save_path)
model = AutoModel.from_pretrained(model_name, cache_dir=save_path)

print(f"模型和分词器已成功下载并保存到 {save_path}")