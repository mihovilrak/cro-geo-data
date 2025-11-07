CREATE OR REPLACE FUNCTION split_address(address_table_name TEXT)
RETURNS VOID AS $$
BEGIN

    -- 0. adjust these names
    -- main table: my_schema.my_points
    -- full-address column: fulladdr
    -- primary key: id

    -- 1) create token table (persisted temp table)
    CREATE TEMP TABLE tmp_tokens AS
    SELECT id, idx, token
    FROM (
    SELECT id,
            regexp_split_to_table(regexp_replace(coalesce(fulladdr,''), '[,;]+', ' ', 'g'), '\s+') WITH ORDINALITY
            AS t(token, idx)
    FROM address_table_name
    ) tokens;

    -- Indexes to speed joins/aggregates
    CREATE INDEX ON tmp_tokens(id);
    CREATE INDEX ON tmp_tokens(id, idx);

    -- 2) zip positions (first exact 5-digit token)
    CREATE TEMP TABLE tmp_zip AS
    SELECT id, min(idx) AS zip_idx
    FROM tmp_tokens
    WHERE token ~ '^[0-9]{5}$'
    GROUP BY id;
    CREATE INDEX ON tmp_zip(id);

    -- 3) candidate digit-tokens BEFORE zip: mark tokens that start with digit and are NOT simple ranges/paren ranges.
    CREATE TEMP TABLE tmp_digits_before_zip AS
    SELECT t.id, t.idx, t.token
    FROM tmp_tokens t
    JOIN tmp_zip z ON z.id = t.id
    WHERE t.idx < z.zip_idx
    AND t.token ~ '^[0-9]'  -- starts with digit
    AND NOT (t.token ~ '^\(.*\)$' OR t.token ~ '^[0-9]+-[0-9]+$' OR t.token ~ '^\([0-9]+-[0-9]+\)$');

    CREATE INDEX ON tmp_digits_before_zip(id);
    CREATE INDEX ON tmp_digits_before_zip(id, idx);

    -- 4) rank candidates per id from right-to-left and keep rn = 1 (nearest) and rn = 2 (second nearest)
    CREATE TEMP TABLE tmp_digits_ranked AS
    SELECT id, idx, token,
        row_number() OVER (PARTITION BY id ORDER BY idx DESC) AS rn
    FROM tmp_digits_before_zip;
    CREATE INDEX ON tmp_digits_ranked(id, rn);

    -- 5) pick the 2nd nearest where present, else nearest (rn=2 preferred, else rn=1 fallback)
    -- we compute preferred_house_idx per id
    CREATE TEMP TABLE tmp_house_idx AS
    SELECT id,
        COALESCE(
            (SELECT idx FROM tmp_digits_ranked d2 WHERE d2.id = d.id AND d2.rn = 2 LIMIT 1),
            (SELECT idx FROM tmp_digits_ranked d1 WHERE d1.id = d.id AND d1.rn = 1 LIMIT 1)
        ) AS house_idx
    FROM (SELECT DISTINCT id FROM tmp_tokens) d;
    CREATE INDEX ON tmp_house_idx(id);

    -- 6) assemble final parsed table (string_agg for street and settlement)
    CREATE TEMP TABLE tmp_parsed AS
    SELECT p.id,
    -- street: tokens before house_idx
    CASE WHEN h.house_idx IS NULL THEN NULL
        WHEN h.house_idx > 1 THEN
            (SELECT string_agg(token,' ' ORDER BY idx)
            FROM tmp_tokens tt WHERE tt.id = p.id AND tt.idx < h.house_idx)
        ELSE NULL END AS street,
    -- house_number: token at house_idx
    (SELECT token FROM tmp_tokens tt WHERE tt.id = p.id AND tt.idx = h.house_idx LIMIT 1) AS house_number,
    -- settlement: tokens strictly between house_idx and zip_idx (if zip exists)
    (SELECT string_agg(token,' ' ORDER BY idx)
    FROM tmp_tokens tt
    LEFT JOIN tmp_zip z ON z.id = tt.id
    WHERE tt.id = p.id
        AND h.house_idx IS NOT NULL
        AND tt.idx > h.house_idx
        AND (z.zip_idx IS NULL OR tt.idx < z.zip_idx)
    ) AS settlement,
    -- zip token
    (SELECT token FROM tmp_tokens tt JOIN tmp_zip z ON z.id = tt.id
    WHERE tt.id = p.id AND tt.idx = z.zip_idx LIMIT 1) AS zip
    FROM (SELECT DISTINCT id FROM tmp_tokens) p
    LEFT JOIN tmp_house_idx h ON h.id = p.id;

    -- 7) copy results back to main table (single UPDATE join)
    UPDATE address_table_name
    SET street = tp.street,
        house_number = tp.house_number,
        settlement = trim(both ' ,.' FROM regexp_replace(coalesce(tp.settlement,''), '\s*\(.*\)\s*$', '', 'g')),
        zip = tp.zip
    FROM tmp_parsed tp
    WHERE address_table_name.id = tp.id;

    -- 8) drop temporary tables
    DROP TABLE tmp_tokens;
    DROP TABLE tmp_zip;
    DROP TABLE tmp_digits_before_zip;
    DROP TABLE tmp_digits_ranked;
    DROP TABLE tmp_house_idx;
    DROP TABLE tmp_parsed;

END;
$$ LANGUAGE plpgsql;
