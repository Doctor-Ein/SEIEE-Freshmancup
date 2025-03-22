from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
from config import Config

class MilvusClient:
    def __init__(self):
        # 连接Milvus
        connections.connect(
            "default", 
            host=Config.MILVUS_HOST, 
            port=Config.MILVUS_PORT
        )
        
        # 定义Collection Schema（适配中文模型）
        self.fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),  # 支持长文本
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=Config.VECTOR_DIM)
        ]
        self.schema = CollectionSchema(
            fields=self.fields,
            description="红楼梦文本向量存储"
        )
        
    def create_collection(self):
        """创建/重置集合"""
        if Collection(Config.COLLECTION_NAME).has():
            Collection(Config.COLLECTION_NAME).drop()
        return Collection(
            Config.COLLECTION_NAME, 
            schema=self.schema, 
            using="default"
        ).create_index(
            field_name="vector",
            index_params={
                "index_type": "HNSW",
                "metric_type": "IP",  # 内积相似度
                "params": {"M": 16, "efConstruction": 128}
            }
        )
    
    def insert_data(self, nodes: list[dict], embed_model):
        """批量插入向量数据"""
        collection = Collection(Config.COLLECTION_NAME)
        
        # 生成向量
        texts = [node.text for node in nodes]
        vectors = embed_model.get_text_embedding_batch(texts)
        
        # 准备插入数据
        entities = [
            [node.text for node in nodes],  # text字段
            vectors  # vector字段
        ]
        
        # 批量插入（优化吞吐量）
        insert_result = collection.insert(entities)
        collection.flush()
        
        return insert_result