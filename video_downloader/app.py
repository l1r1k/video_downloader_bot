# Extended dependencies
import argparse
import asyncio
import logging
import os
import pytz
from datetime import datetime
# Telegram Bot API dependencies
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import SimpleI18nMiddleware
# ENV dependencies
from decouple import config
# Install function
from download_video import (
    download_video_async,
    get_video_id,
    correct_video,
    check_video_size
)
# Localfiles dependencies
from check_dependencies import check
# Custom exceptions
from excps import RequiredPackageNotInstalledOrNotFound

# Const variable block
BOT_TOKEN = config('BOT_TOKEN', default=None) # Telegram api bot token
ADMIN_ID = config('ADMIN_ID', default=None) # Admin of telegram bot for get notification of errors
PATH_TO_COOKIES = config('PATH_TO_COOKIES', default=None) # Path to cookies for downloading Instagram Reels
# Available platforms and path to dir
PLATFORMS = {
    'youtube': 'youtube_videos',
    'youtu': 'youtube_videos',
    'tiktok': 'tiktok_videos',
    'instagram': 'inst_reels_videos',
    'twitch': 'twitch_videos'
}

dp = Dispatcher()
# Check was bot token entered in .env file
if BOT_TOKEN:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
else:
    raise Exception('Not found telegram api bot token in .env. Please, enter took token from BotFather and enter in .env!')
# Configure translation engine
i18n = I18n(
    path='locales',
    default_locale='en',
    domain='messages'
)
# Add parser for reading values that entered in terminal when bot running
parser = argparse.ArgumentParser(description='VideoDownloaderTelegramBot')
# Configure args
parser.add_argument('--save', action='store', dest='save', default=0) # 0 - no save video in folders, 1 - save video in folders.
parser.add_argument('--no-send-back', action='store', dest='no_send_back', default=0) # 0 - send back video to user, 1 - no send back video to user, just save
# Read arguments from terminal
args = parser.parse_args()
save_type = args.save
no_send_back_type = args.no_send_back
# Create and add engine for translation
i18n_middleware = SimpleI18nMiddleware(i18n)
dp.update.middleware(i18n_middleware)
# If local dirs not exist - create them
if not os.path.exists('youtube_videos'):
    os.makedirs('youtube_videos')
if not os.path.exists('tiktok_videos'):
    os.makedirs('tiktok_videos')
if not os.path.exists('inst_reels_videos'):
    os.makedirs('inst_reels_videos')
if not os.path.exists('twitch_videos'):
    os.makedirs('twitch_videos')
# If dirs for local save in best quality not exist - create them
if not os.path.exists('youtube_videos/locals'):
    os.makedirs('youtube_videos/locals')
if not os.path.exists('tiktok_videos/locals'):
    os.makedirs('tiktok_videos/locals')
if not os.path.exists('inst_reels_videos/locals'):
    os.makedirs('inst_reels_videos/locals')
if not os.path.exists('twitch_videos/locals'):
    os.makedirs('twitch_videos/locals')

def is_message_valid_url(message: str) -> bool:
    """
    Function for checking is message from user it's a url
    """
    return message.find('http') >= 0

def get_url_from_message(message: str) -> str:
    """
    Function for getting url from message
    """
    start_index_of_url = message.find('http')
    return message[start_index_of_url:]

def is_platform_from_url_available(url: str) -> bool:
    """
    Function for checking is url from user is available for downloading
    """
    for available_platform in PLATFORMS.keys():
        if url.find(available_platform) >= 0:
            return True
    return False

def get_folder_to_save(url: str) -> str:
    """
    Function for getting folder to save for video from platform
    """
    for available_platform, folder_to_save in PLATFORMS.items():
        if url.find(available_platform) >= 0:
            if no_send_back_type:
                return folder_to_save+'/locals'
            return folder_to_save
    return None

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Handler function for /start command
    """
    username = message.from_user.username
    await message.answer(
        _('Hello, {name}! This is app for downloading any video from TikTok and YouTube. Write down a url link to video for downloading!')
        .format(name=username)
    )

@dp.message()
async def any_message_handler(message: Message) -> None:
    """
    Handler function for any messages from user. Using for collecting urls and downloading video
    """
    messages_from_user = message.text.rstrip().lstrip().split(' ') # Split every word from user message
    available_platform_urls = [] # Array for saving urls that was validate
    paths_to_video = [] # Array for saving paths to video, that was downloaded or found at folders
    downloaded_msgs = [] # Array for saving all messages that notificate user about success download video
    try:
        # Get all urls from message
        for msg in messages_from_user:
            if not is_message_valid_url(msg):
                continue
            url = get_url_from_message(msg)
            if not is_platform_from_url_available(url):
                continue
            available_platform_urls.append(url)

        urls_message = await message.answer(
            _("We would be able to get the {count_urls} URLs from your message. We're starting to download them...")
            .format(count_urls=len(available_platform_urls))
        )
    except:
        await message.answer(
            _('Something went wrong...We send msg to admin, try later!')
        )
        await bot.send_message(ADMIN_ID, 
                               _('Something went wrong at {error_situation} at time {date_and_time}. Check logs for more information!')
                               .format(
                                   error_situation='get urls from user msg',
                                   date_and_time=datetime.now(pytz.utc).strftime('%d.%m.%Y %H:%M:%S'))
                                   )      
        raise Exception('Something went wrong in block of getting urls from user msg')                          

    # If urls in message was found make other logic
    if len(available_platform_urls) > 0:
        try:
            # Download or get from local folders all video by url
            for download_url in available_platform_urls:
                path_to_save = get_folder_to_save(download_url)
                if path_to_save:
                    if 'instagram' in download_url:
                        video_id, stdout_video_id, stderror_video_id = await get_video_id(download_url, PATH_TO_COOKIES)
                        is_available_to_send_back, stdout_check_video_size, stderror_check_video_size = await check_video_size(download_url, PATH_TO_COOKIES)
                    else:
                        video_id, stdout_video_id, stderror_video_id = await get_video_id(download_url, None)
                        is_available_to_send_back, stdout_check_video_size, stderror_check_video_size = await check_video_size(download_url)
                   
                    logging.info(stdout_check_video_size)
                    logging.error(stderror_check_video_size)
                    logging.info(stdout_video_id)
                    logging.error(stderror_video_id)
                    
                    if not is_available_to_send_back and not no_send_back_type:
                        await message.answer(
                            _('Video {video_id} is too big for sending back to you!')
                            .format(video_id=video_id)
                        )
                        continue

                    path_to_video = f'{path_to_save}/{video_id}.mp4'
                    if not os.path.exists(path_to_video):
                        # If downloading video from Instagram Reels - add a path to cookies, else download without them
                        if 'inst' in path_to_video:
                            path_to_video, stdout_download_video, strerror_download_video = await download_video_async(download_url, path_to_save, video_id, no_send_back_type, PATH_TO_COOKIES)
                        else:
                            path_to_video, stdout_download_video, strerror_download_video = await download_video_async(download_url, path_to_save, video_id, no_send_back_type)
                        logging.info(stdout_download_video)
                        logging.error(strerror_download_video)
                        # if it's youtebe video and it's for sending back to user to telegram we correct it
                        if ('youtube' in path_to_video or 'inst' in path_to_video) and not no_send_back_type:
                            path_to_video, stdout_correct, stderror_correct = await correct_video(path_to_video)
                            logging.info(stdout_correct)
                            logging.error(stderror_correct)
                    paths_to_video.append(path_to_video) # Save path to video for sending them after
                
                await urls_message.delete()
                success_download_msg = await message.answer(
                    _('{count_videos} video was downloaded!')
                    .format(count_videos=len(paths_to_video))
                )
                downloaded_msgs.append(success_download_msg)
        except:
            await message.answer(
                _('Something went wrong...We send msg to admin, try later!')
                )
            await bot.send_message(ADMIN_ID, 
                               _('Something went wrong at {error_situation} at time {date_and_time}. Check logs for more information!')
                               .format(
                                   error_situation='downloading video from urls that user enter',
                                   date_and_time=datetime.now(pytz.utc).strftime('%d.%m.%Y %H:%M:%S'))
                                   )
            raise Exception('Something went wrong in block of downloading video from urls that user enter')
        # If type of running program for sending back videos - we do this
        if not no_send_back_type:
            # If videos was less than 2 we make fictional pause for better reading message
            if len(downloaded_msgs) < 2:
                await asyncio.sleep(3)
            # Delete all messages that notificated user about success download video
            for downloaded_msg in downloaded_msgs:
                await downloaded_msg.delete()
            # Sending video block
            try:
                upload_msg = await message.answer(
                    _('Sending the videos!')
                )
                # Get all paths to videos that we saved and make it to type that answer_video can get
                for path_to_video in paths_to_video:
                    video = FSInputFile(path_to_video)
                    await message.answer_video(video)
                    # If type of running program was choose for no saving we must delete video that was download
                    if not save_type:
                        os.remove(path_to_video)
                await upload_msg.delete()
            except:
                await message.answer(
                    ('Something went wrong...We send msg to admin, try later!')
                    )
                await bot.send_message(ADMIN_ID, 
                                _('Something went wrong at {error_situation} at time {date_and_time}. Check logs for more information!')
                                .format(
                                    error_situation='sending a downloaded video to user',
                                    date_and_time=datetime.now(pytz.utc).strftime('%d.%m.%Y %H:%M:%S'))
                                    )
                raise Exception('Something went wrong in block of sending videos to user')
    else:
        # If urls in user message was not fount we notificate him about this
        await message.answer(
            _('No urls! Nothing to download...For download write a url to video from available platforms ({available_platforms})!')
            .format(available_platforms=' '.join(PLATFORMS.keys()))
        )
    # Message that remember that user should do, then he will return later
    await message.answer(
        _('For download video send a url here!')
    )

async def main() -> None:
    """
    Function that start polling bot
    """
    await dp.start_polling(bot)

# If file is working like running we start bot work
if __name__ == '__main__':
    try:
        today = datetime.now(pytz.utc) # Get today datetime
        today_str = today.strftime('%d.%m.%Y') # Make it to string with format dd.mm.yyyy
        logging_format = '[%(asctime)s | %(levelname)s:%(name)s] - %(message)s' # Make format for logger
        logging.basicConfig(filename=f'logs/{today_str}.log', level=logging.INFO, format=logging_format) # Configure logger
        check() # Check all required packages
        asyncio.run(main()) # Run bot
    except RequiredPackageNotInstalledOrNotFound:
        """
        If we get our custom exception we raise another exception, that we need install or update packages
        """
        raise Exception('Some requiered packages was not install... Check logs for more information!')
    except:
        """
        If we get another exception we just notificatie to check logs
        """
        raise Exception('Some was going wrong...For detail information check logs or traceback in terminal!')