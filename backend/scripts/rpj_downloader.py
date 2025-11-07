"""
Downloader for AU and AD datasets from the DGU Geoportal.
"""

import asyncio
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import aiofiles
import httpx

import extractor
from logger import logger

BASE_URL    = "https://geoportal.dgu.hr/services/atom/"
AU_FILENAME = "INSPIRE_Administrative_Units_(AU).zip"
AD_FILENAME = "INSPIRE_Addresses_(AD).zip"

AU_URL    = urljoin(BASE_URL, AU_FILENAME)
AD_URL    = urljoin(BASE_URL, AD_FILENAME)

DOWNLOADS_DIR = Path(__file__).parent.parent / 'data' / 'downloads'
DATE          = date.today().isoformat()

AU_OUTPUT_DIR = DOWNLOADS_DIR / 'au' / DATE
AD_OUTPUT_DIR = DOWNLOADS_DIR / 'ad' / DATE

AU_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
AD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def _download_zip(url: str, filename: str, output_dir: Path) -> Path:
    """
    Download a zip file from the DGU Geoportal.

    Args:
        url (str): URL to the zip file
        filename (str): Name of the zip file
        output_dir (Path): Path to the output directory

    Returns:
        Path to the downloaded zip file.
    """
    logger.info(f"Downloading AU dataset from {url}")
    dest_path = output_dir / filename
    async with aiofiles.open(dest_path, 'wb') as f:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size=8192):
                if chunk:
                    await f.write(chunk)

    logger.info(f"Downloaded AU dataset to {dest_path}")

    return dest_path

def download_zip(url: str, filename: str, output_dir: Path) -> Path:
    """
    Download a zip file from the DGU Geoportal.

    Args:
        url (str): URL to the zip file
        filename (str): Name of the zip file
        output_dir (Path): Path to the output directory

    Returns:
        Path to the downloaded zip file.
    """
    zip_path = asyncio.run(_download_zip(url, filename, output_dir))
    return zip_path

def download_au() -> None:
    """
    Download the AU dataset from the DGU Geoportal.

    Args:
        url (str): URL to the zip file
        filename (str): Name of the zip file
        output_dir (Path): Path to the output directory
    """
    zip_path = download_zip(AU_URL, AU_FILENAME, AU_OUTPUT_DIR)
    extractor.extract_au(zip_path)

def download_ad() -> None:
    """
    Download the AD dataset from the DGU Geoportal.

    Args:
        url (str): URL to the zip file
        filename (str): Name of the zip file
        output_dir (Path): Path to the output directory
    """
    zip_path = download_zip(AD_URL, AD_FILENAME, AD_OUTPUT_DIR)
    extractor.extract_ad(zip_path)
