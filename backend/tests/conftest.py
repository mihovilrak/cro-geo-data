"""
Pytest configuration and fixtures for cadastral app tests.
"""
from __future__ import annotations
import os
import sys
from typing import Any, TYPE_CHECKING
from pathlib import Path
from datetime import datetime

import pytest
from django.contrib.gis.geos import (
    Point,
    Polygon,
    MultiPolygon,
)
from django.utils import timezone
from django.db import connection
import dotenv
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

if TYPE_CHECKING:
    from psycopg2.extensions import Cursor

dotenv.load_dotenv()

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

pytest_plugins = ["pytest_django"]

def _find_sql_init_directory() -> Path:
    """
    Find the SQL init directory.
    
    Tries multiple locations:
    1. DB_INIT_DIR environment variable (for CI/CD or custom setups)
    2. /db/init (Docker mounted volume)
    3. Relative to backend directory: ../db/init (local development)
    4. Relative to repo root: db/init (if running from repo root)
    
    Returns:
        Path to the SQL init directory
        
    Raises:
        FileNotFoundError: If the directory cannot be found
    """
    if db_init_dir := os.getenv("DB_INIT_DIR"):
        path = Path(db_init_dir)
        if path.exists() and path.is_dir():
            return path

    docker_path = Path("/db/init")
    if docker_path.exists() and docker_path.is_dir():
        return docker_path

    backend_dir = Path(__file__).parent.parent
    repo_root = backend_dir.parent
    init_dir = repo_root / "db" / "init"
    if init_dir.exists() and init_dir.is_dir():
        return init_dir

    cwd_init_dir = Path.cwd() / "db" / "init"
    if cwd_init_dir.exists() and cwd_init_dir.is_dir():
        return cwd_init_dir
    
    raise FileNotFoundError(
        f"Could not find SQL init directory. Tried:\n"
        f"  - DB_INIT_DIR env var: {os.getenv('DB_INIT_DIR', 'not set')}\n"
        f"  - {docker_path}\n"
        f"  - {init_dir}\n"
        f"  - {cwd_init_dir}\n"
        f"Please set DB_INIT_DIR environment variable or ensure db/init exists."
    )


def _execute_sql_file(cursor: Cursor, sql_file: Path) -> None:
    """
    Execute a SQL file using the database cursor.
    
    Handles files with multiple statements by splitting on semicolons
    and executing each statement separately. This is necessary because
    psycopg2's execute() can only handle one statement at a time.
    
    Args:
        cursor: Database cursor
        sql_file: Path to SQL file
    """
    try:
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read().strip()
        
        if not sql_content:
            return

        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

        for statement in statements:
            if not statement:
                continue

            try:
                cursor.execute(statement)
            except Exception as e:
                error_msg = str(e).lower()
                if any(
                    phrase in error_msg
                    for phrase in ("already exists", "does not exist", "duplicate")
                ):
                    continue
                raise RuntimeError(
                    f"Error executing statement in {sql_file.name}: {e}"
                ) from e

    except Exception as e:
        raise RuntimeError(f"Error executing {sql_file.name}: {e}") from e


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(django_db_setup: Any, django_db_blocker: Any) -> None:
    """
    Automatically set up the test database schema by executing SQL init scripts.
    
    This fixture runs once per test session and creates all necessary
    schemas and tables for unmanaged models. It reads SQL files from the
    db/init directory, so the SQL scripts remain the source of truth.
    
    The fixture executes SQL files in this order:
    - Extensions (001_EXT_*.sql)
    - Schemas (002-006_SCHEMA_*.sql)
    - Tables (101-111_TBL_*.sql)
    - Views (301-313_VIEW_*.sql) - in dependency order
    - Materialized views (311_MVIEW_*.sql) - after regular views
    
    It skips:
    - Unmanaged tables (201-210_UTBL_*.sql) - not needed for basic tests
    - Functions (401-412_FUNC_*.sql) - may depend on data
    
    Environment variables:
        DB_INIT_DIR: Optional path to SQL init directory (for CI/CD)
    """
    with django_db_blocker.unblock():
        try:
            init_dir = _find_sql_init_directory()
        except FileNotFoundError as e:
            pytest.skip(f"Skipping database setup: {e}")
            return
        
        with connection.cursor() as cursor:
            sql_files = sorted(init_dir.glob("*.sql"))
            
            if not sql_files:
                pytest.skip(f"No SQL files found in {init_dir}")
                return

            needed_files = (
                file for file in sql_files
                if file.name.startswith(("0", "1", "3"))
            )
            for sql_file in needed_files:
                try:
                    _execute_sql_file(cursor, sql_file)
                except Exception as e:
                    print(f"Warning: {sql_file.name} - {e}")

            connection.commit()

@pytest.fixture
def sample_point() -> Point:
    """
    Create a sample point geometry in EPSG:3765.
    """
    return Point(500000, 5000000, srid=3765)

@pytest.fixture
def sample_polygon() -> Polygon:
    """
    Create a sample polygon geometry in EPSG:3765.
    """
    coords = (
        (500000, 5000000),
        (501000, 5000000),
        (501000, 5001000),
        (500000, 5001000),
        (500000, 5000000),
    )
    return Polygon(coords, srid=3765)

@pytest.fixture
def sample_multipolygon() -> MultiPolygon:
    """
    Create a sample multipolygon geometry in EPSG:3765.
    """
    coords = (
        (500000, 5000000),
        (501000, 5000000),
        (501000, 5001000),
        (500000, 5001000),
        (500000, 5000000),
    )
    polygon = Polygon(coords, srid=3765)
    return MultiPolygon(polygon, srid=3765)

@pytest.fixture
def sample_bbox() -> str:
    """
    Create a sample bounding box string for testing.
    """
    return "500000,5000000,501000,5001000"

@pytest.fixture
def sample_datetime() -> datetime:
    """
    Create a sample datetime for testing.
    """
    return timezone.now()

@pytest.fixture
def api_client() -> APIClient:
    """
    Create an API client for testing.
    """
    return APIClient()

@pytest.fixture
def api_request_factory() -> APIRequestFactory:
    """
    Create an API request factory for testing.
    """
    return APIRequestFactory()
