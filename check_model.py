import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
import torch

def check_model_integrity(model_path):
    """验证模型文件的完整性"""
    print(f"正在验证模型: {model_path}")
    
    # 关键文件列表及最小大小（字节）
    required_files = {
        "config.json": 1000,
        "model.safetensors": 1.2 * 1024 * 1024 * 1024,  # 约1.2GB
        "sentencepiece.bpe.model": 10 * 1024 * 1024,     # 至少10MB
        "tokenizer_config.json": 1000,
        "special_tokens_map.json": 500
    }
    
    # 检查文件是否存在且大小正常
    missing_files = []
    corrupted_files = []
    
    for file, min_size in required_files.items():
        file_path = Path(model_path) / file
        if not file_path.exists():
            missing_files.append(file)
            continue
            
        actual_size = file_path.stat().st_size
        if actual_size < min_size:
            corrupted_files.append((file, f"大小异常: {actual_size} < {min_size}"))
    
    # 打印检查结果
    if missing_files:
        print("❌ 缺失文件:", missing_files)
    if corrupted_files:
        print("❌ 文件损坏:", corrupted_files)
    if not missing_files and not corrupted_files:
        print("✅ 所有关键文件存在且大小正常")
    
    # 尝试加载分词器和模型
    print("\n尝试加载模型...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModel.from_pretrained(model_path)
        
        # 简单推理测试
        test_text = "测试模型完整性"
        inputs = tokenizer(test_text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        
        print("✅ 模型加载成功，推理测试通过")
        print(f"输出向量形状: {outputs.last_hidden_state.shape}")
        return True
    except Exception as e:
        print(f"❌ 模型加载失败: {str(e)}")
        return False

if __name__ == "__main__":
    model_path = "./models/bge-reranker-large"
    if not os.path.exists(model_path):
        print(f"错误: 目录不存在 {model_path}")
    else:
        check_model_integrity(model_path)