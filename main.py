import os
import asyncio
import logging
from tqdm.asyncio import tqdm_asyncio
from telethon import TelegramClient, events
from decouple import config
import aiofiles
import nest_asyncio
from datetime import datetime

# Apply the event loop patch for Jupyter
nest_asyncio.apply()

# Configuration
API_ID = config('API_ID')
API_HASH = config('API_HASH')
CHANNEL_USERNAME = config('CHANNEL_USERNAME')
DOWNLOAD_FOLDER = config('DOWNLOAD_FOLDER')
LOG_FILE = config('LOG_FILE')
MAX_CONCURRENT_DOWNLOADS = 5  # Adjust based on your connection
RETRY_LIMIT = 3

# Setup directories
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def download_with_progress(client, message, semaphore):
    """Download a file with progress tracking and retry logic"""
    file_name = message.document.attributes[0].file_name
    save_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    async with semaphore:
        for attempt in range(RETRY_LIMIT):
            try:
                if os.path.exists(save_path):
                    logger.info(f"Skipping existing file: {file_name}")
                    return

                logger.info(f"Downloading (attempt {attempt + 1}): {file_name}")

                # Create async file handle
                async with aiofiles.open(save_path, 'wb') as f:
                    progress = tqdm_asyncio(
                        total=message.document.size,
                        unit='B',
                        unit_scale=True,
                        desc=file_name[:20] + '...' if len(file_name) > 20 else file_name
                    )

                    async for chunk in client.iter_download(message.document):
                        await f.write(chunk)
                        progress.update(len(chunk))

                    progress.close()
                return  # Success

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {file_name}: {str(e)}")
                if os.path.exists(save_path):
                    os.remove(save_path)
                await asyncio.sleep(2 ** attempt)  # Exponential backoff


async def download_pdfs():
    """Main function to download PDFs with enhanced features"""
    logger.info("Starting download process...")

    async with TelegramClient("session", API_ID, API_HASH) as client:
        try:
            # Single pass message processing
            pdf_messages = []
            async for message in client.iter_messages(CHANNEL_USERNAME):
                if message.document and message.document.mime_type == "application/pdf":
                    pdf_messages.append(message)
                    if len(pdf_messages) % 50 == 0:  # Periodic logging
                        logger.info(f"Collected {len(pdf_messages)} PDFs so far...")

            logger.info(f"Total PDFs found: {len(pdf_messages)}")

            # Create semaphore for concurrent downloads
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

            # Create download tasks
            tasks = [download_with_progress(client, msg, semaphore) for msg in pdf_messages]

            # Run tasks with progress
            for f in tqdm_asyncio.as_completed(tasks, desc="Overall Progress", total=len(tasks)):
                await f

            logger.info("All downloads completed!")

        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            raise


# Run the async function
if __name__ == "__main__":
    start_time = datetime.now()
    asyncio.run(download_pdfs())
    logger.info(f"Total execution time: {datetime.now() - start_time}")
