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

DECLARE 
    columns TEXT[];
    inserted INTEGER;
    deleted INTEGER;
    updated INTEGER;

BEGIN

    SELECT array_agg(column_name) INTO columns
    FROM information_schema.columns
    WHERE table_schema = schema_name
    AND table_name = table_old
    AND column_name NOT IN ('id', 'created_at', 'updated_at');

    CREATE UNLOGGED TABLE staging.hashes_a AS
    SELECT * FROM staging.md5_hash(schema_name || '.' || table_old, 'id', columns);

    CREATE UNLOGGED TABLE staging.hashes_b AS
    SELECT * FROM staging.md5_hash(schema_name || '.' || table_new, 'id', columns);

    CREATE INDEX idx_hashes_a_id
    ON staging.hashes_a 
    USING HASH (id);

    CREATE INDEX idx_hashes_b_id
    ON staging.hashes_b 
    USING HASH (id);

    CREATE INDEX idx_hashes_a_hash
    ON staging.hashes_a 
    USING HASH (row_hash);

    CREATE INDEX idx_hashes_b_hash
    ON staging.hashes_b 
    USING HASH (row_hash);

    IF schema_name = 'dkp'
    OR table_old IN ('streets', 'postal_offices') THEN
        EXECUTE format(
            'UPDATE %I.%I n'
            || ' SET updated_at = o.updated_at'
            || ' FROM %I.%I o'
            || ' INNER JOIN staging.hashes_a a ON a.id = o.id'
            || ' INNER JOIN staging.hashes_b b ON b.id = n.id AND a.id = b.id'
            || ' WHERE a.row_hash = b.row_hash'
            , schema_name, table_new, schema_name, table_old
        );
    END IF;

    SELECT 
        COUNT(*) FILTER (WHERE a.id IS NULL) AS inserted_cnt,
        COUNT(*) FILTER (WHERE b.id IS NULL) AS deleted_cnt,
        COUNT(*) FILTER (WHERE a.id IS NOT NULL AND b.id IS NOT NULL 
                         AND a.row_hash IS DISTINCT FROM b.row_hash) AS updated_cnt
    INTO inserted, deleted, updated
    FROM staging.hashes_a a
    FULL OUTER JOIN staging.hashes_b b USING (id);

    DROP TABLE staging.hashes_b;
    DROP TABLE staging.hashes_a;

    RETURN QUERY
    SELECT inserted, deleted, updated;

END;
$$ LANGUAGE plpgsql;