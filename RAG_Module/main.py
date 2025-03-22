from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from data_processor import DataProcessor
from milvus_client import MilvusClient
from config import Config

def main():
    # 初始化组件
    processor = DataProcessor()
    milvus = MilvusClient()
    
    # 加载并分块数据
    docs = processor.load_data()
    nodes = processor.chunk_text(docs)
    
    # 初始化本地嵌入模型
    embed_model = HuggingFaceEmbedding(
        model_name=Config.EMBED_MODEL,
        device=Config.DEVICE,
        encode_kwargs = {'normalize_embeddings': True}  # 适合IP计算
    )
    
    # 创建Milvus集合
    milvus.create_collection()
    
    # 插入数据
    result = milvus.insert_data(nodes, embed_model)
    print(f"插入成功，ID范围：{result.primary_keys[:5]}...")

if __name__ == "__main__":
    main()