from pymilvus import MilvusClient
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

collection_name = "Dream_of_the_Red_Chamber"

# 使用 llama_index 加载本地模型
embedding = HuggingFaceEmbedding(model_name="../models/bge-small-zh-v1.5")

# 连接到 Milvus 服务
client = MilvusClient(uri="http://0.0.0.0:19530")
print(client.has_collection(collection_name=collection_name),flush=True)
print(client.describe_collection(collection_name=collection_name),flush=True)

# 查询上下文
QueryContext = "贾宝玉和林黛玉初次见面时发生了什么？"

# 将查询上下文转化为向量
QueryVector = embedding.get_text_embedding(QueryContext)

# 检索 Milvus 中的向量
search_params = {"metric_type": "L2", "params": {}}
result = client.search(
    collection_name = collection_name,
    data = [QueryVector],  # 查询向量
    anns_field = "vector",  # 向量字段名
    search_params = search_params,  # 检索参数
    limit= 20 ,  # 返回的最相似向量数量
    output_fields = ["text"]  # 输出字段
)


# 打印检索结果
for hits in result:
    for hit in hits:
        print(f"ID: {hit['id']}, Distance: {hit['distance']}, Text: {hit['entity'].get('text', 'N/A')}")
        print('\n')