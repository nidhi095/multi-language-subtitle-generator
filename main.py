import argparse
import sys
from pathlib import Path
from src.audio_extractor import extract_audio
from src.speech_to_text import transcribe_audio
from src.translator import translate_subtitles
from src.subtitle_generator import generate_srt, generate_vtt
from src.video_overlay import overlay_subtitles

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "it": "Italian",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="ML-based Multi-Language Subtitle Generator"
    )
    parser.add_argument("input_video", help="Path to input video file")
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["en"],
        help=f"Target languages. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}",
    )
    parser.add_argument(
        "--source-lang",
        default=None,
        help="Source language of the video (auto-detected if not specified)",
    )
    parser.add_argument(
        "--model",
        default="large-v2",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="Whisper model size (larger = more accurate but slower)",
    )
    parser.add_argument(
        "--output-dir",
        default="subtitles",
        help="Directory to save subtitle files",
    )
    parser.add_argument(
        "--overlay",
        action="store_true",
        help="Burn subtitles into the video (requires ffmpeg)",
    )
    parser.add_argument(
        "--overlay-lang",
        default=None,
        help="Language to use for video overlay (defaults to first target language)",
    )
    parser.add_argument(
        "--format",
        choices=["srt", "vtt", "both"],
        default="srt",
        help="Subtitle file format",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Device to run ML models on",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate input
    input_path = Path(args.input_video)
    if not input_path.exists():
        print(f"[ERROR] Input video not found: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate languages
    for lang in args.languages:
        if lang not in SUPPORTED_LANGUAGES:
            print(f"[ERROR] Unsupported language: {lang}")
            print(f"Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}")
            sys.exit(1)

    print(f"\n{'='*60}")
    print("  ML Multi-Language Subtitle Generator")
    print(f"{'='*60}")
    print(f"  Input  : {input_path.name}")
    print(f"  Langs  : {', '.join(args.languages)}")
    print(f"  Model  : whisper-{args.model}")
    print(f"  Device : {args.device}")
    print(f"{'='*60}\n")

    # Step 1: Extract audio
    print("[1/4] Extracting audio from video...")
    audio_path = extract_audio(input_path)
    print(f"      Audio saved to: {audio_path}\n")

    # Step 2: Transcribe
    print(f"[2/4] Transcribing with Whisper ({args.model})...")
    segments, detected_lang = transcribe_audio(
        audio_path,
        model_size=args.model,
        source_lang=args.source_lang,
        device=args.device,
    )
    print(f"      Detected language: {SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)}")
    print(f"      Segments found: {len(segments)}\n")

    # Step 3: Translate + generate subtitles per language
    print("[3/4] Translating and generating subtitles...")
    generated_files = []

    for lang in args.languages:
        lang_name = SUPPORTED_LANGUAGES[lang]
        print(f"      → {lang_name} ({lang})...")

        if lang == detected_lang:
            translated_segments = segments
        else:
            translated_segments = translate_subtitles(segments, target_lang=lang)

        stem = input_path.stem
        if args.format in ("srt", "both"):
            srt_path = output_dir / f"{stem}.{lang}.srt"
            generate_srt(translated_segments, srt_path)
            generated_files.append(srt_path)
            print(f"        SRT: {srt_path}")

        if args.format in ("vtt", "both"):
            vtt_path = output_dir / f"{stem}.{lang}.vtt"
            generate_vtt(translated_segments, vtt_path)
            generated_files.append(vtt_path)
            print(f"        VTT: {vtt_path}")

    print()

    # Step 4: Optional overlay
    if args.overlay:
        overlay_lang = args.overlay_lang or args.languages[0]
        stem = input_path.stem
        subtitle_for_overlay = output_dir / f"{stem}.{overlay_lang}.srt"

        if not subtitle_for_overlay.exists():
            print(f"[WARNING] Subtitle file not found for overlay: {subtitle_for_overlay}")
        else:
            print(f"[4/4] Burning subtitles ({overlay_lang}) into video...")
            output_video = Path("output_video") / f"{stem}.{overlay_lang}.mp4"
            output_video.parent.mkdir(parents=True, exist_ok=True)
            overlay_subtitles(input_path, subtitle_for_overlay, output_video)
            print(f"      Output video: {output_video}\n")
    else:
        print("[4/4] Skipping video overlay (use --overlay to enable)\n")

    print(f"{'='*60}")
    print(f"  Done! Generated {len(generated_files)} subtitle file(s).")
    print(f"  Output dir: {output_dir.resolve()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()