from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import pysrt

def overlay_subtitles(video_path, subtitle_file, output_video):

    video = VideoFileClip(video_path)

    subs = pysrt.open(subtitle_file)

    subtitle_clips = []

    for sub in subs:

        txt_clip = (
            TextClip(
                sub.text,
                fontsize=40,
                color="white",
                bg_color="black"
            )
            .set_start(sub.start.ordinal / 1000)
            .set_end(sub.end.ordinal / 1000)
            .set_position(("center", "bottom"))
        )

        subtitle_clips.append(txt_clip)

    final = CompositeVideoClip([video] + subtitle_clips)

    final.write_videofile(output_video)
