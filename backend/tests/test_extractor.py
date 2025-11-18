"""
Tests for the extractor module.
"""
from collections.abc import Iterator
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import zipfile

import pytest

from scripts import extractor

@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """
    Create a temporary directory for tests.

    Returns:
        Iterator[Path]: Iterator over the path to the temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_zip_file(temp_dir: Path) -> Path:
    """
    Create a sample ZIP file with test content.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to the sample ZIP file
    """
    zip_path = temp_dir / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("test_file.txt", "test content")
        zf.writestr("subdir/nested.txt", "nested content")
    return zip_path

@pytest.fixture
def sample_dkp_zip(temp_dir: Path) -> Path:
    """
    Create a sample DKP ZIP file with GML files.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to the sample DKP ZIP file
    """
    zip_path = temp_dir / "dkp.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr(
            "katastarske_opcine.gml", "<?xml version='1.0'?><gml>opcine</gml>"
        )
        zf.writestr(
            "katastarske_cestice.gml", "<?xml version='1.0'?><gml>cestice</gml>"
        )
        zf.writestr(
            "nacini_uporabe_zgrada.gml", "<?xml version='1.0'?><gml>zgrada</gml>"
        )
    return zip_path

@pytest.fixture
def sample_au_zip(temp_dir: Path) -> Path:
    """
    Create a sample AU ZIP file with AdministrativeUnits.gml.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to the sample AU ZIP file
    """
    zip_path = temp_dir / "au.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("AdministrativeUnits.gml", "<?xml version='1.0'?><gml>admin</gml>")
    return zip_path

@pytest.fixture
def sample_ad_zip(temp_dir: Path) -> Path:
    """
    Create a sample AD ZIP file with Addresses.gml.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to the sample AD ZIP file
    """
    zip_path = temp_dir / "ad.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("Addresses.gml", "<?xml version='1.0'?><gml>addresses</gml>")
    return zip_path

class TestExtractor:
    """Test cases for extractor context manager."""

    def test_extractor_extracts_zip(self, sample_zip_file: Path) -> None:
        """
        Test that extractor extracts ZIP file correctly.

        Args:
            sample_zip_file: Path to the sample ZIP file
        """
        with extractor.extractor(sample_zip_file) as temp_dir:
            assert temp_dir.exists()
            assert (temp_dir / "test_file.txt").exists()
            assert (temp_dir / "subdir" / "nested.txt").exists()
            assert (temp_dir / "test_file.txt").read_text() == "test content"

        assert not sample_zip_file.exists()

    def test_extractor_deletes_zip_on_exception(self, sample_zip_file: Path) -> None:
        """Test that extractor deletes ZIP file even when exception occurs.

        Args:
            sample_zip_file: Path to the sample ZIP file
        """
        try:
            with extractor.extractor(sample_zip_file) as temp_dir:
                assert temp_dir.exists()
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert not sample_zip_file.exists()

    def test_extractor_with_invalid_zip(self, temp_dir: Path) -> None:
        """
        Test that extractor raises error with invalid ZIP file.

        Args:
            temp_dir: Temporary directory
        """
        invalid_zip = temp_dir / "invalid.zip"
        invalid_zip.write_text("not a zip file")

        with pytest.raises(zipfile.BadZipFile):
            with extractor.extractor(invalid_zip):
                pass

class TestExtractDKP:
    """Test cases for extract_dkp function."""

    @patch("scripts.extractor.parse_gml")
    @patch("scripts.extractor.SQL_DIR", Path("/fake/sql"))
    def test_extract_dkp_calls_parse_gml_for_all_types(
        self,
        mock_parse_gml: Mock,
        sample_dkp_zip: Path,
        temp_dir: Path
    ) -> None:
        """
        Test that extract_dkp calls parse_gml for all DKP types.

        Args:
            mock_parse_gml: Mocked parse_gml function
            sample_dkp_zip: Path to the sample DKP ZIP file
            temp_dir: Temporary directory
        """
        test_zip = temp_dir / "test_dkp.zip"
        with zipfile.ZipFile(sample_dkp_zip, 'r') as src:
            with zipfile.ZipFile(test_zip, 'w') as dst:
                for item in src.infolist():
                    data = src.read(item.filename)
                    dst.writestr(item, data)

        extractor.extract_dkp(test_zip)

        assert mock_parse_gml.call_count == 3

        calls = [call[0] for call in mock_parse_gml.call_args_list]
        gml_files = [str(call[0]) for call in calls]
        sql_args = [str(call[1]) for call in calls]
        layer_names = [call[2] for call in calls]

        assert any("cadastral_municipalities.gml" in gml for gml in gml_files)
        assert any("cadastral_parcels.gml" in gml for gml in gml_files)
        assert any("buildings.gml" in gml for gml in gml_files)

        assert "staging.u_cadastral_municipalities" in layer_names
        assert "staging.u_cadastral_parcels" in layer_names
        assert "staging.u_buildings" in layer_names

    @patch("scripts.extractor.parse_gml")
    def test_extract_dkp_deletes_zip_after_extraction(
        self,
        mock_parse_gml: Mock,
        sample_dkp_zip: Path,
        temp_dir: Path
    ) -> None:
        """
        Test that extract_dkp deletes ZIP file after extraction.

        Args:
            mock_parse_gml: Mocked parse_gml function
            sample_dkp_zip: Path to the sample DKP ZIP file
            temp_dir: Temporary directory
        """
        test_zip = temp_dir / "test_dkp.zip"
        with zipfile.ZipFile(sample_dkp_zip, 'r') as src:
            with zipfile.ZipFile(test_zip, 'w') as dst:
                for item in src.infolist():
                    data = src.read(item.filename)
                    dst.writestr(item, data)

        extractor.extract_dkp(test_zip)

        assert not test_zip.exists()

class TestExtractAU:
    """Test cases for extract_au function."""

    @patch("scripts.extractor.parse_gml")
    @patch("scripts.extractor.SQL_DIR", Path("/fake/sql"))
    def test_extract_au_calls_parse_gml_for_all_au_types(
        self,
        mock_parse_gml: Mock,
        sample_au_zip: Path,
        temp_dir: Path
    ) -> None:
        """
        Test that extract_au calls parse_gml for all AU types.

        Args:
            mock_parse_gml: Mocked parse_gml function
            sample_au_zip: Path to the sample AU ZIP file
            temp_dir: Temporary directory
        """
        mock_sql_dir = temp_dir / "sql"
        mock_sql_dir.mkdir()
        mock_sql_file = mock_sql_dir / "administrative_units.sql"
        mock_sql_file.write_text("SELECT * FROM table WHERE type = '$AU_TYPE'")

        test_zip = temp_dir / "test_au.zip"
        with zipfile.ZipFile(sample_au_zip, 'r') as src:
            with zipfile.ZipFile(test_zip, 'w') as dst:
                for item in src.infolist():
                    data = src.read(item.filename)
                    dst.writestr(item, data)

        with patch("scripts.extractor.SQL_DIR", mock_sql_dir):
            extractor.extract_au(test_zip)

        assert mock_parse_gml.call_count == 4

        calls = [call[0] for call in mock_parse_gml.call_args_list]
        layer_names = [call[2] for call in calls]

        assert "staging.u_country" in layer_names
        assert "staging.u_county" in layer_names
        assert "staging.u_municipality" in layer_names
        assert "staging.u_settlement" in layer_names

    @patch("scripts.extractor.parse_gml")
    def test_extract_au_deletes_zip_after_extraction(
        self,
        mock_parse_gml: Mock,
        sample_au_zip: Path,
        temp_dir: Path
    ) -> None:
        """
        Test that extract_au deletes ZIP file after extraction.

        Args:
            mock_parse_gml: Mocked parse_gml function
            sample_au_zip: Path to the sample AU ZIP file
            temp_dir: Temporary directory
        """
        test_zip = temp_dir / "test_au.zip"
        with zipfile.ZipFile(sample_au_zip, 'r') as src:
            with zipfile.ZipFile(test_zip, 'w') as dst:
                for item in src.infolist():
                    data = src.read(item.filename)
                    dst.writestr(item, data)

        mock_sql_dir = temp_dir / "sql"
        mock_sql_dir.mkdir()
        mock_sql_file = mock_sql_dir / "administrative_units.sql"
        mock_sql_file.write_text("SELECT * FROM table WHERE type = '$AU_TYPE'")

        with patch("scripts.extractor.SQL_DIR", mock_sql_dir):
            extractor.extract_au(test_zip)

        assert not test_zip.exists()

class TestExtractAD:
    """Test cases for extract_ad function."""

    @patch("scripts.extractor.parse_gml")
    @patch("scripts.extractor.SQL_DIR", Path("/fake/sql"))
    def test_extract_ad_calls_parse_gml(
        self,
        mock_parse_gml: Mock,
        sample_ad_zip: Path,
        temp_dir: Path
    ) -> None:
        """
        Test that extract_ad calls parse_gml with correct arguments.

        Args:
            mock_parse_gml: Mocked parse_gml function
            sample_ad_zip: Path to the sample AD ZIP file
            temp_dir: Temporary directory
        """
        test_zip = temp_dir / "test_ad.zip"
        with zipfile.ZipFile(sample_ad_zip, 'r') as src:
            with zipfile.ZipFile(test_zip, 'w') as dst:
                for item in src.infolist():
                    data = src.read(item.filename)
                    dst.writestr(item, data)

        extractor.extract_ad(test_zip)

        assert mock_parse_gml.call_count == 3

        gml_files = [str(call[0][0]) for call in mock_parse_gml.call_args_list]
        assert any("Address.gml" in gml for gml in gml_files)
        assert any("ThoroughfareName.gml" in gml for gml in gml_files)
        assert any("PostalDescriptor.gml" in gml for gml in gml_files)

    @patch("scripts.extractor.parse_gml")
    def test_extract_ad_deletes_zip_after_extraction(
        self,
        mock_parse_gml: Mock,
        sample_ad_zip: Path,
        temp_dir: Path
    ) -> None:
        """
        Test that extract_ad deletes ZIP file after extraction.

        Args:
            mock_parse_gml: Mocked parse_gml function
            sample_ad_zip: Path to the sample AD ZIP file
            temp_dir: Temporary directory
        """
        test_zip = temp_dir / "test_ad.zip"
        with zipfile.ZipFile(sample_ad_zip, 'r') as src:
            with zipfile.ZipFile(test_zip, 'w') as dst:
                for item in src.infolist():
                    data = src.read(item.filename)
                    dst.writestr(item, data)

        extractor.extract_ad(test_zip)

        assert not test_zip.exists()

class TestParseGML:
    """Test cases for parse_gml function."""

    @patch("scripts.extractor.subprocess.run")
    @patch("scripts.extractor.logger")
    def test_parse_gml_calls_ogr2ogr_with_correct_args(
        self,
        mock_logger: Mock,
        mock_subprocess: Mock,
        temp_dir: Path
    ) -> None:
        """
        Test that parse_gml calls ogr2ogr with correct arguments.

        Args:
            mock_logger: Mocked logger function
            mock_subprocess: Mocked subprocess function
            temp_dir: Temporary directory
        """
        gml_file = temp_dir / "test.gml"
        gml_file.write_text("<?xml version='1.0'?><gml>test</gml>")
        sql_query = "SELECT * FROM table"
        layer_name = "test_layer"

        with patch("scripts.extractor.DB_STRING", "PG:dbname=test"):
            extractor.parse_gml(gml_file, sql_query, layer_name)

        assert mock_subprocess.call_count == 1

        call_args = mock_subprocess.call_args[0][0]
        assert call_args[:5] == (
            "ogr2ogr",
            "-f",
            "PostgreSQL",
            "PG:dbname=test",
            str(gml_file),
        )
        assert "-append" in call_args
        assert "-lco" in call_args
        assert "ENCODING=UTF-8" in call_args
        assert "ENCODING=UTF-8" in call_args
        assert call_args[call_args.index("-nln") + 1] == layer_name
        assert call_args[call_args.index("-sql") + 1] == sql_query
        assert str(gml_file) in call_args

        assert mock_subprocess.call_args[1]["check"] is True

        mock_logger.info.assert_called_once()

    @patch("scripts.extractor.subprocess.run")
    def test_parse_gml_raises_on_subprocess_error(
        self,
        mock_subprocess: Mock,
        temp_dir: Path
    ) -> None:
        """
        Test that parse_gml raises error when subprocess fails.

        Args:
            mock_subprocess: Mocked subprocess function
            temp_dir: Temporary directory
        """
        gml_file = temp_dir / "test.gml"
        gml_file.write_text("<?xml version='1.0'?><gml>test</gml>")
        sql_query = "SELECT * FROM table"
        layer_name = "test_layer"

        import subprocess
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "ogr2ogr")

        with patch("scripts.extractor.DB_STRING", "PG:dbname=test"):
            with pytest.raises(subprocess.CalledProcessError):
                extractor.parse_gml(gml_file, sql_query, layer_name)

    @patch("scripts.extractor.subprocess.run")
    def test_parse_gml_with_sql_file_path(
        self,
        mock_subprocess: Mock,
        temp_dir: Path
    ) -> None:
        """
        Test that parse_gml handles SQL file path with @ prefix.

        Args:
            mock_subprocess: Mocked subprocess function
            temp_dir: Temporary directory
        """
        gml_file = temp_dir / "test.gml"
        gml_file.write_text("<?xml version='1.0'?><gml>test</gml>")
        sql_path = temp_dir / "query.sql"
        sql_query = f"@{sql_path}"
        layer_name = "test_layer"

        with patch("scripts.extractor.DB_STRING", "PG:dbname=test"):
            extractor.parse_gml(gml_file, sql_query, layer_name)

        call_args = mock_subprocess.call_args[0][0]
        sql_arg = call_args[call_args.index("-sql") + 1]
        assert sql_arg == sql_query
        assert sql_arg.startswith("@")
