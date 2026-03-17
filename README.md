# ML Multi-Language Subtitle Generator

Generates accurate, timed subtitles for any video using:
- **OpenAI Whisper** — state-of-the-art speech-to-text (local, offline)
- **Helsinki-NLP MarianMT** — neural machine translation for 12 languages
- **ffmpeg** — audio extraction and optional subtitle burning

---

## Architecture

```
input_video
    │
    ▼
[audio_extractor.py]  ← ffmpeg: extract 16kHz mono WAV
    │
    ▼
[speech_to_text.py]   ← Whisper: transcribe → List[Segment]
    │
    ▼
[translator.py]       ← MarianMT: translate segments per language
    │
    ▼
[subtitle_generator.py] ← write .srt / .vtt files
    │
    ▼ (optional)
[video_overlay.py]    ← ffmpeg: burn subtitles into video
```

---

## Setup

```bash
# 1. Create & activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install ffmpeg (system-level)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
# Windows: https://ffmpeg.org/download.html
```

---

## Usage

### Basic — English subtitles only
```bash
python main.py input_video/my_video.mp4
```

### Multi-language subtitles
```bash
python main.py input_video/my_video.mp4 --languages en hi es fr de
```

### Use a larger model for better accuracy
```bash
python main.py input_video/my_video.mp4 \
    --languages en hi \
    --model large-v3
```

### Burn subtitles into the video
```bash
python main.py input_video/my_video.mp4 \
    --languages en hi \
    --overlay \
    --overlay-lang hi
```

### Generate WebVTT (for web players)
```bash
python main.py input_video/my_video.mp4 \
    --languages en fr \
    --format vtt
```

### Force GPU / CPU
```bash
python main.py input_video/my_video.mp4 --device cuda
python main.py input_video/my_video.mp4 --device cpu
```

---

## Supported Languages

| Code | Language   | Code | Language   |
|------|-----------|------|-----------|
| en   | English   | ar   | Arabic    |
| hi   | Hindi     | pt   | Portuguese|
| es   | Spanish   | ru   | Russian   |
| fr   | French    | ja   | Japanese  |
| de   | German    | ko   | Korean    |
| zh   | Chinese   | it   | Italian   |

---

## Model Size vs. Accuracy Tradeoff

| Model     | VRAM  | Speed   | WER  |
|-----------|-------|---------|------|
| tiny      | ~1 GB | fastest | ~15% |
| base      | ~1 GB | fast    | ~10% |
| small     | ~2 GB | fast    | ~8%  |
| medium    | ~5 GB | medium  | ~5%  |
| large-v2  | ~10GB | slow    | ~3%  |
| large-v3  | ~10GB | slow    | ~3%  |

`large-v2` is the recommended default for production use.

---

## Output

- **`subtitles/`** — `.srt` and/or `.vtt` files, one per language
  - e.g. `subtitles/my_video.en.srt`, `subtitles/my_video.hi.srt`
- **`output_video/`** — burned-in video (if `--overlay` used)
- **`audio/`** — extracted WAV (intermediate, can be deleted)

---

## Notes

- Translation uses a **pivot through English** for non-English → non-English pairs (e.g. Hindi → Spanish goes hi→en→es).
- MarianMT models are downloaded automatically from HuggingFace on first use and cached locally in `~/.cache/huggingface/`.
- For GPU acceleration on CUDA, install `torch` with CUDA support from [pytorch.org](https://pytorch.org/get-started/locally/).