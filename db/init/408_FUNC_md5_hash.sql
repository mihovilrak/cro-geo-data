CREATE OR REPLACE FUNCTION staging.md5_hash(
    table_name TEXT,
    pk_column TEXT,
    columns TEXT[]
)
RETURNS TABLE(id TEXT, row_hash TEXT)
AS $$

DECLARE
    args TEXT;
    sql TEXT;

BEGIN

    args := array_to_string(ARRAY(
        SELECT format('%I', c) || '::text'
        FROM unnest(columns) c
        WHERE c != 'geom'
    ), ' || ');

    IF 'geom' = ANY(columns) THEN
        args := 'ST_AsEWKB(ST_Normalize(geom)) || ' || args;
    END IF;

    sql := format(
        'SELECT %s AS id, md5(%s) AS row_hash FROM %s',
        format('%I', pk_column),
        args,
        table_name::regclass::text
    );

    RETURN QUERY EXECUTE sql;

END;
$$ LANGUAGE plpgsql;