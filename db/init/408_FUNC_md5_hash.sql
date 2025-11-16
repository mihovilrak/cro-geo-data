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
        SELECT quote_literal(c) || ', ' || format('%I', c)
        FROM unnest(columns) c
    ), ', ');

    sql := format(
        'SELECT %s AS id, md5((jsonb_build_object(%s)::text)) AS row_hash FROM %s',
        format('%I', pk_column),
        args,
        table_name::regclass::TEXT
    );

    RETURN QUERY EXECUTE sql;

END;
$$ LANGUAGE plpgsql;