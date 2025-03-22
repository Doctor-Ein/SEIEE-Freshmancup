from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pymilvus import connections, Collection, utility
import os
import time

# 设置 HuggingFace 缓存路径
os.environ["HF_HOME"] = "./models"

# 初始化 Milvus 连接
def init_milvus():
    try:
        connections.connect(host="0.0.0.0", port="19530")
        print("✅ Milvus连接成功")
    except Exception as e:
        print(f"❌ Milvus连接失败: {e}")
        raise

# 初始化 Milvus 连接
init_milvus()

# 检查AWS凭证
if not all([os.getenv("AWS_ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY")]):
    raise ValueError("请设置AWS_ACCESS_KEY_ID和AWS_SECRET_ACCESS_KEY环境变量")

# 初始化本地嵌入模型
embed_model = HuggingFaceEmbedding(model_name="./models/bge-small-zh-v1.5")

# 初始化Milvus向量存储
vector_store = MilvusVectorStore(
    uri="http://0.0.0.0:19530",
    collection_name="hongloumeng_vectors"
)

# 获取集合对象
collection = Collection("hongloumeng_vectors")

# 检查并加载集合
max_retries = 10
retry_count = 0
load_state = utility.load_state("hongloumeng_vectors")

while load_state != "Loaded" and retry_count < max_retries:
    print(f"集合未加载，正在加载... (尝试 {retry_count + 1}/{max_retries})")
    try:
        collection.load()
        load_state = utility.load_state("hongloumeng_vectors")
        if load_state == "Loaded":
            print("✅ 集合已加载")
            break
    except Exception as e:
        print(f"❌ 集合加载失败: {str(e)}")
    retry_count += 1
    time.sleep(1)  # 等待1秒后重试

if load_state != "Loaded":
    raise RuntimeError(f"集合加载失败，已达到最大重试次数 {max_retries}")

# 检查集合中的实体数量
print("集合中的实体数量:", collection.num_entities)

# 配置AWS Bedrock Converse
llm = BedrockConverse(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1"
)

# 创建查询引擎
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)

# 创建查询引擎
query_engine = index.as_query_engine(
    llm=llm,
    similarity_top_k=20,  # 增大 top_k 值
    vector_store_query_mode="default",
    vector_store_kwargs={
        "search_params": {"metric_type": "L2", "params": {"nprobe": 20}}  # 调整 nprobe
    }
)

class QueryEngine:
    def __init__(self):
        # 初始化Milvus连接
        init_milvus()
        
        # 创建向量存储
        self.vector_store = MilvusVectorStore(
            uri="http://0.0.0.0:19530",
            collection_name="hongloumeng_vectors"
        )
        
        # 创建查询引擎
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store, 
            embed_model=embed_model
        )
        
        self.query_engine = self.index.as_query_engine(
            llm=llm,
            similarity_top_k=20,
            vector_store_query_mode="default",
            vector_store_kwargs={
                "search_params": {"metric_type": "L2", "params": {"nprobe": 20}}
            }
        )

    def query(self, question: str):
        """执行查询"""
        try:
            response = self.query_engine.query(question)
            return {
                "answer": str(response),
                "sources": [node.text for node in response.source_nodes]
            }
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    engine = QueryEngine()
    while True:
        question = input("\n请输入查询内容（输入q退出）：")
        if question.lower() == "q":
            break
        result = engine.query(question)
        if "error" in result:
            print(f"❌ 查询失败: {result['error']}")
        else:
            print("\n查询结果：")
            print(result["answer"])
            print("\n参考来源：")
            for i, source in enumerate(result["sources"], 1):
                print(f"{i}. {source}")
