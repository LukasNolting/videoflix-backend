import subprocess
import os
from django_rq import job
from dotenv import load_dotenv

load_dotenv()

ffmpeg_path = os.getenv('FFMPEG_PATH')
RESOLUTIONS = {
    '240p': 'scale=426:240',
    '360p': 'scale=640:360',
    '480p': 'scale=854:480',
    '720p': 'scale=1280:720',
    '1080p': 'scale=1920:1080',
}

def run_ffmpeg_command(cmd):
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"Fehler: {result.stderr.decode()}")
    return result.returncode

def convert_video_to_hls(video_path):
    print(f"Original video_path: {video_path}")
    video_basename = os.path.splitext(video_path)[0]
    print(f"video_basename: {video_basename}")

    for resolution, scale in RESOLUTIONS.items():
        hls_output_dir = f"{video_basename}_{resolution}_hls"
        print(f"hls_output_dir: {hls_output_dir}")
        os.makedirs(hls_output_dir, exist_ok=True)

        hls_playlist = os.path.join(hls_output_dir, f"index.m3u8")
        print(f"hls_playlist: {hls_playlist}")

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
            print(f"Fehler bei der Konvertierung in {resolution}")

@job('default')
def process_video(instance):
    print(f'instance: {instance.video_file.path}')
    if not os.path.exists(instance.video_file.path):
        print(f"Fehler: Die Datei {instance.video_file.path} existiert nicht.")
        return

    convert_video_to_hls(instance.video_file.path)

    if instance.video_file:
        print('Video wurde erfolgreich in das HLS-Format konvertiert')
        instance.save()