import torch

class Config:
    # 数据配置
    DATA_PATH = "./data.txt"
    ENCODING = "UTF-8"  # 红楼梦常见编码
    
    # 分块配置（适配中文古典文学）
    CHUNK_SIZE = 384   # 根据模型max_length调整
    CHUNK_OVERLAP = 64
    
    # 嵌入模型
    EMBED_MODEL = "BAAI/bge-base-zh-v1.5"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Milvus配置
    MILVUS_HOST = "localhost"
    MILVUS_PORT = "19530"
    COLLECTION_NAME = "hongloumeng_vectors"
    VECTOR_DIM = 768  # bge-base-zh-v1.5的维度