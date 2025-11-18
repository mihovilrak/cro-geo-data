CREATE OR REPLACE FUNCTION gs.get_native_bbox(table_json TEXT)
RETURNS TEXT
AS $$
DECLARE
    table_name TEXT;
    bbox GEOMETRY;
BEGIN

    SELECT SPLIT_PART(
        SPLIT_PART(
            table_json,
            '.',
            1
        ),
        '/',
        2
    ) INTO table_name;

    SELECT ST_EstimatedExtent('gs', table_name, 'geom') INTO bbox;

    RETURN format(
        '%I|%I|%I|%I',
        ST_XMin(bbox),
        ST_XMax(bbox),
        ST_YMin(bbox),
        ST_Ymax(bbox)
    );
END;
$$ LANGUAGE plpgsql;