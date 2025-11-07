"""
Scraper for DGU ATOM feed that downloads cadastral municipality zip files.

Environment variable:
    DOWNLOADS_DIR: Directory to store downloaded files
    DATE: Date of the download
    ATOM_URL: URL of the ATOM feed
    ATOM_NAMESPACE: Namespace of the ATOM feed
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path
from typing import NamedTuple
import xml.etree.ElementTree as ET

import aiofiles
import httpx

from logger import logger

class Entry(NamedTuple):
    id: int
    title: str
    url: str
    updated: datetime

class DKPDownloader:
    """Downloader for cadastral municipality data from ATOM feed."""

    ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}
    ATOM_URL       = "https://oss.uredjenazemlja.hr/oss/public/atom/atom_feed.xml"
    DOWNLOADS_DIR  = Path(__file__).parent.parent / 'data' / 'downloads'
    DATE           = date.today().isoformat()

    def __init__(self) -> None:
        """
        Initialize the downloader.
        """
        self.output_dir = self.DOWNLOADS_DIR / 'dkp' / self.DATE
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.atom_xml_path = self.output_dir / f'{self.DATE}_atom_feed.xml'

    async def _download_atom_feed(self) -> None:
        """
        Download the ATOM feed XML file asynchronously.
        """
        if self.atom_xml_path.exists():
            logger.info(
                f"ATOM feed already exists, skipping download: {self.atom_xml_path}"
            )
            return

        logger.info(f"Downloading ATOM feed from: {self.ATOM_URL}")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("GET", self.ATOM_URL) as response:
                    response.raise_for_status()

                    async with aiofiles.open(self.atom_xml_path, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            if chunk:
                                await f.write(chunk)

            file_size = self.atom_xml_path.stat().st_size
            logger.info(
                f"Downloaded ATOM feed to: {self.atom_xml_path} ({file_size:,} bytes)"
            )

        except httpx.RequestError as e:
            logger.error(f"Failed to download ATOM feed: {e}")
            if self.atom_xml_path.exists():
                self.atom_xml_path.unlink()
            raise

    def _parse_atom_feed(self) -> None:
        """
        Parse the downloaded ATOM feed XML and extract entries.
        """
        self.tree = ET.parse(self.atom_xml_path)
        self.root = self.tree.getroot()
        self.entries = self._extract_entries()
        logger.info(f"Extracted {len(self.entries)} entries from XML")

    def _extract_single_entry(self, entry: ET.Element) -> Entry | None:
        """
        Extract information from a single XML entry element.

        Args:
            entry: XML entry element

        Returns:
            Entry object if successful, None otherwise
        """
        try:
            title_elem = entry.find("atom:title", self.ATOM_NAMESPACE)
            title = title_elem.text if title_elem is not None else "Unknown"

            link_elem = entry.find("atom:link", self.ATOM_NAMESPACE)
            if link_elem is None:
                logger.warning(f"Skipping entry '{title}': no link found")
                return None

            url = link_elem.attrib.get("href", "")
            if not url:
                logger.warning(f"Skipping entry '{title}': empty href")
                return None

            id_elem = entry.find("atom:id", self.ATOM_NAMESPACE)
            if id_elem is not None:
                entry_id = int(id_elem.text.rsplit("-", 1)[1].split(".")[0])
            else:
                logger.warning(f"Skipping entry '{title}': no id found")
                return None

            updated_elem = entry.find("atom:updated", self.ATOM_NAMESPACE)
            updated = datetime.fromisoformat(updated_elem.text) if updated_elem is not None else ""

            return Entry(entry_id, title, url, updated)

        except Exception as e:
            logger.warning(f"Error processing entry: {e}")
            return None

    def _extract_entries(self, max_workers: int = 4) -> list[Entry]:
        """
        Extract entry information from parsed XML root using parallel processing.

        Args:
            max_workers (int): Maximum number of worker threads for parallel processing

        Returns:
            List of Entry objects
        """
        entries = self.root.findall(".//atom:entry", self.ATOM_NAMESPACE)

        logger.info(f"Extracting {len(entries)} entries using {max_workers} workers")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_entry = {
                executor.submit(self._extract_single_entry, entry): entry
                for entry in entries
            }

            entries_list = [
                future.result() for future in as_completed(future_to_entry)
                if future.result() is not None
            ]

        entries_list.sort(key=lambda e: e.id)

        logger.info(f"Extracted {len(entries_list)} entries from XML")
        return entries_list

    async def download_zip(
        self,
        url: str,
        filename: str | None = None,
        client: httpx.AsyncClient | None = None
    ) -> Path:
        """
        Download a zip file from URL asynchronously.

        Args:
            url (str): URL to the zip file
            filename (str | None): Optional custom filename. If not provided, extracts from URL.
            client (httpx.AsyncClient | None): Optional httpx client for connection pooling.
                    If None, creates a new one.

        Returns:
            Path to the downloaded file.
        """
        if filename is None:
            filename = Path(url).name

        dest_path = self.output_dir / filename

        use_external_client = client is not None
        if client is None:
            client = httpx.AsyncClient(timeout=120.0)

        try:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                async with aiofiles.open(dest_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        if chunk:
                            await f.write(chunk)

            file_size = dest_path.stat().st_size
            logger.info(f"Downloaded: {dest_path} ({file_size:,} bytes)")
            return dest_path

        except httpx.RequestError as e:
            logger.error(f"Failed to download {url}: {e}")
            if dest_path.exists():
                dest_path.unlink()
            raise
        finally:
            if not use_external_client:
                await client.aclose()

    async def scrape(self, max_concurrent_downloads: int = 10) -> list[Path]:
        """
        Download all zip files asynchronously with concurrent downloads.

        Args:
            max_concurrent_downloads: Maximum number of concurrent downloads

        Returns:
            List of paths to downloaded files
        """
        logger.info(
            f"Starting async download of {len(self.entries)} files "
            f"(max {max_concurrent_downloads} concurrent downloads)"
        )

        semaphore = asyncio.Semaphore(max_concurrent_downloads)

        async with httpx.AsyncClient(
            timeout=120.0,
            limits=httpx.Limits(
                max_keepalive_connections=max_concurrent_downloads,
                max_connections=max_concurrent_downloads * 2
            )
        ) as client:
            async def download_with_semaphore(entry: Entry, index: int) -> Path | None:
                """
                Download a single file with semaphore control.

                Args:
                    entry (Entry): Entry object containing the URL and title
                    index (int): Index of the entry

                Returns:
                    Path to the downloaded file or None if failed
                """
                async with semaphore:
                    url   = entry.url
                    title = entry.title

                    logger.info(f"[{index}/{len(self.entries)}] Processing: {title}")

                    try:
                        file_path = await self.download_zip(url, client=client)
                        return file_path
                    except Exception as e:
                        logger.error(f"Failed to download {url}: {e}")
                        return None

            tasks = [
                download_with_semaphore(entry, i + 1)
                for i, entry in enumerate(self.entries)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        downloaded_files = [
            result for result in results
            if result is not None and not isinstance(result, Exception)
        ]

        logger.info(
            f"Successfully downloaded {len(downloaded_files)}/{len(self.entries)} files"
        )
        return downloaded_files

    async def _download(self, max_concurrent_downloads: int = 10) -> list[Path]:
        """
        Async main entry point for the downloader.

        Args:
            max_concurrent_downloads: Maximum number of concurrent downloads

        Returns:
            List of paths to downloaded files
        """
        await self._download_atom_feed()
        self._parse_atom_feed()

        try:
            downloaded = await self.scrape(max_concurrent_downloads)
            logger.info(
                f"Scraping completed. Downloaded {len(downloaded)} files "
                f"to {self.output_dir}"
            )
            return downloaded
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise

    def download(self, max_concurrent_downloads: int = 10) -> list[Path]:
        """
        Main entry point for the downloader.

        Args:
            max_concurrent_downloads: Maximum number of concurrent downloads

        Returns:
            List of paths to downloaded files
        """
        return asyncio.run(self._download(max_concurrent_downloads))
