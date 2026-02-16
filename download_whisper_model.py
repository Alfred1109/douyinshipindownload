"""
预下载 Whisper 模型
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("="*60)
    print("下载 Whisper 模型")
    print("="*60)
    
    try:
        from faster_whisper import WhisperModel
        
        model_size = "medium"  # 从配置读取
        device = "cpu"  # Windows CPU 通常用 cpu
        compute_type = "int8"  # CPU 推荐使用 int8
        
        print(f"\n模型配置:")
        print(f"  - 大小: {model_size}")
        print(f"  - 设备: {device}")
        print(f"  - 精度: {compute_type}")
        print(f"\n⏬ 开始下载模型（约 1.5GB，首次运行需要几分钟）...")
        print("   请耐心等待...\n")
        
        # 初始化模型会自动下载
        model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            download_root=None,  # 使用默认缓存目录
        )
        
        print("\n" + "="*60)
        print("✅ 模型下载完成！")
        print("="*60)
        print(f"\n模型已缓存，后续使用将直接加载")
        print(f"现在可以运行: python quick_extract.py")
        print("\n" + "="*60)
        
    except ImportError:
        print("\n❌ faster-whisper 未安装")
        print("请运行: pip install faster-whisper")
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
