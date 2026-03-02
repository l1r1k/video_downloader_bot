import os
import sys
from excps import *

check_yt_dlp = os.system('yt-dlp --version')
check_ffmpeg = os.system('ffmpeg -version')
check_ffprobe = os.system('ffprobe -version')
check_python = os.system('python --version | python3 --version')
python_version = sys.version_info
major_version = python_version[0] >= 3
minor_version = python_version[1] >= 10

def check():
    if check_yt_dlp != 0:
        raise RequiredPackageNotInstalledOrNotFound('Required package yt-dlp not found. Please install it from github!')

    if check_ffmpeg != 0:
        raise RequiredPackageNotInstalledOrNotFound('Required package ffmpeg not found. Please install it with your package manager!')

    if check_ffprobe != 0:
        raise RequiredPackageNotInstalledOrNotFound('Required package ffprobe not found. Please install it with your package manager!')

    if not (major_version and minor_version):
        raise RequiredPackageNotInstalledOrNotFound(f'For good work package yt-dlp you need upgrade your Python version from {major_version}.{minor_version} to 3.10+!')
    
    os.system('cls' if os.name == 'nt' else 'clear')