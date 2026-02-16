"""
直接测试 Whisper
"""
from pathlib import Path

audio_file = Path("temp/audio.mp3")

if not audio_file.exists():
    print(f"❌ 音频文件不存在: {audio_file}")
    exit(1)

print("="*60)
print("直接测试 Whisper 语音识别")
print("="*60)
print(f"\n音频文件: {audio_file}")
print(f"文件大小: {audio_file.stat().st_size / 1024:.2f} KB\n")

try:
    from faster_whisper import WhisperModel
    
    print("📦 加载模型...")
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    print("✅ 模型加载完成\n")
    
    print("🎤 开始识别（5分钟音频，预计需要 2-5 分钟）...")
    segments, info = model.transcribe(
        str(audio_file),
        language="zh",
        beam_size=5,
        vad_filter=True,
    )
    
    print(f"✅ 识别完成！语言: {info.language}\n")
    
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
    
    # 保存结果
    output_file = Path("output/transcript.txt")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(result, encoding='utf-8')
    print(f"\n💾 已保存到: {output_file}")
    
except Exception as e:
    print(f"\n❌ 识别失败: {e}")
    import traceback
    traceback.print_exc()
