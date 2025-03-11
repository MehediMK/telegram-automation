# Telegram PDF Downloader

This project downloads all PDF files from a specified Telegram channel using the **Telethon** library.

## Features
- Connects to a Telegram channel via **Telethon**.
- Scans all messages and identifies PDFs.
- Downloads PDFs to a specified folder.
- Logs activities for tracking.
- Uses **asyncio** for asynchronous execution.

## Requirements
Make sure you have Python 3.8 or higher installed.

### Install Dependencies
```sh
pip install telethon python-decouple tqdm nest_asyncio
```

## Configuration
Create a `.env` file in the project directory and add the following environment variables:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
CHANNEL_USERNAME=your_channel_username  # Without @
DOWNLOAD_FOLDER=downloads
LOG_FILE=logs/app.log
```

## Usage

1. **Run the script:**
```sh
python main.py
```

2. **What it does:**
   - Connects to Telegram using the API credentials.
   - Fetches messages from the given channel.
   - Identifies messages containing PDF files.
   - Downloads them to the `DOWNLOAD_FOLDER`.
   - Logs activities in the `logs` folder.

## Troubleshooting

- **Permission Error:** Ensure you have write permissions for the `logs` and `downloads` folders.
- **Invalid API credentials:** Check `.env` file for correct `API_ID` and `API_HASH`.
- **Blocked Telegram access:** Use a VPN if Telegram is restricted in your region.
