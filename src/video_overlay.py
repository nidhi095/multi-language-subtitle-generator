"""
video_overlay.py
----------------
Burns (hard-codes) subtitles into a video using ffmpeg's subtitles filter.
Requires ffmpeg with libass support.
"""

from __future__ import annotations
import subprocess
from pathlib import Path


def overlay_subtitles(
    video_path: Path,
    subtitle_path: Path,
    output_path: Path,
    font_size: int = 24,
    font_color: str = "white",
    outline_color: str = "black",
    outline_width: int = 2,
    position: str = "bottom",  # "bottom" or "top"
    video_codec: str = "libx264",
    audio_codec: str = "aac",
    crf: int = 18,
) -> Path:
    """
    Burn subtitles into a video using ffmpeg subtitles filter.

    Args:
        video_path: Input video file.
        subtitle_path: SRT subtitle file to embed.
        output_path: Output video file path.
        font_size: Subtitle font size in points.
        font_color: Subtitle text colour (CSS/ASS colour name or hex).
        outline_color: Outline/shadow colour.
        outline_width: Outline thickness in pixels.
        position: Vertical position — "bottom" (default) or "top".
        video_codec: Video codec for output (default libx264).
        audio_codec: Audio codec for output (default aac).
        crf: Constant Rate Factor for quality (lower = better, 18 is near-lossless).

    Returns:
        Path to the output video.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ASS/libass style string
    margin_v = 20
    alignment = 2 if position == "bottom" else 6  # ASS alignment codes

    style = (
        f"FontSize={font_size},"
        f"PrimaryColour=&H00FFFFFF,"  # white with full opacity (ABGR)
        f"OutlineColour=&H00000000,"  # black outline
        f"Outline={outline_width},"
        f"Shadow=1,"
        f"Alignment={alignment},"
        f"MarginV={margin_v}"
    )

    # Escape the subtitle path for ffmpeg filter (Windows backslash safe)
    escaped_sub = str(subtitle_path).replace("\\", "/").replace(":", "\\:")

    subtitle_filter = f"subtitles='{escaped_sub}':force_style='{style}'"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", subtitle_filter,
        "-c:v", video_codec,
        "-crf", str(crf),
        "-preset", "fast",
        "-c:a", audio_codec,
        "-b:a", "192k",
        str(output_path),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"ffmpeg subtitle overlay failed:\n{error_msg}")

    return output_path


def embed_subtitle_track(
    video_path: Path,
    subtitle_path: Path,
    output_path: Path,
    lang: str = "en",
    title: str = "",
) -> Path:
    """
    Mux a subtitle file as a soft (selectable) track inside an MKV container.
    Does NOT burn; viewers can toggle it on/off.

    Args:
        video_path: Input video file.
        subtitle_path: SRT/VTT subtitle file.
        output_path: Output .mkv file path.
        lang: BCP-47 language code for the subtitle track.
        title: Human-readable track title shown in media players.

    Returns:
        Path to the output video.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-i", str(subtitle_path),
        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "srt",
        "-metadata:s:s:0", f"language={lang}",
        "-metadata:s:s:0", f"title={title or lang}",
        "-disposition:s:0", "default",
        str(output_path),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"ffmpeg track mux failed:\n{error_msg}")

    return output_path