"""
简化版 Whisper 识别 - 直接输出到文件
"""
from pathlib import Path
from faster_whisper import WhisperModel

audio_file = Path("temp/audio.mp3")
output_file = Path("output/transcript_final.txt")
output_file.parent.mkdir(exist_ok=True)

print("开始识别...")
model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, info = model.transcribe(str(audio_file), language="zh", beam_size=5, vad_filter=True)

full_text = []
for segment in segments:
    full_text.append(segment.text.strip())

result = ''.join(full_text)
output_file.write_text(result, encoding='utf-8')
print(f"完成！已保存到: {output_file}")
print(f"字数: {len(result)}")
