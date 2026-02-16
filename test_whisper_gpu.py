"""
使用 GPU 测试 Whisper（速度快 10-20 倍）
"""
from pathlib import Path

audio_file = Path("temp/audio.mp3")

if not audio_file.exists():
    print(f"❌ 音频文件不存在: {audio_file}")
    exit(1)

print("="*60)
print("GPU 加速 Whisper 语音识别")
print("="*60)
print(f"\n音频文件: {audio_file}")
print(f"文件大小: {audio_file.stat().st_size / 1024:.2f} KB\n")

try:
    from faster_whisper import WhisperModel
    import torch
    
    # 检查 CUDA
    if torch.cuda.is_available():
        print(f"✅ 检测到 GPU: {torch.cuda.get_device_name(0)}")
        print(f"   显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB\n")
    else:
        print("⚠️  未检测到 CUDA，将使用 CPU\n")
    
    print("📦 加载模型到 GPU...")
    model = WhisperModel(
        "medium", 
        device="cuda" if torch.cuda.is_available() else "cpu",
        compute_type="float16" if torch.cuda.is_available() else "int8"
    )
    print("✅ 模型加载完成\n")
    
    print("🎤 开始识别（GPU 模式，预计 30-60 秒）...")
    import time
    start_time = time.time()
    
    segments, info = model.transcribe(
        str(audio_file),
        language="zh",
        beam_size=5,
        vad_filter=True,
    )
    
    elapsed = time.time() - start_time
    print(f"✅ 识别完成！耗时: {elapsed:.1f} 秒，语言: {info.language}\n")
    
    print("="*60)
    print("识别结果:")
    print("="*60)
    
    full_text = []
    for segment in segments:
        text = segment.text.strip()
        full_text.append(text)
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {text}")
    
    result = ''.join(full_text)
    
    print("\n" + "="*60)
    print("完整文案:")
    print("="*60)
    print(result)
    print(f"\n总字数: {len(result)}")
    
    # 保存结果
    output_file = Path("output/transcript.txt")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(result, encoding='utf-8')
    print(f"\n💾 已保存到: {output_file}")
    
    print(f"\n⚡ 性能: {len(result) / elapsed:.1f} 字/秒")
    
except Exception as e:
    print(f"\n❌ 识别失败: {e}")
    import traceback
    traceback.print_exc()
