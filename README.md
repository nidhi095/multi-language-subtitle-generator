# Multi-Language Subtitle Generator

AI system that generates subtitles from videos and translates them into multiple languages.

Languages supported:
- English
- Hindi
- Kannada

Pipeline:
Video → Audio Extraction → Whisper Speech Recognition → NLLB Translation → Subtitle Generation → Video Overlay

Run:

pip install -r requirements.txt
python main.py
