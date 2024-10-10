import subprocess


def convert_video(source):
        
        resolutions = {
        '240p': 'scale=426:240',
        '360p': 'scale=640:360',
        '480p': 'scale=854:480',
        '720p': 'scale=1280:720',
        '1080p': 'scale=1920:1080',
    }
        ffmpeg_path = r"C:\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
                
        for resolution, scale in resolutions.items():
            new_file_name = source.replace('.mp4', f'_{resolution}.mp4')
            cmd = [ffmpeg_path, '-i', source, '-vf', scale, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', new_file_name]
            subprocess.run(cmd, capture_output=True)
