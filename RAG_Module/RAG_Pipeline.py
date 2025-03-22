from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.vector_stores.milvus import MilvusVectorStore
from pymilvus import connections, Collection, utility
import os

# 配置参数
MILVUS_HOST = "0.0.0.0"  # MacOS必须用此地址代替localhost
MILVUS_PORT = 19530
COLLECTION_NAME = "hongloumeng_vectors"
DATA_PATH = os.path.join(os.path.dirname(__file__), "data.txt")

# 初始化Milvus连接
def init_milvus():
    try:
        connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
        print("✅ Milvus连接成功")
    except Exception as e:
        print(f"❌ Milvus连接失败: {e}")
        raise

# 创建向量存储
def create_vector_store():
    return MilvusVectorStore(
        uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}",
        collection_name=COLLECTION_NAME,
        dim=768,  # HuggingFace嵌入维度
        overwrite=False,  # 防止覆盖已有数据
        consistency_level="Strong",  # 强一致性
        index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
    )

# 处理文本数据
def process_text_data():
    # 使用HuggingFace嵌入模型
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")
    
    # 使用语义分割器
    node_parser = SemanticSplitterNodeParser(
        buffer_size=1,  # 控制分割粒度
        breakpoint_percentile_threshold=95,  # 分割阈值
        embed_model=embed_model  # 传入嵌入模型
    )
    
    # 读取数据
    documents = SimpleDirectoryReader(input_files=[DATA_PATH]).load_data()
    
    # 分割文本
    nodes = node_parser.get_nodes_from_documents(documents)
    print(f"✅ 文本分割完成，共 {len(nodes)} 个节点")
    
    return nodes, embed_model

def main():
    # 初始化Milvus
    init_milvus()
    
    # 创建向量存储
    vector_store = create_vector_store()
    
    # 处理文本数据
    nodes, embed_model = process_text_data()
    
    # 创建向量索引
    index = VectorStoreIndex(nodes=[], embed_model=embed_model, vector_store=vector_store)
    
    # 插入数据
    index.insert_nodes(nodes)
    print(f"✅ 数据插入完成，共插入 {len(nodes)} 个节点")
    
    # 获取集合对象
    collection = Collection(COLLECTION_NAME)
    
    # 强制释放集合
    try:
        collection.release()
        print("✅ 集合已强制释放")
    except Exception as e:
        print(f"❌ 集合释放失败: {e}")
    
    # 删除已有索引
    if collection.has_index():
        print("删除已有索引...")
        try:
            collection.drop_index()
            print("✅ 索引删除成功")
        except Exception as e:
            print(f"❌ 索引删除失败: {e}")
    
    # 创建索引
    print("创建索引...")
    try:
        collection.create_index(
            field_name="embedding",
            index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
        )
        print("✅ 索引创建完成")
    except Exception as e:
        print(f"❌ 索引创建失败: {e}")
    
    # 重新加载集合
    print("重新加载集合...")
    try:
        collection.load()
        print("✅ 集合重新加载成功")
    except Exception as e:
        print(f"❌ 集合重新加载失败: {e}")

if __name__ == "__main__":
    main()
