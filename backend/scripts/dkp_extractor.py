from collections.abc import Mapping
import os
from pathlib import Path
import zipfile

import dotenv
import geopandas as gpd
from sqlalchemy import create_engine

from logger import logger

dotenv.load_dotenv()
DB_STRING = os.getenv("DB_STRING")

KO_COLUMNS = {
    'KATASTARSKA_OPCINA_ID': 'id',
    'MATICNI_BROJ': 'maticni_broj',
    'NAZIV': 'naziv',
    'STATUS_HARMONIZACIJE': 'status_harmonizacije',
    'geometry': 'geom'
}

KC_COLUMNS = {
    'CESTICA_ID': 'id',
    'BROJ_CESTICE': 'broj_cestice',
    'GRAFICKA_POVRSINA': 'graficka_povrsina',
    'MATICNI_BROJ_KO': 'ko_maticni_broj',
    'geometry': 'geom'
}

ZGRADA_COLUMNS = {
    'ZGRADA_ID': 'id',
    'BROJ_ZGRADE': 'broj_zgrade',
    'MATICNI_BROJ_KO': 'ko_maticni_broj',
    'SIFRA_NACINA_UPORABE': 'uporaba_sifra',
    'geometry': 'geom'
}

class DKPExtractor:
    def __init__(self, zip_path: Path) -> None:
        self.zip_path = zip_path
        self.ko_mb    = self.zip_path.stem.split('-')[-1]
        self.extracted_path = zip_path.parent / zip_path.stem
        self.extracted_path.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(DB_STRING)

    def extract(self) -> None:
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            zf.extractall(self.extracted_path)
            logger.info(f"Extracted {self.zip_path} to {self.extracted_path}")

        self.gml_files = self.extracted_path.glob("*.gml")

    def parse_gml(self, gml: Path, columns: Mapping[str, str]) -> None:
        gdf = gpd.read_file(gml)
        gdf_cleaned = gdf[columns.keys()].rename(columns=columns)
        if gdf_cleaned.count() == 1:
            gdf_cleaned['geom'] = gdf_cleaned['geom'].polygonize()
        gdf_cleaned.to_postgis(
            f'tmp_{gml.stem}_{self.ko_mb}',
            self.engine,
            if_exists='replace',
            schema=f'tmp_{gml.stem}'
        )
        logger.info(f"Parsed {gml.name} and loaded to PostGIS schema 'tmp_{gml.stem}'")

    def parse_all(self) -> None:
        for gml in self.gml_files:
            match gml.stem:
                case 'katastarske_opcine':
                    self.parse_gml(gml, KO_COLUMNS)
                case 'katastarske_cestice':
                    self.parse_gml(gml, KC_COLUMNS)
                case 'nacini_uporabe_zgrada':
                    self.parse_gml(gml, ZGRADA_COLUMNS)
                case _:
                    pass