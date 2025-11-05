"""
Module for extracting and parsing geospatial data from ZIP archives containing GML files.

This script provides functions to extract 'DKP' (cadastral parcels and related layers) 
and 'AU' (administrative units) data from ZIP archives, parse them using SQL templates, 
and load them into a PostGIS-enabled PostgreSQL database. The appropriate SQL scripts 
and GML files are handled automatically, and logs are generated for each major step.

Environment variable:
    DB_STRING: Database connection string loaded from .env

Dependencies:
    - os
    - pathlib
    - subprocess
    - tempfile
    - zipfile
    - dotenv
    - logger

Intended for use within the backend data pipeline.
"""

import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

import dotenv

from logger import logger

dotenv.load_dotenv()

DB_STRING = os.getenv("DB_STRING")
SQL_DIR   = Path(__file__).parent / "sql"
AU_TYPES  = ('Država', 'Županija', 'Jedinica lokalne samouprave', 'Naselje')
DKP_TYPES = ('katastarske_opcine', 'katastarske_cestice', 'nacini_uporabe_zgrada')

def extract_dkp(zip_path: Path) -> None:
    """
    Extracts 'DKP' (cadastral parcels and related) GML files from the given ZIP archive,
    parses them using corresponding SQL templates, and loads them into PostGIS.

    Args:
        zip_path (Path): Path to the ZIP archive containing DKP GML files.

    Steps:
        1. Unzips the archive to a temporary directory.
        2. For each DKP layer type defined in DKP_TYPES:
            - Constructs the GML file path.
            - Parses the GML using the respective SQL template.
            - Loads the parsed data into PostGIS.
        3. Logs actions at each major step.
    """
    with zipfile.ZipFile(zip_path, 'r') as zf, \
        tempfile.TemporaryDirectory() as temp_dir:
        # Extract all files from the archive into the temp directory
        zf.extractall(temp_dir)
        logger.info(f"Extracted {zip_path}")

        # Iterate over each DKP type to parse and load its corresponding GML file
        for dkp in DKP_TYPES:
            gml_path = Path(temp_dir) / f"{dkp}.gml"
            parse_dkp_gml(gml_path, SQL_DIR / f"{dkp}.sql")
        logger.info(f"Parsed {gml_path.name} and loaded to PostGIS")

def extract_au(zip_path: Path) -> None:
    """
    Extracts 'AdministrativeUnits.gml' from the given ZIP archive,
    parses different administrative unit types, and loads them into PostGIS.

    Args:
        zip_path (Path): Path to the ZIP archive containing AdministrativeUnits.gml.

    Steps:
        1. Unzips the archive into a temporary directory.
        2. Locates the AdministrativeUnits.gml file.
        3. Iterates through each administrative unit type in AU_TYPES.
            - Calls parse_au_gml for each type to perform import using ogr2ogr.
        4. Logs actions at major steps.
    """
    with zipfile.ZipFile(zip_path, 'r') as zf, \
         tempfile.TemporaryDirectory() as temp_dir:
        # Extract all files from the zip archive into a temp directory.
        zf.extractall(temp_dir)
        logger.info(f"Extracted {zip_path}")

        # Location of GML file assumed to have this fixed name after extraction.
        gml_file = Path(temp_dir) / "AdministrativeUnits.gml"

        # For each AU (Administrative Unit) type, parse using template and import to DB.
        for au_type in AU_TYPES:
            parse_au_gml(gml_file, au_type)

        logger.info(f"Parsed {gml_file.name} and loaded to PostGIS")

def parse_au_gml(gml_file: Path, au_type: str) -> None:
    """
    Parses a specific administrative unit type from a GML file
    and loads it into the PostGIS database using ogr2ogr.

    Args:
        gml_file (Path): Path to the AdministrativeUnits.gml file.
        au_type (str): Name of administrative unit type (e.g., 'Država').
    """
    # Construct the SQL for ogr2ogr by replacing placeholder in SQL template with actual type.
    sql_query = (SQL_DIR / 'au.sql').read_text().replace('$AU_TYPE', au_type)

    # Run ogr2ogr subprocess to perform import into PostGIS with appropriate options.
    subprocess.run((
        "ogr2ogr",
        "-f", "PostgreSQL",
        DB_STRING,
        str(gml_file),
        "-sql", sql_query,
        "-nln", f"tmp_au_{au_type.lower()}",
        "-nlt", "PROMOTE_TO_MULTI",
        "-lco", "GEOMETRY_NAME=geom",
        "-lco", "ENCODING=UTF-8"
    ), check=True)

def parse_dkp_gml(gml_path: Path, sql_file: Path) -> None:
    """
    Parses a given DKP GML file using the provided SQL template
    and loads it into the PostGIS database using ogr2ogr.

    Args:
        gml_path (Path): Path to the DKP GML file.
        sql_file (Path): Path to the corresponding SQL template.
    """
    # Run ogr2ogr subprocess to import DKP data into PostGIS using @filename SQL syntax.
    subprocess.run((
        "ogr2ogr",
        "-f", "PostgreSQL",
        DB_STRING,
        str(gml_path),
        "-sql", f"@{sql_file}",
        "-nln", f"tmp_{gml_path.stem}",
        "-nlt", "PROMOTE_TO_MULTI",
        "-lco", "GEOMETRY_NAME=geom",
        "-lco", "ENCODING=UTF-8"
    ), check=True)
    logger.info(f"Parsed {gml_path.name} and loaded to PostGIS")
