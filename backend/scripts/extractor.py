import os
from pathlib import Path
import zipfile

import dotenv
import geopandas as gpd
from sqlalchemy import create_engine

from logger import logger

dotenv.load_dotenv()
DB_STRING = os.getenv("DB_STRING")

AU_COLUMNS = {
    'localId': 'id',
    'nationalCode': 'maticni_broj',
    'text': 'naziv',
    'beginLifespanVersion': 'datum_promjene',
    'LocalisedCharacterString': 'au_type',
    'geometry': 'geom'
}

class AUExtractor:
    def __init__(self, zip_path: Path) -> None:
        self.zip_path = zip_path
        self.extracted_path = zip_path.parent / zip_path.stem
        self.engine = create_engine(DB_STRING)

    def extract(self) -> None:
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            zf.extractall(self.extracted_path)
            logger.info(f"Extracted {self.zip_path} to {self.extracted_path}")

        self.gml_file = self.extracted_path / "AdministrativeUnits.gml"

    def read_gml(self) -> None:
        gdf = gpd.read_file(self.gml_file)
        gdf = gdf[AU_COLUMNS.keys()].rename(columns=AU_COLUMNS)
        gdf['id'] = gdf['id'].str.split('.')[1].astype(int)
    
        country_gdf = gdf[gdf['au_type'] == 'Država'].drop(columns=['au_type'])
        county_gdf  = gdf[gdf['au_type'] == 'Županija'].drop(columns=['au_type'])

        municipality_gdf = (
            gdf[gdf['au_type'] == 'Jedinica lokalne samouprave']
        ).drop(columns=['au_type'])

        settlement_gdf = gdf[gdf['au_type'] == 'Naselje'].drop(columns=['au_type'])

        country_gdf.to_postgis(
            'tmp_au_country',
            self.engine,
            if_exists='replace',
            schema='tmp_au'
        )
        county_gdf.to_postgis(
            'tmp_au_county',
            self.engine,
            if_exists='replace',
            schema='tmp_au'
        )
        municipality_gdf.to_postgis(
            'tmp_au_municipality',
            self.engine,
            if_exists='replace',
            schema='tmp_au'
        )
        settlement_gdf.to_postgis(
            'tmp_au_settlement',
            self.engine,
            if_exists='replace',
            schema='tmp_au'
        )
        logger.info(f"Loaded administrative units to PostGIS schema 'tmp_au'")