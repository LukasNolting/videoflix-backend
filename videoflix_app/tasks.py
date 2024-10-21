import subprocess
import os

ffmpeg_path = r"C:\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
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

def convert_video_to_hls(source):
    video_basename = os.path.splitext(source)[0]

    for resolution, scale in RESOLUTIONS.items():
        hls_output_dir = f"{video_basename}_{resolution}_hls"
        os.makedirs(hls_output_dir, exist_ok=True)

        hls_playlist = os.path.join(hls_output_dir, f"index.m3u8")
        cmd = [
            ffmpeg_path, '-i', source,
            '-vf', scale,
            '-c:v', 'libx264', '-crf', '23',
            '-c:a', 'aac', '-strict', '-2',
            '-f', 'hls', 
            '-hls_time', '5', 
            '-hls_playlist_type', 'vod', 
            hls_playlist
        ]
        run_ffmpeg_command(cmd)

def process_video(instance):
    convert_video_to_hls(instance.video_file.path)
    if instance.video_file:
        print('Video was converted to HLS format')
        instance.save()
