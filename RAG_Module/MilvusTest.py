from pymilvus import connections

try:
    connections.connect("default", host="localhost", port="19530")
    print("Milvus 连接成功！")
except Exception as e:
    print(f"Milvus 连接失败：{e}")