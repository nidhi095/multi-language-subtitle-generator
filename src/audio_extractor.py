"""
audio_extractor.py
------------------
Extracts audio from a video file using ffmpeg-python.
Outputs a 16kHz mono WAV — the format Whisper expects.
"""

import subprocess
from pathlib import Path


def extract_audio(
    video_path: Path,
    output_dir: Path = Path("audio"),
    sample_rate: int = 16000,
) -> Path:
    """
    Extract audio from a video file and save as a 16kHz mono WAV.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory to save the extracted audio.
        sample_rate: Target sample rate (default 16000 Hz for Whisper).

    Returns:
        Path to the extracted audio file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{video_path.stem}.wav"

    cmd = [
        "ffmpeg",
        "-y",               # overwrite if exists
        "-i", str(video_path),
        "-vn",              # no video
        "-acodec", "pcm_s16le",  # 16-bit PCM
        "-ar", str(sample_rate),
        "-ac", "1",         # mono
        str(audio_path),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"ffmpeg audio extraction failed:\n{error_msg}")

    return audio_path