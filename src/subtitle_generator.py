"""
subtitle_generator.py
----------------------
Converts a list of Segment objects into SRT and WebVTT subtitle files.
"""

from __future__ import annotations
from pathlib import Path
from src.speech_to_text import Segment


# ─── Formatting helpers ───────────────────────────────────────────────────────

def _seconds_to_srt_time(seconds: float) -> str:
    """Convert float seconds → SRT timestamp  HH:MM:SS,mmm"""
    ms = int(round(seconds * 1000))
    h = ms // 3_600_000
    ms %= 3_600_000
    m = ms // 60_000
    ms %= 60_000
    s = ms // 1_000
    ms %= 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _seconds_to_vtt_time(seconds: float) -> str:
    """Convert float seconds → WebVTT timestamp  HH:MM:SS.mmm"""
    ms = int(round(seconds * 1000))
    h = ms // 3_600_000
    ms %= 3_600_000
    m = ms // 60_000
    ms %= 60_000
    s = ms // 1_000
    ms %= 1_000
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


# ─── SRT ──────────────────────────────────────────────────────────────────────

def generate_srt(segments: list[Segment], output_path: Path) -> Path:
    """
    Write an SRT subtitle file from a list of Segment objects.

    Args:
        segments: Timed text segments.
        output_path: Destination .srt file.

    Returns:
        Path to the written file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []

    for i, seg in enumerate(segments, start=1):
        start = _seconds_to_srt_time(seg.start)
        end = _seconds_to_srt_time(seg.end)
        text = seg.text.strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


# ─── WebVTT ───────────────────────────────────────────────────────────────────

def generate_vtt(segments: list[Segment], output_path: Path) -> Path:
    """
    Write a WebVTT subtitle file from a list of Segment objects.

    Args:
        segments: Timed text segments.
        output_path: Destination .vtt file.

    Returns:
        Path to the written file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["WEBVTT", ""]  # required header

    for i, seg in enumerate(segments, start=1):
        start = _seconds_to_vtt_time(seg.start)
        end = _seconds_to_vtt_time(seg.end)
        text = seg.text.strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path