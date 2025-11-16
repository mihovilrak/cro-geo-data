CREATE OR REPLACE FUNCTION
staging.diff(
    schema_name TEXT,
    table_old TEXT,
    table_new TEXT
)
RETURNS TABLE(
    inserted INTEGER,
    deleted INTEGER,
    updated INTEGER
) AS $$
BEGIN

    DECLARE 
        columns TEXT[];
        inserted INTEGER;
        deleted INTEGER;
        updated INTEGER;

    SELECT array_agg(column_name) INTO columns
    FROM information_schema.columns
    WHERE table_schema = schema_name
    AND table_name = table_name
    AND column_name NOT IN ('id', 'created_at', 'updated_at');

    CREATE TEMPORARY TABLE hashes_a AS
    SELECT * FROM md5_hash(table_old, id, columns)
    ORDER BY id
    ON COMMIT DROP;

    CREATE TEMPORARY TABLE hashes_b AS
    SELECT * FROM md5_hash(table_new, id, columns)
    ORDER BY id
    ON COMMIT DROP;

    IF schema_name = 'dkp'
    OR table_old IN ('streets', 'postal_offices') THEN
        EXECUTE format(
            'UPDATE %I.%I n'
            || ' SET updated_at = o.updated_at'
            || ' FROM %I.%I o'
            || ' JOIN hashes_a a ON a.id = o.id'
            || ' JOIN hashes_b b ON b.id = n.id AND a.id = b.id'
            || ' WHERE n.id = o.id'
            || ' AND a.row_hash = b.row_hash'
            , schema_name, table_new, schema_name, table_old
        );

    END IF;

    SELECT COUNT(*) INTO updated
    FROM hashes_a a
    LEFT JOIN hashes_b b ON a.id = b.id
    WHERE a.row_hash IS DISTINCT FROM b.row_hash
    AND b.id IS NOT NULL;

    SELECT COUNT(*) INTO deleted
    FROM hashes_a a
    LEFT JOIN hashes_b b ON a.id = b.id
    WHERE b.id IS NULL;

    SELECT COUNT(*) INTO inserted
    FROM hashes_b b
    LEFT JOIN hashes_a a ON b.id = a.id
    WHERE a.id IS NULL;

    RETURN QUERY
    SELECT inserted, deleted, updated;

END;
$$ LANGUAGE plpgsql;