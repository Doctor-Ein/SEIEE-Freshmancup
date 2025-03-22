from pymilvus import connections, utility, Collection

# 配置连接参数
MILVUS_HOST = "0.0.0.0"  # MacOS 必须用此地址代替 localhost
MILVUS_PORT = 19530

def test_milvus_connection():
    try:
        # 连接 Milvus
        connections.connect(
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        print("✅ 连接成功！")

        # 获取服务端版本
        print("服务端版本:", utility.get_server_version())

        # 列出所有集合（若无集合则为空列表）
        print("现有集合:", utility.list_collections())

    except Exception as e:
        print("❌ 连接失败:", e)
        return False
    return True

def check_collection(collection_name):
    try:
        # 检查集合是否存在
        if utility.has_collection(collection_name):
            print(f"集合 '{collection_name}' 存在")

            # 获取集合对象
            collection = Collection(collection_name)

            # 检查集合中的实体数量
            print(f"集合 '{collection_name}' 中的实体数量:", collection.num_entities)
        else:
            print(f"集合 '{collection_name}' 不存在")
    except Exception as e:
        print(f"❌ 检查集合 '{collection_name}' 失败:", e)

if __name__ == "__main__":
    # 测试 Milvus 连接
    if test_milvus_connection():
        # 检查指定集合
        check_collection("hongloumeng_vectors")