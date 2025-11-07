SELECT  ZGRADA_ID as id,
        BROJ_ZGRADE as building_number,
        MATICNI_BROJ_KO as cadastral_municipality_code,
        SIFRA_NACINA_UPORABE_ZGRADE as usage_code,
        geom
FROM "ZGRADE";