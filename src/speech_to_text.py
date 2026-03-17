"""
speech_to_text.py
-----------------
Transcribes audio using OpenAI Whisper (local ML model).
Returns a list of timed subtitle segments.
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import torch


@dataclass
class Segment:
    """A single subtitle segment with timing and text."""
    start: float        # seconds
    end: float          # seconds
    text: str
    words: list = field(default_factory=list)  # word-level timestamps (optional)

    def __repr__(self):
        return f"Segment({self.start:.2f}s → {self.end:.2f}s | {self.text!r})"


def _resolve_device(device: str) -> str:
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def transcribe_audio(
    audio_path: Path,
    model_size: str = "large-v2",
    source_lang: Optional[str] = None,
    device: str = "auto",
    word_timestamps: bool = False,
) -> tuple[list[Segment], str]:
    """
    Transcribe audio using Whisper and return timed segments.

    Args:
        audio_path: Path to the WAV file.
        model_size: Whisper model variant.
        source_lang: ISO-639-1 language code (None = auto-detect).
        device: "cpu", "cuda", or "auto".
        word_timestamps: Whether to extract word-level timing.

    Returns:
        (segments, detected_language)
    """
    import whisper  # imported lazily so the rest of the codebase loads without it

    resolved_device = _resolve_device(device)
    print(f"      Loading whisper-{model_size} on {resolved_device}...")

    model = whisper.load_model(model_size, device=resolved_device)

    transcribe_kwargs = dict(
        word_timestamps=word_timestamps,
        verbose=False,
    )
    if source_lang:
        transcribe_kwargs["language"] = source_lang

    result = model.transcribe(str(audio_path), **transcribe_kwargs)

    detected_lang: str = result.get("language", "en")

    segments: list[Segment] = []
    for raw in result["segments"]:
        words = []
        if word_timestamps and "words" in raw:
            words = [
                {"word": w["word"], "start": w["start"], "end": w["end"]}
                for w in raw["words"]
            ]
        segments.append(
            Segment(
                start=float(raw["start"]),
                end=float(raw["end"]),
                text=raw["text"].strip(),
                words=words,
            )
        )

    return segments, detected_lang