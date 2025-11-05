SELECT  KATASTARSKA_OPCINA_ID as id,
        MATICNI_BROJ as maticni_broj,
        NAZIV as naziv,
        STATUS_HARMONIZACIJE as status_harmonizacije,
        ST_Polygonize(geom) as geom
FROM katastarske_opcine;
