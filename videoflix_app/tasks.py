import subprocess

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

def convert_video(source):
        
    
    for resolution, scale in RESOLUTIONS.items():
        new_file_name = source.replace('.mp4', f'_{resolution}.mp4')
        cmd = [
            ffmpeg_path, '-i', source,
            '-vf', scale,
            '-c:v', 'libx264', '-crf', '23',
            '-c:a', 'aac', '-strict', '-2', new_file_name
        ]
        run_ffmpeg_command(cmd)


def process_video(instance):
    convert_video(instance.video_file.path)

    if instance.video_file:
        print('Video was converted')

        instance.save()  
