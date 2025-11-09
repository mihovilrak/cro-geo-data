SELECT CESTICA_ID as id,
    BROJ_CESTICE as parcel_number,
    POVRSINA_GRAFICKA as graphical_area,
    MATICNI_BROJ_KO as cadastral_municipality_code,
    geom
FROM "CESTICE";