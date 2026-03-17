from src.audio_extractor import extract_audio
from src.speech_to_text import transcribe_audio
from src.translator import translate_text
from src.subtitle_generator import generate_subtitles
from src.video_overlay import overlay_subtitles


VIDEO_PATH = "input_video/sample.mp4"
AUDIO_PATH = "audio/audio.wav"
OUTPUT_VIDEO = "output_video/subtitled_video.mp4"


def main():

    language = input("Choose subtitle language (english / hindi / kannada): ").lower()

    subtitle_file = f"subtitles/output_{language}.srt"

    print("Extracting audio...")
    extract_audio(VIDEO_PATH, AUDIO_PATH)

    print("Transcribing speech...")
    segments, text = transcribe_audio(AUDIO_PATH)

    print("Generating subtitles...")
    generate_subtitles(segments, translate_text, subtitle_file, language)

    print("Overlaying subtitles...")
    overlay_subtitles(VIDEO_PATH, subtitle_file, OUTPUT_VIDEO)

    print("Finished!")
    print("Output video:", OUTPUT_VIDEO)


if __name__ == "__main__":
    main()
