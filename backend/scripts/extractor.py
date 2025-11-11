"""
Module for extracting and parsing geospatial data from ZIP archives containing GML files.

This script provides functions to extract 'DKP' (cadastral parcels and related layers)
and 'AU' (administrative units) data from ZIP archives, parse them using SQL templates,
and load them into a PostGIS-enabled PostgreSQL database. The appropriate SQL scripts
and GML files are handled automatically, and logs are generated for each major step.

Environment variable:
    DB_STRING: Database connection string loaded from .env

Intended for use within the backend data pipeline.
"""

from __future__ import annotations
import contextlib
import os
from pathlib import Path
import subprocess
import tempfile
from typing import NamedTuple, TYPE_CHECKING
import zipfile

import dotenv

from logger import logger

if TYPE_CHECKING:
    from collections.abc import Iterator

dotenv.load_dotenv()

class AuType(NamedTuple):
    name: str
    table: str
    parent: str | None = None

class AdType(NamedTuple):
    name: str
    gml_file: str

DB_STRING = os.getenv("DB_STRING")
SQL_DIR   = Path(__file__).parent / "sql"
AU_TYPES = (
    AuType('Država', 'staging.u_country'),
    AuType('Županija', 'staging.u_county'),
    AuType('Jedinica lokalne samouprave', 'staging.u_municipality', 'county'),
    AuType('Naselje', 'staging.u_settlement', 'municipality')
)
DKP_TYPES = (
    'cadastral_municipalities',
    'cadastral_parcels',
    'buildings'
)
AD_TYPES = (
    AdType('addresses', 'Address.gml'),
    AdType('streets', 'ThoroughfareName.gml'),
    AdType('postal_offices', 'PostalDescriptor.gml')
)

@contextlib.contextmanager
def extractor(zip_path: Path) -> Iterator[Path]:
    """
    Context manager for extracting a ZIP archive and returning
    the path to the extracted files.

    Args:
        zip_path (Path): Path to the ZIP archive to extract.

    Returns:
        Iterator[Path]: Iterator over the paths to the extracted files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)
                yield Path(temp_dir)
        finally:
            zip_path.unlink()

def extract_dkp(zip_path: Path) -> None:
    """
    Extracts 'DKP' (cadastral parcels and related) GML files from the given ZIP archive,
    parses them using corresponding SQL templates, and loads them into PostGIS.

    Args:
        zip_path (Path): Path to the ZIP archive containing DKP GML files.
    """
    with extractor(zip_path) as temp_dir:
        for dkp in DKP_TYPES:
            gml_path = temp_dir / f"{dkp}.gml"
            sql_path = SQL_DIR / f"{dkp}.sql"
            parse_gml(gml_path, f"@{sql_path}", f"staging.u_{dkp}")

def extract_au(zip_path: Path) -> None:
    """
    Extracts 'AdministrativeUnits.gml' from the given ZIP archive,
    parses different administrative unit types, and loads them into PostGIS.

    Args:
        zip_path (Path): Path to the ZIP archive containing AdministrativeUnits.gml.
    """
    with extractor(zip_path) as temp_dir:
        gml_file = temp_dir / "AdministrativeUnits.gml"

        for au_type in AU_TYPES:
            sql_query = (
                SQL_DIR / 'administrative_units.sql'
            ).read_text().replace('$AU_TYPE', au_type.name)
            if au_type.parent:
                sql_query = sql_query.replace('$PARENT', au_type.parent)
            else:
                sql_query = sql_query.replace('NULL AS $PARENT_id,', '')
            parse_gml(gml_file, sql_query, au_type.table)

def extract_ad(zip_path: Path) -> None:
    """
    Extracts 'Address.gml', 'ThoroughfareName.gml', 
    and 'PostalDescriptor.gml' from the given ZIP archive,
    parses them and loads them into PostGIS.

    Args:
        zip_path (Path): Path to the ZIP archive containing 
        Address.gml, ThoroughfareName.gml, and PostalDescriptor.gml files.
    """
    with extractor(zip_path) as temp_dir:
        for ad_type in AD_TYPES:
            gml_file = temp_dir / ad_type.gml_file
            sql = SQL_DIR / f'{ad_type.name}.sql'
            parse_gml(gml_file, f"@{sql}", f"staging.u_{ad_type.name}")

def parse_gml(gml_file: Path, sql: str, layer_name: str) -> None:
    """
    Parses a GML file using the provided SQL template
    and loads it into the PostGIS database using ogr2ogr.

    Args:
        gml_file (Path): Path to the GML file to parse.
        sql (str): SQL template to use for parsing.
        layer_name (str): Name of the layer to load into PostGIS.
    """
    subprocess.run((
        "ogr2ogr",
        "-f", "PostgreSQL",
        DB_STRING,
        str(gml_file),
        "-append",
        "-sql", sql,
        "-nln", layer_name,
        "-lco", "ENCODING=UTF-8",
        "--config", "PG_USE_COPY=YES"
    ), check=True)
    logger.info(f"Parsed {gml_file.name} and loaded to PostGIS")
