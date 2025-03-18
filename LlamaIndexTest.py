from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Step 1: Load a single file (data.txt)
reader = SimpleDirectoryReader(input_files=["./data.txt"])
documents = reader.load_data()

# Step 2: Initialize the embedding model
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-zh-v1.5")

# Step 3: Build the index
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# Step 4: Save the index data
index.storage_context.persist(persist_dir="./vector_store")

print("向量化完成，数据已存储。")