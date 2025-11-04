"""
Tests for the DKP scraper module.
"""
import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import xml.etree.ElementTree as ET

import httpx
import pytest

from scripts.dkp_downloader import DKPDownloader, Entry


def async_iter_bytes(data: bytes):
    """Helper to create an async iterator factory from bytes."""
    async def _iter():
        yield data
    return _iter()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_atom_xml():
    """Sample ATOM feed XML content."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <title>Cadastral municipality TEST 1</title>
        <link href="https://example.com/ko-123456.zip" rel="alternate"/>
        <id>https://example.com/ko-123456.zip</id>
        <updated>2025-01-01T12:00:00Z</updated>
    </entry>
    <entry>
        <title>Cadastral municipality TEST 2</title>
        <link href="https://example.com/ko-789012.zip" rel="alternate"/>
        <id>https://example.com/ko-789012.zip</id>
        <updated>2025-01-02T12:00:00Z</updated>
    </entry>
    <entry>
        <title>Cadastral municipality INVALID</title>
        <link href="" rel="alternate"/>
        <id>https://example.com/ko-invalid.zip</id>
        <updated>2025-01-03T12:00:00Z</updated>
    </entry>
</feed>"""


@pytest.fixture
def sample_atom_xml_file(temp_dir, sample_atom_xml):
    """Create a sample ATOM XML file."""
    xml_file = temp_dir / "atom_feed.xml"
    xml_file.write_text(sample_atom_xml, encoding="utf-8")
    return xml_file


class TestDKPDownloader:
    """Test cases for DKPDownloader class."""

    def test_init(self, temp_dir: Path) -> None:
        """Test DKPDownloader initialization."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            downloader = DKPDownloader()
            
            assert downloader.output_dir.exists()
            assert downloader.atom_xml_path.parent == downloader.output_dir
            assert downloader.atom_xml_path.name.endswith("_atom_feed.xml")

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.httpx.AsyncClient")
    async def test_download_atom_feed_success(
        self,
        mock_client_class: AsyncMock,
        temp_dir: Path,
        sample_atom_xml: str
    ) -> None:
        """Test successful ATOM feed download."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            # Mock the HTTP client and response
            mock_response = AsyncMock()
            mock_response.raise_for_status = Mock()
            # aiter_bytes should return an async iterator, not a coroutine
            mock_response.aiter_bytes = Mock(return_value=async_iter_bytes(sample_atom_xml.encode()))
            
            mock_stream = AsyncMock()
            mock_stream.__aenter__ = AsyncMock(return_value=mock_response)
            mock_stream.__aexit__ = AsyncMock(return_value=None)
            
            mock_client = AsyncMock()
            # stream() should return the mock_stream directly, not a coroutine
            mock_client.stream = Mock(return_value=mock_stream)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            downloader = DKPDownloader()
            await downloader._download_atom_feed()
            
            assert downloader.atom_xml_path.exists()
            assert downloader.atom_xml_path.read_text() == sample_atom_xml

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.httpx.AsyncClient")
    async def test_download_atom_feed_already_exists(
        self,
        mock_client_class: AsyncMock,
        temp_dir: Path,
        sample_atom_xml: str
    ) -> None:
        """Test that ATOM feed download is skipped if file already exists."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            downloader = DKPDownloader()
            downloader.atom_xml_path.write_text(sample_atom_xml)
            
            await downloader._download_atom_feed()
            
            # Verify client was not called
            mock_client_class.assert_not_called()

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.httpx.AsyncClient")
    async def test_download_atom_feed_error(
        self,
        mock_client_class: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test ATOM feed download error handling."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            # Mock HTTP error - stream() raises error when called
            mock_client = AsyncMock()
            mock_client.stream = Mock(side_effect=httpx.RequestError("Connection error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            downloader = DKPDownloader()
            
            with pytest.raises(httpx.RequestError):
                await downloader._download_atom_feed()
            
            # Verify partial file is cleaned up
            assert not downloader.atom_xml_path.exists()

    def test_parse_atom_feed(self, temp_dir: Path, sample_atom_xml_file: Path) -> None:
        """Test parsing ATOM feed XML."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            downloader = DKPDownloader()
            downloader.atom_xml_path = sample_atom_xml_file
            downloader._parse_atom_feed()
            
            assert hasattr(downloader, 'tree')
            assert hasattr(downloader, 'root')
            assert hasattr(downloader, 'entries')
            assert len(downloader.entries) == 2  # Only 2 valid entries (third has empty href)

    def test_extract_single_entry_valid(self, temp_dir: Path, sample_atom_xml: str) -> None:
        """Test extracting a valid entry from XML."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            root = ET.fromstring(sample_atom_xml)
            entry = root.find(".//{http://www.w3.org/2005/Atom}entry")
            
            downloader = DKPDownloader()
            result = downloader._extract_single_entry(entry)
            
            assert result is not None
            assert isinstance(result, Entry)
            assert result.id == 123456
            assert result.title == "Cadastral municipality TEST 1"
            assert result.url == "https://example.com/ko-123456.zip"
            assert isinstance(result.updated, datetime)

    def test_extract_single_entry_no_link(self, temp_dir: Path) -> None:
        """Test extracting entry with no link element."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            xml = """<entry xmlns="http://www.w3.org/2005/Atom">
                <title>Test Entry</title>
                <id>https://example.com/ko-123456.zip</id>
            </entry>"""
            entry = ET.fromstring(xml)
            
            downloader = DKPDownloader()
            result = downloader._extract_single_entry(entry)
            
            assert result is None

    def test_extract_single_entry_empty_href(self, temp_dir: Path) -> None:
        """Test extracting entry with empty href."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            xml = """<entry xmlns="http://www.w3.org/2005/Atom">
                <title>Test Entry</title>
                <link href="" rel="alternate"/>
                <id>https://example.com/ko-123456.zip</id>
            </entry>"""
            entry = ET.fromstring(xml)
            
            downloader = DKPDownloader()
            result = downloader._extract_single_entry(entry)
            
            assert result is None

    def test_extract_single_entry_no_id(self, temp_dir: Path) -> None:
        """Test extracting entry with no id element."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            xml = """<entry xmlns="http://www.w3.org/2005/Atom">
                <title>Test Entry</title>
                <link href="https://example.com/test.zip" rel="alternate"/>
            </entry>"""
            entry = ET.fromstring(xml)
            
            downloader = DKPDownloader()
            result = downloader._extract_single_entry(entry)
            
            assert result is None

    def test_extract_entries(self, temp_dir: Path, sample_atom_xml_file: Path) -> None:
        """Test extracting multiple entries from XML."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            downloader = DKPDownloader()
            downloader.atom_xml_path = sample_atom_xml_file
            downloader.tree = ET.parse(sample_atom_xml_file)
            downloader.root = downloader.tree.getroot()
            
            entries = downloader._extract_entries(max_workers=2)
            
            assert len(entries) == 2
            assert all(isinstance(entry, Entry) for entry in entries)
            assert entries[0].id == 123456
            assert entries[1].id == 789012

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.aiofiles.open")
    @patch("scripts.dkp_scrapper.httpx.AsyncClient")
    async def test_download_zip_success(
        self,
        mock_client_class: AsyncMock,
        mock_aiofiles: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test successful zip file download."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            # Mock file content
            zip_content = b"fake zip content"
            
            downloader = DKPDownloader()
            url = "https://example.com/test.zip"
            dest_path = downloader.output_dir / "test.zip"
            
            # Mock aiofiles - make write actually write to the file (accumulate chunks)
            async def mock_write(data: bytes):
                # Accumulate chunks by appending
                if data:  # Only write non-empty chunks
                    if dest_path.exists():
                        dest_path.write_bytes(dest_path.read_bytes() + data)
                    else:
                        dest_path.write_bytes(data)
            
            mock_file = AsyncMock()
            mock_file.write = AsyncMock(side_effect=mock_write)
            mock_aiofiles.return_value.__aenter__ = AsyncMock(return_value=mock_file)
            mock_aiofiles.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock HTTP response
            mock_response = AsyncMock()
            mock_response.raise_for_status = Mock()
            # aiter_bytes should return an async iterator, not a coroutine
            mock_response.aiter_bytes = Mock(return_value=async_iter_bytes(zip_content))
            
            mock_stream = AsyncMock()
            mock_stream.__aenter__ = AsyncMock(return_value=mock_response)
            mock_stream.__aexit__ = AsyncMock(return_value=None)
            
            mock_client = AsyncMock()
            mock_client.stream = Mock(return_value=mock_stream)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            # Test with no client (creates its own)
            result = await downloader.download_zip(url)
            
            assert result.exists()
            assert result.name == "test.zip"
            mock_file.write.assert_called()
            assert result.read_bytes() == zip_content

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.aiofiles.open")
    @patch("scripts.dkp_scrapper.httpx.AsyncClient")
    async def test_download_zip_with_custom_filename(
        self,
        mock_client_class: AsyncMock,
        mock_aiofiles: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test zip download with custom filename."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            zip_content = b"fake zip content"
            
            downloader = DKPDownloader()
            url = "https://example.com/test.zip"
            custom_filename = "custom.zip"
            dest_path = downloader.output_dir / custom_filename
            
            # Mock aiofiles - make write actually write to the file (accumulate chunks)
            async def mock_write(data: bytes):
                # Accumulate chunks by appending
                if data:  # Only write non-empty chunks
                    if dest_path.exists():
                        dest_path.write_bytes(dest_path.read_bytes() + data)
                    else:
                        dest_path.write_bytes(data)
            
            mock_file = AsyncMock()
            mock_file.write = AsyncMock(side_effect=mock_write)
            mock_aiofiles.return_value.__aenter__ = AsyncMock(return_value=mock_file)
            mock_aiofiles.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_response = AsyncMock()
            mock_response.raise_for_status = Mock()
            # aiter_bytes should return an async iterator, not a coroutine
            mock_response.aiter_bytes = Mock(return_value=async_iter_bytes(zip_content))
            
            mock_stream = AsyncMock()
            mock_stream.__aenter__ = AsyncMock(return_value=mock_response)
            mock_stream.__aexit__ = AsyncMock(return_value=None)
            
            mock_client = AsyncMock()
            mock_client.stream = Mock(return_value=mock_stream)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            result = await downloader.download_zip(url, filename=custom_filename)
            
            assert result.name == custom_filename
            assert result.read_bytes() == zip_content

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.aiofiles.open")
    @patch("scripts.dkp_scrapper.httpx.AsyncClient")
    async def test_download_zip_error_cleanup(
        self,
        mock_client_class: AsyncMock,
        mock_aiofiles: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test that partial download is cleaned up on error."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            # Mock HTTP error
            mock_client = AsyncMock()
            mock_client.stream = Mock(side_effect=httpx.RequestError("Connection error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            downloader = DKPDownloader()
            url = "https://example.com/test.zip"
            dest_path = downloader.output_dir / "test.zip"
            
            # Create a partial file to simulate failed download
            dest_path.write_bytes(b"partial content")
            
            with pytest.raises(httpx.RequestError):
                await downloader.download_zip(url)
            
            # Verify file was cleaned up
            assert not dest_path.exists()

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.DKPDownloader.download_zip")
    async def test_scrape(self, mock_download_zip: AsyncMock, temp_dir: Path) -> None:
        """Test scraping multiple files."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            # Create mock entries
            entry1 = Entry(1, "Test 1", "https://example.com/test1.zip", datetime.now())
            entry2 = Entry(2, "Test 2", "https://example.com/test2.zip", datetime.now())
            
            downloader = DKPDownloader()
            downloader.entries = [entry1, entry2]
            
            # Mock download_zip to return paths
            mock_path1 = temp_dir / "test1.zip"
            mock_path2 = temp_dir / "test2.zip"
            mock_download_zip.side_effect = [mock_path1, mock_path2]
            
            results = await downloader.scrape(max_concurrent_downloads=2)
            
            assert len(results) == 2
            assert mock_path1 in results
            assert mock_path2 in results
            assert mock_download_zip.call_count == 2

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.DKPDownloader.download_zip")
    async def test_scrape_with_failures(
        self,
        mock_download_zip: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test scraping with some download failures."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            entry1 = Entry(1, "Test 1", "https://example.com/test1.zip", datetime.now())
            entry2 = Entry(2, "Test 2", "https://example.com/test2.zip", datetime.now())
            
            downloader = DKPDownloader()
            downloader.entries = [entry1, entry2]
            
            # Mock download_zip - first succeeds, second fails
            mock_path1 = temp_dir / "test1.zip"
            mock_download_zip.side_effect = [
                mock_path1,
                Exception("Download failed")
            ]
            
            results = await downloader.scrape(max_concurrent_downloads=2)
            
            # Only successful downloads should be in results
            assert len(results) == 1
            assert mock_path1 in results

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.DKPDownloader.scrape")
    @patch("scripts.dkp_scrapper.DKPDownloader._parse_atom_feed")
    @patch("scripts.dkp_scrapper.DKPDownloader._download_atom_feed")
    async def test_download_full_workflow(
        self,
        mock_download_feed: AsyncMock,
        mock_parse_feed: AsyncMock,
        mock_scrape: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test the full download workflow."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            downloader = DKPDownloader()
            mock_scrape.return_value = [temp_dir / "file1.zip", temp_dir / "file2.zip"]
            
            results = await downloader._download(max_concurrent_downloads=5)
            
            mock_download_feed.assert_called_once()
            mock_parse_feed.assert_called_once()
            mock_scrape.assert_called_once_with(5)
            assert len(results) == 2

    @patch("scripts.dkp_scrapper.DKPDownloader._download")
    def test_download_sync_entry_point(
        self,
        mock_async_download: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test the synchronous download entry point."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            mock_async_download.return_value = [temp_dir / "file1.zip"]
            
            downloader = DKPDownloader()
            results = downloader.download(max_concurrent_downloads=3)
            
            mock_async_download.assert_called_once_with(3)
            assert len(results) == 1

    @pytest.mark.asyncio
    @patch("scripts.dkp_scrapper.DKPDownloader.scrape")
    @patch("scripts.dkp_scrapper.DKPDownloader._parse_atom_feed")
    @patch("scripts.dkp_scrapper.DKPDownloader._download_atom_feed")
    async def test_download_error_propagation(
        self,
        mock_download_feed: AsyncMock,
        mock_parse_feed: AsyncMock,
        mock_scrape: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test that errors in scrape are properly propagated."""
        with patch.object(DKPDownloader, "DOWNLOADS_DIR", temp_dir):
            downloader = DKPDownloader()
            mock_scrape.side_effect = Exception("Scrape failed")
            
            with pytest.raises(Exception, match="Scrape failed"):
                await downloader._download()

