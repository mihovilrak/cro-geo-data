SELECT KATASTARSKA_OPCINA_ID as id,
    MATICNI_BROJ as national_code,
    NAZIV as name,
    STATUS_HARMONIZACIJE as harmonization_status,
    ST_Polygonize(geom) as geom
FROM katastarske_opcine;
