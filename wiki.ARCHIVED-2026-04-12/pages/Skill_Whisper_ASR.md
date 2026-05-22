---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- mlops
- multimodal
audience:
- engineers
- researchers
- operators
difficulty: intermediate
prerequisites:
- MCP_Tools
tags:
- whisper
- speech-recognition
- asr
- multimodal
- multilingual
- transcription
- translation
- audio-processing
- openai
sources:
- Hermes official skill: official/mlops/whisper
- OpenAI Whisper GitHub: https://github.com/openai/whisper
- Paper: https://arxiv.org/abs/2212.04356
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: Whisper — Speech Recognition

**Whisper** is OpenAI's general-purpose speech recognition model. Supports 99 languages, transcription, translation to English, and language identification. Six model sizes from tiny (39M params) to large (1550M params). Best for robust, multilingual ASR in the federation.

## Purpose

To give federation agents speech-to-text capability:
- Transcribe audio/video in 99 languages
- Translate non-English audio to English text
- Generate subtitles (SRT, VTT, JSON)
- Automate meeting notes and podcast transcription
- Process noisy or multilingual audio

## Specifications

- **Stage**: 111 (Sensing)
- **Layer**: MACHINE
- **Trinity**: Δ (Mind — grounding audio into text)
- **Floors touched most directly**: F2 (Truth — transcription accuracy), F4 (Guardrails — language/content boundaries), F9 (Anti-Hantu — audio must not bypass text filters)

## Installation

```bash
# Python package
pip install -U openai-whisper

# ffmpeg (required)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
```

**Installed on**: `/root` (VPS host, Hermes venv)  
**ffmpeg**: `/usr/bin/ffmpeg` v7.1.1  
**Whisper version**: 20250625  
**License**: MIT

## Model Sizes

| Model | Parameters | English-only | Multilingual | Speed | VRAM |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **tiny** | 39M | ✓ | ✓ | ~32× | ~1 GB |
| **base** | 74M | ✓ | ✓ | ~16× | ~1 GB |
| **small** | 244M | ✓ | ✓ | ~6× | ~2 GB |
| **medium** | 769M | ✓ | ✓ | ~2× | ~5 GB |
| **large** | 1550M | ✗ | ✓ | 1× | ~10 GB |
| **turbo** | 809M | ✗ | ✓ | ~8× | ~6 GB |

**Recommendation**: Use `turbo` for best speed/quality tradeoff. Use `base` or `tiny` for quick prototyping.

## Basic Usage

### Python API
```python
import whisper

# Load model
model = whisper.load_model("turbo")

# Transcribe
result = model.transcribe("audio.mp3")
print(result["text"])

# Access segments with timestamps
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

### CLI
```bash
# Basic transcription
whisper audio.mp3

# Specify model
whisper audio.mp3 --model turbo

# Output formats
whisper audio.mp3 --output_format txt     # Plain text
whisper audio.mp3 --output_format srt     # Subtitles
whisper audio.mp3 --output_format vtt     # WebVTT
whisper audio.mp3 --output_format json    # JSON with timestamps

# Language
whisper audio.mp3 --language Spanish

# Translation to English
whisper spanish.mp3 --task translate
```

## Advanced Options

### Language specification
```python
# Auto-detect (slower)
result = model.transcribe("audio.mp3")

# Specify language (faster)
result = model.transcribe("audio.mp3", language="en")

# Supported: en, es, fr, de, it, pt, ru, ja, ko, zh, and 89 more
```

### Task selection
```python
# Transcription (default)
result = model.transcribe("audio.mp3", task="transcribe")

# Translation to English
result = model.transcribe("spanish.mp3", task="translate")
```

### Initial prompt
```python
# Improve accuracy with domain context
result = model.transcribe(
    "audio.mp3",
    initial_prompt="This is a technical podcast about machine learning and AI."
)
```

### Word-level timestamps
```python
result = model.transcribe("audio.mp3", word_timestamps=True)

for segment in result["segments"]:
    for word in segment["words"]:
        print(f"{word['word']} ({word['start']:.2f}s - {word['end']:.2f}s)")
```

### Temperature fallback
```python
# Retry with different temperatures if confidence low
result = model.transcribe(
    "audio.mp3",
    temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
)
```

## GPU Acceleration

```python
import whisper

# Automatically uses GPU if available
model = whisper.load_model("turbo")

# Force CPU
model = whisper.load_model("turbo", device="cpu")

# Force GPU
model = whisper.load_model("turbo", device="cuda")
```

**10-20× faster on GPU.**

## Batch Processing

```python
import os
import whisper

model = whisper.load_model("turbo")
audio_files = ["file1.mp3", "file2.mp3", "file3.mp3"]

for audio_file in audio_files:
    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)
    output_file = audio_file.replace(".mp3", ".txt")
    with open(output_file, "w") as f:
        f.write(result["text"])
```

## Real-time / Faster Alternative

For streaming or real-time use cases, use `faster-whisper` (CTranslate2 backend):

```bash
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="float16")
segments, info = model.transcribe("audio.mp3", beam_size=5)

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

**4× faster than openai-whisper.**

## Integration Patterns

### Subtitle generation
```bash
whisper video.mp4 --output_format srt --language English
# Output: video.srt
```

### Extract audio from video
```bash
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav
whisper audio.wav
```

### With LangChain RAG
```python
from langchain.document_loaders import WhisperTranscriptionLoader

loader = WhisperTranscriptionLoader(file_path="audio.mp3")
docs = loader.load()

# Feed into vector store
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
```

## Federation Context

- **Hermes**: Skill installed at `~/.hermes/skills/mlops/whisper/`
- **A-FORGE / arifOS**: Can invoke via ShellTool or Python subprocess
- **GPU**: This VPS may not have a GPU; use `tiny` or `base` model for CPU inference
- **Storage**: Model weights cached at `~/.cache/whisper/` after first download

## Best Practices

| Tip | Why |
| :--- | :--- |
| Use `turbo` model | Best speed/quality for English |
| Specify language | Faster than auto-detect |
| Add initial prompt | Improves technical terms and proper nouns |
| Use GPU if available | 10-20× faster |
| Batch process | More efficient than one-at-a-time |
| Convert to WAV first | Better compatibility with ffmpeg |
| Split long audio | <30 min chunks for best accuracy |
| Use `faster-whisper` | 4× speedup for production pipelines |

## Limitations

| Issue | Mitigation |
| :--- | :--- |
| Hallucinations (repeated/invented text) | Use lower temperature, post-process |
| Long-form accuracy degradation (>30 min) | Split audio into chunks |
| No speaker diarization | Use AssemblyAI or pyannote.audio separately |
| Accent variation | Use larger model or fine-tune |
| Background noise | Pre-process with noise reduction |
| Not suitable for live captioning | Use `faster-whisper` with streaming |

## Performance

| Model | Real-time factor (CPU) | Real-time factor (GPU) |
| :--- | :--- | :--- |
| tiny | ~0.32 | ~0.01 |
| base | ~0.16 | ~0.01 |
| turbo | ~0.08 | ~0.01 |
| large | ~1.0 | ~0.05 |

*Real-time factor: 0.1 = 10× faster than real-time*

## Related

- [[Skill_Chroma_Vector_DB]] (Store transcriptions in vector DB for RAG)
- [[Skill_Qdrant_Vector_DB]] (Production vector search for transcription retrieval)
- [[Skill_Inference_CLI]] (Alternative: cloud ASR APIs via inference.sh)
- [[MCP_Tools]] (Tool surface architecture)
