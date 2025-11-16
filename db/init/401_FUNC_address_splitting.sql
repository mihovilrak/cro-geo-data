CREATE OR REPLACE FUNCTION staging.address_splitting()
RETURNS VOID AS $$
BEGIN

    CREATE TEMPORARY TABLE staging.tmp_tokens AS
    SELECT id,
        idx,
        token
        FROM staging.u_addresses
    CROSS JOIN LATERAL regexp_split_to_table(
        regexp_replace(
            coalesce(alternate_address, ''), 
            '[,;]+',
            ' ',
            'g'
        ), 
        '\s+'
    ) WITH ORDINALITY AS t(token, idx);

    CREATE INDEX ON staging.tmp_tokens(id);
    CREATE INDEX ON staging.tmp_tokens(id, idx);

    CREATE TEMPORARY TABLE staging.tmp_zip AS
    SELECT id, min(idx) AS zip_idx
    FROM staging.tmp_tokens
    WHERE token ~ '^[0-9]{5}$'
    GROUP BY id;
    CREATE INDEX ON staging.tmp_zip(id);

    CREATE TEMPORARY TABLE staging.tmp_digits_before_zip AS
    SELECT t.id, t.idx, t.token
    FROM staging.tmp_tokens t
    JOIN staging.tmp_zip z ON z.id = t.id
    WHERE t.idx < z.zip_idx
    AND t.token ~ '^[0-9]'
    AND NOT (
           t.token ~ '^\(.*\)$' 
        OR t.token ~ '^[0-9]+-[0-9]+$' 
        OR t.token ~ '^\([0-9]+-[0-9]+\)$'
    );

    CREATE INDEX ON staging.tmp_digits_before_zip(id);
    CREATE INDEX ON staging.tmp_digits_before_zip(id, idx);

    CREATE TEMPORARY TABLE staging.tmp_digits_ranked AS
    SELECT id,
        idx,
        token,
        row_number() OVER (PARTITION BY id ORDER BY idx DESC) AS rn
    FROM staging.tmp_digits_before_zip;
    CREATE INDEX ON staging.tmp_digits_ranked(id, rn);

    CREATE TEMPORARY TABLE staging.tmp_house_idx AS
    SELECT id,
        COALESCE(
            (
                SELECT idx 
                FROM staging.tmp_digits_ranked d2 
                WHERE d2.id = d.id 
                AND d2.rn = 2 
                LIMIT 1
            ),
            (
                SELECT idx
                FROM staging.tmp_digits_ranked d1 
                WHERE d1.id = d.id 
                AND d1.rn = 1 
                LIMIT 1
            )
        )::INT AS house_idx
    FROM (
        SELECT DISTINCT id 
        FROM staging.tmp_tokens
    ) d;
    CREATE INDEX ON staging.tmp_house_idx(id);

    CREATE TEMPORARY TABLE staging.tmp_parsed AS
    SELECT p.id,
    CASE 
        WHEN h.house_idx IS NULL 
        THEN NULL
        WHEN h.house_idx > 1
        THEN (
            SELECT string_agg(token, ' ' ORDER BY idx)
            FROM staging.tmp_tokens tt 
            WHERE tt.id = p.id 
            AND tt.idx < h.house_idx
        )
        ELSE NULL
    END AS street_name,
    (
        SELECT token 
        FROM staging.tmp_tokens tt 
        WHERE tt.id = p.id 
        AND tt.idx = h.house_idx
        LIMIT 1
    ) AS house_number,
    (
        SELECT string_agg(token, ' ' ORDER BY idx)
        FROM staging.tmp_tokens tt
        LEFT JOIN staging.tmp_zip z ON z.id = tt.id
        WHERE tt.id = p.id
        AND h.house_idx IS NOT NULL
        AND tt.idx > h.house_idx
        AND (z.zip_idx IS NULL OR tt.idx < z.zip_idx)
    ) AS settlement_name,
    (
        SELECT token 
        FROM staging.tmp_tokens tt 
        JOIN staging.tmp_zip z ON z.id = tt.id
        WHERE tt.id = p.id 
        AND tt.idx = z.zip_idx 
        LIMIT 1
    ) AS zip
    FROM (
        SELECT DISTINCT id 
        FROM staging.tmp_tokens
    ) p
    LEFT JOIN staging.tmp_house_idx h ON h.id = p.id;
    CREATE INDEX ON staging.tmp_parsed(id);

    UPDATE staging.u_addresses
    SET street_name = tp.street_name,
        house_number = tp.house_number,
        settlement_name = trim(
            both ' ,.' 
            FROM regexp_replace(
                coalesce(tp.settlement_name,''), 
                '\s*\(.*\)\s*$',
                '',
                'g'
            )
        ),
        zip = tp.zip::INT
    FROM staging.tmp_parsed tp
    WHERE staging.u_addresses.id = tp.id;

    DROP TABLE IF EXISTS staging.tmp_parsed;
    DROP TABLE IF EXISTS staging.tmp_house_idx;
    DROP TABLE IF EXISTS staging.tmp_digits_ranked;
    DROP TABLE IF EXISTS staging.tmp_digits_before_zip;
    DROP TABLE IF EXISTS staging.tmp_zip;
    DROP TABLE IF EXISTS staging.tmp_tokens;

END;
$$ LANGUAGE plpgsql;
