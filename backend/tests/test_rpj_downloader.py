"""
Tests for the RPJ downloader module.
"""
from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock

import httpx
import pytest

with patch.dict(sys.modules, {'extractor': MagicMock()}):
    from scripts import rpj_downloader

def async_iter_bytes(data: bytes) -> AsyncIterator[bytes]:
    """
    Helper to create an async iterator from bytes.

    Args:
        data: Bytes to create an async iterator from

    Returns:
        Async iterator that yields the data
    """
    async def _iter() -> AsyncIterator[bytes]:
        yield data
    return _iter()


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """
    Create a temporary directory for tests.

    Returns:
        Iterator[Path]: Iterator over the path to the temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestDownloadZip:
    """Test cases for _download_zip function."""

    @pytest.mark.asyncio
    @patch("scripts.rpj_downloader.aiofiles.open")
    @patch("scripts.rpj_downloader.httpx.AsyncClient")
    async def test_download_zip_success(
        self,
        mock_client_class: AsyncMock,
        mock_aiofiles: AsyncMock,
        temp_dir: Path
    ) -> None:
        """
        Test successful zip file download.

        Args:
            mock_client_class: Mocked HTTP client class
            mock_aiofiles: Mocked aiofiles class
            temp_dir: Temporary directory
        """
        url = "https://example.com/test.zip"
        filename = "test.zip"
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        dest_path = output_dir / filename

        zip_content = b"fake zip content"

        async def mock_write(data: bytes):
            if data:
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
        mock_response.aiter_bytes = Mock(return_value=async_iter_bytes(zip_content))

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await rpj_downloader._download_zip(url, filename, output_dir)

        assert result == dest_path
        assert dest_path.exists()
        assert dest_path.read_bytes() == zip_content
        mock_client.get.assert_called_once_with(url)
        mock_file.write.assert_called()

    @pytest.mark.asyncio
    @patch("scripts.rpj_downloader.httpx.AsyncClient")
    async def test_download_zip_http_error(
        self,
        mock_client_class: AsyncMock,
        temp_dir: Path
    ) -> None:
        """Test download zip with HTTP error.

        Args:
            mock_client_class: Mocked HTTP client class
            temp_dir: Temporary directory
        """
        url = "https://example.com/test.zip"
        filename = "test.zip"
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(httpx.RequestError):
            await rpj_downloader._download_zip(url, filename, output_dir)

    @pytest.mark.asyncio
    @patch("scripts.rpj_downloader.aiofiles.open")
    @patch("scripts.rpj_downloader.httpx.AsyncClient")
    async def test_download_zip_uses_correct_file_path(
        self,
        mock_client_class: AsyncMock,
        mock_aiofiles: AsyncMock,
        temp_dir: Path
    ) -> None:
        """
        Test that download uses dest_path, not filename for file open.

        Args:
            mock_client_class: Mocked HTTP client class
            mock_aiofiles: Mocked aiofiles class
            temp_dir: Temporary directory
        """
        url = "https://example.com/test.zip"
        filename = "test.zip"
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        dest_path = output_dir / filename

        zip_content = b"fake zip content"

        mock_file = AsyncMock()
        mock_file.write = AsyncMock()
        mock_aiofiles.return_value.__aenter__ = AsyncMock(return_value=mock_file)
        mock_aiofiles.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_response.aiter_bytes = Mock(return_value=async_iter_bytes(zip_content))

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        await rpj_downloader._download_zip(url, filename, output_dir)

        call_args = mock_aiofiles.call_args[0]
        assert call_args[0] == dest_path

class TestDownloadZipSync:
    """Test cases for download_zip function (synchronous wrapper)."""

    @patch("scripts.rpj_downloader.asyncio.run")
    @patch("scripts.rpj_downloader._download_zip")
    def test_download_zip_calls_async_version(
        self,
        mock_async_download: AsyncMock,
        mock_asyncio_run: Mock,
        temp_dir: Path
    ) -> None:
        """
        Test that download_zip calls _download_zip and runs it.

        Args:
            mock_async_download: Mocked async download function
            mock_asyncio_run: Mocked asyncio.run function
            temp_dir: Temporary directory
        """
        url = "https://example.com/test.zip"
        filename = "test.zip"
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        expected_path = output_dir / filename

        mock_async_download.return_value = expected_path
        mock_asyncio_run.return_value = expected_path

        result = rpj_downloader.download_zip(url, filename, output_dir)

        assert result == expected_path
        assert mock_asyncio_run.called
        call_args = mock_asyncio_run.call_args[0]
        assert len(call_args) > 0

class TestDownloadAU:
    """Test cases for download_au function."""

    @patch("scripts.rpj_downloader.extractor.extract_au")
    @patch.object(rpj_downloader, "download_zip")
    def test_download_au_calls_download_and_extract(
        self,
        mock_download_zip: Mock,
        mock_extract_au: Mock,
        temp_dir: Path
    ) -> None:
        """
        Test that download_au calls download_zip and extract_au.

        Args:
            mock_download_zip: Mocked download_zip function (from top decorator)
            mock_extract_au: Mocked extract_au function (from bottom decorator)
            temp_dir: Temporary directory
        """
        zip_path = temp_dir / "downloaded.zip"
        zip_path.write_bytes(b"zip content")
        mock_download_zip.return_value = zip_path

        au_output_dir = temp_dir / "au"
        au_output_dir.mkdir(parents=True, exist_ok=True)

        with patch.object(rpj_downloader, "AU_FILENAME", "INSPIRE_Administrative_Units_(AU).zip"):
            with patch.object(rpj_downloader, "AU_URL", "https://example.com/au.zip"):
                with patch.object(rpj_downloader, "AU_OUTPUT_DIR", au_output_dir):
                    rpj_downloader.download_au()

        mock_download_zip.assert_called_once()
        mock_extract_au.assert_called_once_with(zip_path)

class TestDownloadAD:
    """Test cases for download_ad function."""

    @patch("scripts.rpj_downloader.extractor.extract_ad")
    @patch.object(rpj_downloader, "download_zip")
    def test_download_ad_calls_download_and_extract(
        self,
        mock_download_zip: Mock,
        mock_extract_ad: Mock,
        temp_dir: Path
    ) -> None:
        """
        Test that download_ad calls download_zip and extract_ad.

        Args:
            mock_download_zip: Mocked download_zip function (from top decorator)
            mock_extract_ad: Mocked extract_ad function (from bottom decorator)
            temp_dir: Temporary directory
        """
        zip_path = temp_dir / "downloaded.zip"
        zip_path.write_bytes(b"zip content")
        mock_download_zip.return_value = zip_path

        ad_output_dir = temp_dir / "ad"
        ad_output_dir.mkdir(parents=True, exist_ok=True)

        with patch.object(rpj_downloader, "AD_FILENAME", "INSPIRE_Addresses_(AD).zip"):
            with patch.object(rpj_downloader, "AD_URL", "https://example.com/ad.zip"):
                with patch.object(rpj_downloader, "AD_OUTPUT_DIR", ad_output_dir):
                    rpj_downloader.download_ad()

        mock_download_zip.assert_called_once()
        mock_extract_ad.assert_called_once_with(zip_path)

class TestConstants:
    """Test cases for module constants."""

    def test_base_url(self) -> None:
        """Test that BASE_URL is set correctly."""
        assert rpj_downloader.BASE_URL == "https://geoportal.dgu.hr/services/atom/"

    def test_filenames(self) -> None:
        """Test that filenames are set correctly."""
        assert rpj_downloader.AU_FILENAME == "INSPIRE_Administrative_Units_(AU).zip"
        assert rpj_downloader.AD_FILENAME == "INSPIRE_Addresses_(AD).zip"

    def test_urls_are_constructed(self) -> None:
        """Test that URLs are properly constructed."""
        assert rpj_downloader.AU_URL.endswith(rpj_downloader.AU_FILENAME)
        assert rpj_downloader.AD_URL.endswith(rpj_downloader.AD_FILENAME)
        assert rpj_downloader.BASE_URL in rpj_downloader.AU_URL
        assert rpj_downloader.BASE_URL in rpj_downloader.AD_URL
