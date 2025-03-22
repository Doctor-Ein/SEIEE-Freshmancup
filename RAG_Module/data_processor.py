from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from typing import List
from config import Config

class DataProcessor:
    def __init__(self):
        # 使用默认分块器（去掉 separators 参数）
        self.splitter = SentenceSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
    
    def load_data(self) -> List[str]:
        """加载红楼梦文本（处理特殊编码）"""
        # 直接指定文件路径而非目录
        reader = SimpleDirectoryReader(
            input_files=[Config.DATA_PATH],
            file_metadata=lambda _: {"encoding": Config.ENCODING}
        )
        return reader.load_data()
    
    def chunk_text(self, documents) -> List[dict]:
        """生成带元数据的中文分块"""
        nodes = self.splitter.get_nodes_from_documents(documents)
        
        # 添加自定义元数据（例如章节信息）
        for idx, node in enumerate(nodes):
            node.metadata["source"] = Config.DATA_PATH
            node.metadata["chunk_id"] = f"chunk_{idx+1}"
        
        return nodes