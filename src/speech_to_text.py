import whisper

def transcribe_audio(audio_path):

    model = whisper.load_model("base")

    result = model.transcribe(audio_path)

    segments = result["segments"]

    return segments, result["text"]
