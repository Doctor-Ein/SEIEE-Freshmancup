import json
import re
from collections import OrderedDict
import jieba

# 配置参数
DEFAULT_CHUNK_SIZE = 400  # 默认块大小
DEFAULT_OVERLAP = 50      # 默认重叠大小
MIN_CHUNK_LENGTH = 20     # 最小块长度（过滤过小碎片）
MIN_MERGE_LENGTH = 100    # 最小合并长度（用于首尾块合并）

def fixed_window_chunking(text, chunk_size, overlap):
    """固定窗口分块函数"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap  # 应用重叠
    # 过滤空块并合并过小碎片
    return [chunk for chunk in chunks if chunk and len(chunk) > MIN_CHUNK_LENGTH]

def protect_entities(text):
    """保护关键实体（避免拆分）"""
    words = jieba.lcut(text)
    protected = []
    for word in words:
        if len(word) > 2:  # 可能是实体
            protected.append(f"##{word}##")
        else:
            protected.append(word)
    return "".join(protected)

def dynamic_chunk_params(avg_length):
    """动态调整分块参数"""
    if avg_length > 500:  # 长段落章节
        return min(600, DEFAULT_CHUNK_SIZE + 100), DEFAULT_OVERLAP + 20
    elif avg_length < 200:  # 短段落章节
        return max(250, DEFAULT_CHUNK_SIZE - 100), DEFAULT_OVERLAP - 20
    else:
        return DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP

def process_chapters(input_path, output_path):
    """处理章节数据并生成分块结果"""
    # 读取原始数据
    with open(input_path, 'r', encoding='utf-8') as f:
        chapters = json.load(f, object_pairs_hook=OrderedDict)
    
    processed = OrderedDict()
    
    # 遍历每个章回（保持顺序）
    for idx, (chap_title, paragraphs) in enumerate(chapters.items(), 1):
        # 合并段落时保留换行符
        full_text = '\n'.join(paragraphs)
        
        # 动态调整分块参数
        avg_length = len(full_text) / len(paragraphs)
        chunk_size, overlap = dynamic_chunk_params(avg_length)
        
        # 保护关键实体
        protected_text = protect_entities(full_text)
        
        # 在英文标点处添加分割保护
        protected_text = re.sub(r'([.!?;])', r'\1##SPLIT##', protected_text)
        
        # 执行分块
        raw_chunks = fixed_window_chunking(
            text=protected_text,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        # 后处理：恢复标点结构和实体
        final_chunks = []
        for chunk in raw_chunks:
            cleaned = chunk.replace('##SPLIT##', '').replace('##', '')
            # 确保不以截断的标点开头
            if cleaned and cleaned[0] in '.!?;':
                cleaned = cleaned[1:].lstrip()
            if cleaned:
                final_chunks.append(cleaned)
        
        # 合并过小的首尾块
        if len(final_chunks) > 1:
            if len(final_chunks[0]) < MIN_MERGE_LENGTH:
                final_chunks[1] = final_chunks[0] + final_chunks[1]
                final_chunks.pop(0)
            if len(final_chunks[-1]) < MIN_MERGE_LENGTH:
                final_chunks[-2] += final_chunks[-1]
                final_chunks.pop()
        
        processed[str(idx)] = final_chunks
    
    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

def generate_debug_view(chunks, output_debug_path):
    """生成分块调试视图"""
    marked = []
    for chap_id, chunk_list in chunks.items():
        marked.append(f"\n===== Chapter {chap_id} =====\n")
        for i, chunk in enumerate(chunk_list):
            marked.append(f"\n--- Chunk {i+1} ---\n{chunk}\n")
    with open(output_debug_path, 'w', encoding='utf-8') as f:
        f.write("".join(marked))

if __name__ == "__main__":
    # 输入输出路径
    input_path = "chapters.json"
    output_path = "chunks.json"
    debug_path = "chunks_debug.txt"
    
    # 处理章节数据
    process_chapters(input_path, output_path)
    
    # 生成调试视图
    with open(output_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    generate_debug_view(chunks, debug_path)
    
    print(f"分块结果已保存至 {output_path}")
    print(f"调试视图已保存至 {debug_path}")