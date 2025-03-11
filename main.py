import os
import asyncio
import logging
import nest_asyncio
from tqdm import tqdm
from telethon import TelegramClient
from decouple import config

# Apply the event loop patch for Jupyter
nest_asyncio.apply()

# Your Telegram API credentials
API_ID = config('API_ID')  # Replace with your API ID
API_HASH = config('API_HASH')  # Replace with your API Hash
CHANNEL_USERNAME = config('CHANNEL_USERNAME')  # Replace with channel username (without @)


# Create a downloads directory
DOWNLOAD_FOLDER = config('DOWNLOAD_FOLDER')
LOG_FILE = config('LOG_FILE')

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def download_pdfs():
    """Download all PDFs from the Telegram channel."""
    logger.info("Connecting to Telegram API...")
    
    async with TelegramClient("session", API_ID, API_HASH) as client:
        try:
            total_messages = await client.get_messages(CHANNEL_USERNAME, limit=0)  # Get total message count
            logger.info(f"Total messages in the channel: {total_messages.total}")

            pdf_messages = []
            async for message in client.iter_messages(CHANNEL_USERNAME):
                if message.document and message.document.mime_type == "application/pdf":
                    pdf_messages.append(message)

            logger.info(f"Found {len(pdf_messages)} PDFs to download.")

            # Progress bar for downloads
            for message in tqdm(pdf_messages, desc="Downloading PDFs", unit="file"):
                file_name = message.document.attributes[0].file_name
                save_path = os.path.join(DOWNLOAD_FOLDER, file_name)
                
                if os.path.exists(save_path):
                    logger.info(f"Skipping (already downloaded): {file_name}")
                    continue
                
                logger.info(f"Downloading: {file_name}")
                await client.download_media(message, file=save_path)

            logger.info("All PDFs downloaded successfully!")

        except Exception as e:
            logger.error(f"An error occurred: {e}")

# Run the async function
asyncio.run(download_pdfs())

# Run the async function properly in Jupyter Notebook
# await download_pdfs()