import subprocess
import os
from django_rq import job
from dotenv import load_dotenv


load_dotenv()

ffmpeg_path = r'/usr/bin/ffmpeg'
RESOLUTIONS = {
    '240p': 'scale=426:240',
    '360p': 'scale=640:360',
    '480p': 'scale=854:480',
    '720p': 'scale=1280:720',
    '1080p': 'scale=1920:1080',
}

def run_ffmpeg_command(cmd):
    """
    Runs an ffmpeg command, checks for errors and prints them if there are any
    :param cmd: The list of arguments to pass to ffmpeg
    :return: The return code of the ffmpeg command
    """
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr.decode()}")
    return result.returncode

def convert_video_to_hls(video_path):
    """
    Converts a video file to multiple HLS streams with different resolutions.

    This function takes a video file path, and for each predefined resolution,
    creates an HLS (HTTP Live Streaming) output directory containing the playlist
    and segment files. The conversion is performed using ffmpeg with specified
    video and audio codecs.

    :param video_path: The file path of the input video to be converted.
    """
    video_basename = os.path.splitext(video_path)[0]

    for resolution, scale in RESOLUTIONS.items():
        hls_output_dir = f"{video_basename}_{resolution}_hls"
        os.makedirs(hls_output_dir, exist_ok=True)

        hls_playlist = os.path.join(hls_output_dir, f"index.m3u8")

        cmd = [
            ffmpeg_path, '-i', video_path,
            '-vf', scale,
            '-c:v', 'libx264', '-crf', '23',
            '-c:a', 'aac', '-strict', '-2',
            '-f', 'hls',
            '-hls_time', '5',
            '-hls_playlist_type', 'vod',
            hls_playlist
        ]

        return_code = run_ffmpeg_command(cmd)
        if return_code != 0:
            print(f"Error: Failed to convert video to {resolution}")

@job('default')
def process_video(instance):
    """
    Job to convert a Video instance's video_file to HLS (HTTP Live Streaming)
    format.

    The function takes an instance of the Video model as an argument, checks if
    the video file exists, and if yes, converts it to HLS format using ffmpeg.

    The converted video is saved in separate folders with the same name as the
    original video but with the appended resolution (e.g. "video_240p_hls").

    :param instance: An instance of the Video model
    :return: None
    """
    if not os.path.exists(instance.video_file.path):
        return

    convert_video_to_hls(instance.video_file.path)

    if instance.video_file:
        instance.save()