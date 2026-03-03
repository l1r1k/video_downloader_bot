import subprocess
import asyncio
import os
from pathlib import Path

COMMAND = 'yt-dlp'
INFO_KEY='-F'
PATH_KEY = '-P'
OUTPUT_KEY = '-o'
OUTPUT_FORMAT = '%(id)s.%(ext)s'
FORMAT_KEY = '-f'
FORMAT_VALUE = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b'
FORMAT_FOR_TG = 'bv*[height<=1080][ext=mp4][vcodec^=hev1]+ba[ext=m4a]/bv*[height<=1080][ext=mp4][vcodec^=avc1]+ba[ext=m4a]/b[height<=1080][ext=mp4]'
COOKIES_KEY = '--cookies'
MAX_SIZE = 50 * 1024 * 1024 # 50 MB Max Size send video from bot with aiogram

async def get_video_id(url: str, path_to_cookies: str = None) -> tuple[str, str, str]:
    """
    Function to get video id from url. If path_to_cookies is not None, then it will be used for getting video id, else it will be used without cookies.
    Getting id for checking if video is already downloaded and for naming video file after downloading.
    """
    if path_to_cookies is None:
        proc = await asyncio.create_subprocess_exec(COMMAND, INFO_KEY, url, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    else:
        proc = await asyncio.create_subprocess_exec(COMMAND, INFO_KEY, COOKIES_KEY, path_to_cookies, url, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderror = await proc.communicate()
    stdout_str = stdout.decode()
    substring = 'Available formats for'
    stdout_str = stdout_str[stdout_str.find(substring):]
    video_id = stdout_str[:stdout_str.find(':')].split(' ')[-1]
    return video_id, stdout.decode(), stderror

async def check_video_size(url: str, path_to_cookies: str = None) -> tuple[bool, str, str]:
    """
    Function for checking video size. If vide size is less than MAX_SIZE, than it will return True, else return False.
    Because Telegram Bot API has a limit of 50 MB for sending video files, so if video is bigger than 50 MB, if user 
    select save and no_sending_back option, video will be downloaded and saved on local folders
    """
    if path_to_cookies is None:
        proc = await asyncio.create_subprocess_exec(COMMAND, '--print', 'filesize', url, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    else:
        proc = await asyncio.create_subprocess_exec(COMMAND, COOKIES_KEY, path_to_cookies, '--print', 'filesize', url, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderror = await proc.communicate()
    stdout_value = stdout.decode().strip()
    if stdout_value.isdigit():
        filesize = int(stdout_value)
    else:
        filesize = None
    return filesize is None or filesize < MAX_SIZE, stdout.decode(), stderror

async def correct_video(path_to_video: str) -> tuple[str, str, str]:
    """
    Function correct video with ffmpeg, because some videos can be downloaded with vcodec
    that telegram doesn't support. For example, if video is downloaded with vcodec HEVC, 
    it will be corrected to H264, because Telegram supports H264, but doesn't support HEVC.
    """
    video_path = Path(path_to_video)
    temp_output = video_path.with_name(video_path.stem + '.tmp.mp4')
    proc = await asyncio.create_subprocess_exec(
        'ffmpeg', '-y', '-fflags', '+genpts', '-i', str(video_path), '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-profile:v', 'high', '-level', '4.0', '-r', '30', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '128k',
        str(temp_output), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
    stdout, stderror = await proc.communicate()
    os.replace(temp_output, video_path)
    return path_to_video, stdout, stderror

async def download_video_async(url: str, path_to_save: str, video_id: str, no_send_back_type: int, path_to_cookies: str = None) -> tuple[str, str, str]:
    """
    Function download video from url with yt-dlp.
    If path_to_cookies is not None, then it will be used for downloading video
    from Instagram Reels, because Instagram Reels has limit for downloading 2 videos
    without login.
    """
    if path_to_cookies is None:
        proc = await asyncio.create_subprocess_exec(COMMAND, PATH_KEY, path_to_save, OUTPUT_KEY, OUTPUT_FORMAT, FORMAT_KEY, f"{FORMAT_VALUE if no_send_back_type else FORMAT_FOR_TG}", url, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    else:
        proc = await asyncio.create_subprocess_exec(COMMAND, PATH_KEY, path_to_save, OUTPUT_KEY, OUTPUT_FORMAT, FORMAT_KEY, FORMAT_VALUE, COOKIES_KEY, path_to_cookies, url, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    return f'{path_to_save}/{video_id}.mp4', stdout.decode(), stderr.decode

def download_video(url: str, path_to_save: str, video_id: str) -> str:
    result = subprocess.run([COMMAND, PATH_KEY, path_to_save, OUTPUT_KEY, OUTPUT_FORMAT, FORMAT_KEY, FORMAT_VALUE, url], capture_output=True)
    return f'{path_to_save}/{video_id}.mp4'

# if __name__ == '__main__':
    # print(asyncio.run(get_video_id('https://www.instagram.com/reel/DVVgH70jKLG/?igsh=MWFka3duazQycWJxeA==')))