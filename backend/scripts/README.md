# Scripts Documentation

This directory contains Python scripts for downloading, extracting, and processing Croatian geospatial data from various government sources. The scripts handle data ingestion from DGU Geoportal and OSS (Uređenja zemlja) ATOM feeds, extract GML files from ZIP archives, and load them into a PostGIS-enabled PostgreSQL database.

## Overview

The scripts are organized into three main components:

1. **Downloaders** - Fetch data from remote sources
2. **Extractor** - Process ZIP archives and load data into PostGIS
3. **SQL Templates** - Define data transformations for GML parsing

## Scripts

### 1. `rpj_downloader.py`

Downloads Administrative Units (AU) and Addresses (AD) datasets from the DGU Geoportal.

#### Features
- Downloads INSPIRE-compliant Administrative Units and Addresses datasets
- Automatically extracts downloaded ZIP files
- Organizes downloads by date in separate directories

#### Functions

##### `download_au() -> None`
Downloads the Administrative Units dataset from DGU Geoportal and extracts it.

**Source URL:** `https://geoportal.dgu.hr/services/atom/INSPIRE_Administrative_Units_(AU).zip`

**Output:** Extracted to `backend/data/downloads/au/{DATE}/`

##### `download_ad() -> None`
Downloads the Addresses dataset from DGU Geoportal and extracts it.

**Source URL:** `https://geoportal.dgu.hr/services/atom/INSPIRE_Addresses_(AD).zip`

**Output:** Extracted to `backend/data/downloads/ad/{DATE}/`

#### Usage

```python
from scripts.rpj_downloader import download_au, download_ad

# Download Administrative Units
download_au()

# Download Addresses
download_ad()
```

#### Dependencies
- `aiofiles` - Async file operations
- `httpx` - HTTP client for async downloads
- `extractor` - Module for extracting and processing ZIP files

---

### 2. `dkp_downloader.py`

Downloads cadastral municipality ZIP files from the OSS (Uređenja zemlja) ATOM feed. This is the main downloader for cadastral parcel data (DKP - Katastarske čestice).

#### Features
- Parses ATOM feed XML to discover available cadastral municipality files
- Concurrent async downloads with configurable concurrency limits
- Automatic retry and error handling
- Progress logging for large batch downloads

#### Class: `DKPDownloader`

##### `__init__(self) -> None`
Initializes the downloader and creates output directory structure.

**Output Directory:** `backend/data/downloads/dkp/{DATE}/`

##### `download(max_concurrent_downloads: int = 10) -> list[Path]`
Main entry point for downloading all cadastral municipality files.

**Parameters:**
- `max_concurrent_downloads` (int): Maximum number of concurrent downloads (default: 10)

**Returns:**
- `list[Path]`: List of paths to downloaded ZIP files

**Process:**
1. Downloads ATOM feed XML from `https://oss.uredjenazemlja.hr/oss/public/atom/atom_feed.xml`
2. Parses XML to extract entry information (ID, title, URL, update date)
3. Downloads all ZIP files concurrently with semaphore-based rate limiting
4. Returns list of successfully downloaded file paths

#### Usage

```python
from scripts.dkp_downloader import DKPDownloader

# Create downloader instance
downloader = DKPDownloader()

# Download all cadastral municipality files (10 concurrent downloads)
downloaded_files = downloader.download(max_concurrent_downloads=10)

# Process downloaded files
for file_path in downloaded_files:
    # Extract and load into database
    extractor.extract_dkp(file_path)
```

#### Internal Methods

- `_download_atom_feed()` - Downloads the ATOM feed XML asynchronously
- `_parse_atom_feed()` - Parses the ATOM feed XML and extracts entries
- `_extract_entries()` - Extracts entry information using parallel processing
- `scrape()` - Downloads all ZIP files asynchronously with concurrency control

#### Dependencies
- `aiofiles` - Async file operations
- `httpx` - HTTP client for async downloads
- `xml.etree.ElementTree` - XML parsing

---

### 3. `extractor.py`

Core module for extracting GML files from ZIP archives and loading them into PostGIS using `ogr2ogr`. Handles data transformation through SQL templates.

#### Features
- Automatic ZIP extraction with cleanup
- GML parsing using SQL templates
- PostGIS integration via `ogr2ogr`
- Support for multiple data types (AU, AD, DKP)

#### Functions

##### `extract_dkp(zip_path: Path) -> None`
Extracts DKP (cadastral parcels) GML files from ZIP archive and loads them into PostGIS.

**Process:**
1. Extracts ZIP to temporary directory
2. Processes three GML files:
   - `katastarske_opcine.gml` → `tmp_katastarske_opcine`
   - `katastarske_cestice.gml` → `tmp_katastarske_cestice`
   - `nacini_uporabe_zgrada.gml` → `tmp_nacini_uporabe_zgrada`
3. Uses corresponding SQL templates from `sql/` directory
4. Loads data into PostGIS using `ogr2ogr`
5. Deletes ZIP file after processing

**SQL Templates Used:**
- `sql/katastarske_opcine.sql`
- `sql/katastarske_cestice.sql`
- `sql/nacini_uporage_zgrade.sql`

##### `extract_au(zip_path: Path) -> None`
Extracts Administrative Units GML file and loads different administrative unit types into PostGIS.

**Process:**
1. Extracts ZIP to temporary directory
2. Processes `AdministrativeUnits.gml` for four unit types:
   - `Država` (Country)
   - `Županija` (County)
   - `Jedinica lokalne samouprave` (Local self-government unit)
   - `Naselje` (Settlement)
3. Creates separate temporary tables: `tmp_au_država`, `tmp_au_županija`, etc.
4. Uses `sql/administrative_units.sql` template with type substitution

##### `extract_ad(zip_path: Path) -> None`
Extracts Addresses GML file and loads addresses into PostGIS.

**Process:**
1. Extracts ZIP to temporary directory
2. Processes `Addresses.gml`
3. Loads to `tmp_ad` table using `sql/adrese.sql` template

##### `parse_gml(gml_file: Path, sql: str, layer_name: str) -> None`
Core function that uses `ogr2ogr` to parse GML files and load them into PostGIS.

**Parameters:**
- `gml_file` (Path): Path to the GML file
- `sql` (str): SQL query or path to SQL file (with `@` prefix)
- `layer_name` (str): Name of the PostGIS table/layer

**ogr2ogr Options:**
- `-f PostgreSQL` - Output format
- `-nln {layer_name}` - Layer/table name
- `-nlt PROMOTE_TO_MULTI` - Promote geometries to Multi geometries
- `-lco GEOMETRY_NAME=geom` - Geometry column name
- `-lco ENCODING=UTF-8` - Character encoding

#### Usage

```python
from pathlib import Path
from scripts.extractor import extract_dkp, extract_au, extract_ad

# Extract DKP data
zip_path = Path("backend/data/downloads/dkp/2024-01-15/some_municipality.zip")
extract_dkp(zip_path)

# Extract Administrative Units
au_zip = Path("backend/data/downloads/au/2024-01-15/INSPIRE_Administrative_Units_(AU).zip")
extract_au(au_zip)

# Extract Addresses
ad_zip = Path("backend/data/downloads/ad/2024-01-15/INSPIRE_Addresses_(AD).zip")
extract_ad(ad_zip)
```

#### Environment Variables

- `DB_STRING` - PostgreSQL connection string (required)
  - Format: `PG:host=localhost port=5432 user=postgres dbname=gis password=...`
  - Loaded from `.env` file via `python-dotenv`

#### Dependencies
- `ogr2ogr` (GDAL) - Must be installed and available in PATH
- `python-dotenv` - Environment variable management
- `subprocess` - For executing `ogr2ogr` commands

---

## SQL Templates

SQL templates in the `sql/` directory define how GML data is transformed when loaded into PostGIS. These are used by `ogr2ogr` with the `-sql` parameter.

### `administrative_units.sql`

Transforms Administrative Units GML data. The `$AU_TYPE` placeholder is replaced with the specific administrative unit type.

**Columns:**
- `id` - Extracted from `localId` (integer after the dot)
- `maticni_broj` - National code (integer)
- `naziv` - Name (text)
- `datum_promjene` - Change date (beginLifespanVersion)
- `geom` - Geometry

**Usage:** Used with type substitution for each administrative unit level.

### `adrese.sql`

Transforms Addresses GML data.

**Columns:**
- `id` - Extracted from `localId` (integer after the dot)
- `alternativna_adresa` - Alternate address
- `geom` - Geometry

### `katastarske_opcine.sql`

Transforms cadastral municipality (katastarske općine) GML data.

**Columns:**
- `id` - Cadastral municipality ID
- `maticni_broj` - National code
- `naziv` - Name
- `status_harmonizacije` - Harmonization status
- `geom` - Geometry (polygonized)

**Note:** Uses `ST_Polygonize()` to convert geometry to polygons.

### `katastarske_cestice.sql`

Transforms cadastral parcel (katastarske čestice) GML data.

**Columns:**
- `id` - Parcel ID (CESTICA_ID)
- `broj_cestice` - Parcel number
- `povrsina_graficka` - Graphical area
- `ko_maticni_broj` - Cadastral municipality national code
- `geom` - Geometry

### `nacini_uporage_zgrade.sql`

Transforms building usage types (načini uporabe zgrada) GML data.

**Columns:**
- `id` - Building ID (ZGRADA_ID)
- `broj_zgrade` - Building number
- `ko_maticni_broj` - Cadastral municipality national code
- `uporaba_sifra` - Usage code
- `geom` - Geometry

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources                             │
├─────────────────────────────────────────────────────────────┤
│ 1. DGU Geoportal                                            │
│    - Administrative Units (AU)                              │
│    - Addresses (AD)                                         │
│                                                             │
│ 2. OSS ATOM Feed                                            │
│    - Cadastral Municipalities (DKP)                         │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Download Scripts                           │
├─────────────────────────────────────────────────────────────┤
│  rpj_downloader.py  →  Downloads AU & AD ZIP files          │
│  dkp_downloader.py  →  Downloads DKP ZIP files from ATOM    │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              ZIP Files (backend/data/downloads/)            │
├─────────────────────────────────────────────────────────────┤
│  au/{DATE}/INSPIRE_Administrative_Units_(AU).zip            │
│  ad/{DATE}/INSPIRE_Addresses_(AD).zip                       │
│  dkp/{DATE}/*.zip (multiple municipality files)             │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Extractor Module                           │
├─────────────────────────────────────────────────────────────┤
│  extractor.py                                               │
│   1. Extract ZIP to temporary directory                     │
│   2. Locate GML files                                       │
│   3. Apply SQL templates for transformation                 │
│   4. Use ogr2ogr to load into PostGIS                       │
│   5. Clean up ZIP file                                      │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              PostGIS Database (Temporary Tables)            │
├─────────────────────────────────────────────────────────────┤
│  tmp_katastarske_opcine                                     │
│  tmp_katastarske_cestice                                    │
│  tmp_nacini_uporabe_zgrada                                  │
│  tmp_au_država, tmp_au_županija, ...                        │
│  tmp_ad                                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Requirements

### System Dependencies

- **GDAL/OGR** - Required for `ogr2ogr` command-line tool
  - Install: `apt-get install gdal-bin` (Linux) or `brew install gdal` (macOS)
  - Windows: Download from [OSGeo4W](https://trac.osgeo.org/osgeo4w/)

- **PostgreSQL with PostGIS** - Database must have PostGIS extension enabled

### Python Dependencies

```txt
aiofiles
httpx
python-dotenv
```

### Environment Setup

Create a `.env` file in the project root with:

```env
DB_STRING=PG:host=localhost port=5432 user=postgres dbname=gis password=your_password
```

---

## Usage Examples

### Complete Workflow: Download and Process DKP Data

```python
from pathlib import Path
from scripts.dkp_downloader import DKPDownloader
from scripts.extractor import extract_dkp

# Download all cadastral municipality files
downloader = DKPDownloader()
downloaded_files = downloader.download(max_concurrent_downloads=10)

# Process each downloaded file
for zip_path in downloaded_files:
    try:
        extract_dkp(zip_path)
        print(f"Successfully processed: {zip_path.name}")
    except Exception as e:
        print(f"Error processing {zip_path.name}: {e}")
```

### Download and Process Administrative Units

```python
from scripts.rpj_downloader import download_au

# Download and extract AU data
download_au()
```

### Download and Process Addresses

```python
from scripts.rpj_downloader import download_ad

# Download and extract AD data
download_ad()
```

---

## Error Handling

All scripts use the project's logging system (`backend/logger.py`) for error reporting. Errors are logged with appropriate levels:

- **INFO** - Normal operations (downloads, extractions)
- **WARNING** - Non-fatal issues (missing entries, skipped files)
- **ERROR** - Fatal errors (download failures, processing errors)

The `extractor.py` module uses `subprocess.check=True` which will raise exceptions if `ogr2ogr` fails, ensuring data integrity.

---

## Notes

- Downloaded ZIP files are automatically deleted after extraction to save disk space
- All extractions use temporary directories that are cleaned up automatically
- Data is loaded into temporary tables (prefixed with `tmp_`) - you may need additional scripts to move data to production tables
- The ATOM feed is cached locally to avoid re-downloading on subsequent runs
- Concurrent downloads are rate-limited to avoid overwhelming the source servers

---

## Troubleshooting

### `ogr2ogr: command not found`
- Install GDAL/OGR tools for your platform
- Ensure `ogr2ogr` is in your system PATH

### Database connection errors
- Verify `DB_STRING` in `.env` file
- Check PostgreSQL is running and accessible
- Ensure PostGIS extension is installed: `CREATE EXTENSION postgis;`

### Download timeouts
- Increase timeout values in `httpx.AsyncClient(timeout=...)`
- Reduce `max_concurrent_downloads` to avoid rate limiting
- Check network connectivity to source servers

### Memory issues with large files
- Process files individually rather than in batches
- Ensure sufficient disk space in temporary directory
- Consider processing during off-peak hours

