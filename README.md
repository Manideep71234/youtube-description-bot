# YouTube Description Bot

Python bot that auto-generates YouTube video descriptions with an LLM, manages comments, and sends alerts and weekly reports.

![Bot in action](docs/screenshots/telegram-alert.png)

## Features
- LLM-generated descriptions (`ai_generator.py`)
- Comment handling (`comment_manager.py`)
- Notifications via Telegram, WhatsApp and Email
- Duplicate protection (`processed_videos.txt`)
- Weekly performance report (`weekly_report.py`)
- Scheduled runs via GitHub Actions or Windows background script

## Tech Stack
Python, YouTube Data API, LLM API, Telegram/WhatsApp/SMTP, GitHub Actions

## Setup
```bash
git clone https://github.com/Manideep71234/youtube-description-bot
cd youtube-description-bot
pip install -r requirements.txt
cp .env.example .env     # add API keys
python main.py
```
Windows: run `setup.bat`, then `run_bot.bat` (or `start_background.vbs`).

## How It Works
1. `youtube_client.py` fetches new videos
2. `ai_generator.py` writes the description
3. Description is updated on YouTube
4. Notifiers report the result; video ID is saved to avoid reprocessing

## Screenshots
![Terminal log](docs/screenshots/terminal.png)
![Weekly report](docs/screenshots/weekly-report.png)
![Updated description](docs/screenshots/description.png)
