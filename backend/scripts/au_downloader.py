import asyncio
from datetime import date
from pathlib import Path

import aiofiles
import httpx

from logger import logger

URL = "https://geoportal.dgu.hr/services/atom/INSPIRE_Administrative_Units_(AU).zip"
DOWNLOADS_DIR = Path(__file__).parent.parent / 'data' / 'downloads'
DATE = date.today().isoformat()
OUTPUT_DIR = DOWNLOADS_DIR / 'au' / DATE
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def _download_au() -> Path:
    """Download the AU dataset from the DGU Geoportal."""
    logger.info(f"Downloading AU dataset from {URL}")
    filename = OUTPUT_DIR / f'{DATE}_au.zip'
    async with aiofiles.open(filename, 'wb') as f:
        async with httpx.AsyncClient() as client:
            response = await client.get(URL)
            response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size=8192):
                if chunk:
                    await f.write(chunk)

    logger.info(f"Downloaded AU dataset to {filename}")
    return filename

def download_au() -> Path:
    """Download the AU dataset from the DGU Geoportal."""
    return asyncio.run(_download_au())
