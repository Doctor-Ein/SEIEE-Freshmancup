from pymilvus import MilvusClient
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path

collection_name = "Dream_of_the_Red_Chamber"

# 获取脚本所在的目录
script_dir = Path(__file__).parent

# 基于脚本目录构建模型路径
model_path = (script_dir / "../models/bge-large-zh-v1.5").resolve()

# 使用 llama_index 加载本地模型
embedding = HuggingFaceEmbedding(model_name = str(model_path))

# 连接到 Milvus 服务
client = MilvusClient(uri="http://0.0.0.0:19530")

def queryContext(QueryContext:str):
    # 将查询上下文转化为向量
    QueryVector = embedding.get_text_embedding(QueryContext)

    # 检索 Milvus 中的向量
    search_params = {"metric_type": "L2", "params": {}}
    result = client.search(
        collection_name = collection_name,
        data = [QueryVector],  # 查询向量
        anns_field = "vector",  # 向量字段名
        search_params = search_params,  # 检索参数
        limit= 10 ,  # 返回的最相似向量数量
        output_fields = ["text", "partition"]  # 输出字段
    )

    context = ["<context>\n"]
    for hits in result:
        for hit in hits:
            context.append(f"第{hit['entity'].get('partition','0')}章：{hit['entity'].get('text','N/A')}\n")
    context.append("\n</context>")
    return context

if __name__ == "__main__":
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
        limit= 10 ,  # 返回的最相似向量数量
        output_fields = ["text", "partition"]  # 输出字段
    )


    # 打印检索结果及其上下文
    for hits in result:
        for hit in hits:
            print(f"ID: {hit['id']}, Distance: {hit['distance']}, Text: {hit['entity'].get('text', 'N/A')}")
            # print("Context:")
            # partition_name = '_' + str(hit['entity'].get('partition', 'default'))
            # # 构造 filter 字符串，确保 id 是整型
            # filter_str = f"id >= {int(hit['id']) - 5} and id <= {int(hit['id']) + 5}"
            # context_result = client.query(
            #     collection_name=collection_name,
            #     filter=filter_str,
            #     output_fields=["id", "text"],
            #     partition_names=[partition_name]
            # )
            # for context_hit in context_result:
            #     print(f"  ID: {context_hit['id']}, Text: {context_hit['text']}")
            print('\n')