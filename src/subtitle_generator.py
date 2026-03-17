import pysrt

def generate_subtitles(segments, translate_function, output_file, language):

    subs = pysrt.SubRipFile()

    for i, seg in enumerate(segments):

        translated_text = translate_function(seg["text"], language)

        sub = pysrt.SubRipItem(
            index=i + 1,
            start=pysrt.SubRipTime(seconds=seg["start"]),
            end=pysrt.SubRipTime(seconds=seg["end"]),
            text=translated_text
        )

        subs.append(sub)

    subs.save(output_file)
