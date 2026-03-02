# Video Downloader Telegram Bot

Небольшой и удобный Telegram-бот для скачивания видео из популярных сервисов. Предназначен для локального развертывания на своем устройстве или хостинге (MacOS/Linux).

**Что умеет бот**
- **Автоматически скачивает видео по ссылке**: отправьте ссылку на видео — бот скачает её.
- **Поддерживаемые платформы**: YouTube, TikTok, Instagram Reels, Twitch.
- **Сохранение локально или отправка в чат**: можно настроить, сохранять ли видео в папках проекта и/или отправлять обратно в Telegram.
- **Поддержка куки-файлов**: для загрузки приватных или требующих куки Instagram Reels можно передать файл с cookie.
- **Международные локали**: локализации лежат в папке `locales` (поддерживаются несколько языков).

**Кому это подойдёт**
- Тем, кто хочет быстро получать видео через Telegram для личного использования или для локального архива. 

**Структура проекта (ключевые файлы)**
- `video_downloader/app.py` — основной бот и логика обработки сообщений.
- `video_downloader/download_video.py` — обёртка над `yt-dlp` и `ffmpeg` для скачивания и корректировки видео.
- `video_downloader/check_dependencies.py` — проверка наличия системных зависимостей.
- `video_downloader/excps.py` — кастомные исключения.

**Требования**
1. Система:
	- Python 3.10+
	- Командные утилиты: `yt-dlp`, `ffmpeg`, `ffprobe` (доступны в PATH).
2. Python-библиотеки (устанавливаются через pip):
	- `aiogram` — Telegram Bot API framework
	- `python-decouple` — работа с .env
	- `pytz` — timezone (используется для логов)
    - `Babel` - для локализации сообщений на разные языки

Пример установки Python-зависимостей:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Системные зависимости (macOS, Homebrew):

```bash
brew install yt-dlp
brew install ffmpeg
```

Альтернатива (установить `yt-dlp` через pip):

```bash
pip install yt-dlp
```

**Конфигурация**
Создайте файл `.env` в корне проекта или в папке `video_downloader` со следующими переменными:

```
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_ID=ваш_telegram_id_админа  # необязательно, используется для уведомлений об ошибках
PATH_TO_COOKIES=path/to/cookies.txt  # опционально, для Instagram Reels
```

Формат куки-файла: обычный `cookies.txt`, используемый `yt-dlp`. Подробннее: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp

**Запуск бота**
1. Из корня репозитория (предпочтительно, когда виртуальное окружение активировано):

```bash
python -m video_downloader.app
```

2. Или зайти в папку `video_downloader` и запустить напрямую:

```bash
cd video_downloader
python app.py
```

При запуске доступны опции командной строки:
- `--save 0|1` — 0 (по умолчанию) не сохранять загруженные видео локально, 1 — сохранять.
- `--no-send-back 0|1` — 0 (по умолчанию) отправлять загруженное видео обратно в чат; 1 — не отправлять, только сохранять локально.

Пример запуска с сохранением и без отправки обратно:

```bash
python -m video_downloader.app --save 1 --no-send-back 1
```

**Логи и папки с видео**
- Логи сохраняются в папке `logs/` в файлы с датой.
- Видео сохраняются в папках:
  - `youtube_videos/` — YouTube
  - `tiktok_videos/` — TikTok
  - `inst_reels_videos/` — Instagram Reels
  - `twitch_videos/` — Twitch
  Внутри каждой папки может быть подпапка `locals/` для сохранения исходных/оригинальных файлов, если используется опция `--no-send-back`.

**Частые проблемы и отладка**
- Если при старте появляется ошибка про `yt-dlp`/`ffmpeg` — убедитесь, что они установлены и доступны в PATH. Проверьте версии команд:

```bash
yt-dlp --version
ffmpeg -version
ffprobe -version
```

- Проверьте, что в `.env` указан корректный `BOT_TOKEN` и при необходимости `ADMIN_ID`.
- Если загрузка Instagram Reels не работает — проверьте `PATH_TO_COOKIES` и формат cookie.

**Локализация**
Проект поддерживает локализации через папку `locales/`. Чтобы добавить перевод, обновите соответствующие `.po` файлы и скомпилируйте их в `.mo`. Подробнее: https://docs.aiogram.dev/en/latest/utils/i18n.html

**Вклад и лицензия**
- Пулреквесты и issue приветствуются.
- Добавьте короткий `CONTRIBUTING.md`, если планируете активно принимать PR.
- Распространяется по лицензии GNU General Public License v3.0

***Конец README***