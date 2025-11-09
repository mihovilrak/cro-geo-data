CREATE OR REPLACE FUNCTION staging.address_splitting()
RETURNS VOID AS $$
BEGIN

    CREATE UNLOGGED TABLE staging.tmp_tokens AS
    SELECT id, idx, token
    FROM (
    SELECT id,
            regexp_split_to_table(
                regexp_replace(
                    coalesce(alternate_address, ''), 
                    '[,;]+',
                    ' ',
                    'g'
                ), 
                '\s+'
            ) WITH ORDINALITY
            AS t(token, idx)
    FROM staging.u_addresses
    ) tokens
    ON COMMIT DROP;

    CREATE INDEX ON staging.tmp_tokens(id);
    CREATE INDEX ON staging.tmp_tokens(id, idx);

    CREATE UNLOGGED TABLE staging.tmp_zip AS
    SELECT id, min(idx) AS zip_idx
    FROM staging.tmp_tokens
    WHERE token ~ '^[0-9]{5}$'
    GROUP BY id
    ON COMMIT DROP;
    CREATE INDEX ON staging.tmp_zip(id);

    CREATE UNLOGGED TABLE tmp_digits_before_zip AS
    SELECT t.id, t.idx, t.token
    FROM staging.tmp_tokens t
    JOIN tmp_zip z ON z.id = t.id
    WHERE t.idx < z.zip_idx
    AND t.token ~ '^[0-9]'
    AND NOT (
           t.token ~ '^\(.*\)$' 
        OR t.token ~ '^[0-9]+-[0-9]+$' 
        OR t.token ~ '^\([0-9]+-[0-9]+\)$'
    )
    ON COMMIT DROP;

    CREATE INDEX ON staging.tmp_digits_before_zip(id);
    CREATE INDEX ON staging.tmp_digits_before_zip(id, idx);

    CREATE UNLOGGED TABLE staging.tmp_digits_ranked AS
    SELECT  id,
            idx,
            token,
        row_number() OVER (PARTITION BY id ORDER BY idx DESC) AS rn
    FROM staging.tmp_digits_before_zip
    ON COMMIT DROP;
    CREATE INDEX ON staging.tmp_digits_ranked(id, rn);

    CREATE UNLOGGED TABLE staging.tmp_house_idx AS
    SELECT id,
        COALESCE(
            (SELECT idx FROM staging.tmp_digits_ranked d2 
            WHERE d2.id = d.id AND d2.rn = 2 LIMIT 1),
            (SELECT idx FROM staging.tmp_digits_ranked d1 
            WHERE d1.id = d.id AND d1.rn = 1 LIMIT 1)
        ) AS house_idx
    FROM (SELECT DISTINCT id FROM staging.tmp_tokens) d
    ON COMMIT DROP;
    CREATE INDEX ON staging.tmp_house_idx(id);

    CREATE UNLOGGED TABLE staging.tmp_parsed AS
    SELECT p.id,
    CASE WHEN h.house_idx IS NULL THEN NULL
        WHEN h.house_idx > 1 THEN
            (SELECT string_agg(token,' ' ORDER BY idx)
            FROM staging.tmp_tokens tt 
            WHERE tt.id = p.id 
            AND tt.idx < h.house_idx)
        ELSE NULL END AS street,
    (SELECT token 
    FROM staging.tmp_tokens tt 
    WHERE tt.id = p.id 
    AND tt.idx = h.house_idx
    LIMIT 1) AS house_number,
    (SELECT string_agg(token, ' ' ORDER BY idx)
    FROM staging.tmp_tokens tt
    LEFT JOIN staging.tmp_zip z ON z.id = tt.id
    WHERE tt.id = p.id
        AND h.house_idx IS NOT NULL
        AND tt.idx > h.house_idx
        AND (z.zip_idx IS NULL OR tt.idx < z.zip_idx)
    ) AS settlement,
    (SELECT token 
    FROM staging.tmp_tokens tt 
    JOIN staging.tmp_zip z ON z.id = tt.id
    WHERE tt.id = p.id 
    AND tt.idx = z.zip_idx 
    LIMIT 1) AS zip
    FROM (SELECT DISTINCT id FROM staging.tmp_tokens) p
    LEFT JOIN staging.tmp_house_idx h ON h.id = p.id
    ON COMMIT DROP;
    CREATE INDEX ON staging.tmp_parsed(id);

    CREATE UNLOGGED TABLE staging.u_addresses2 AS
    SELECT  id,
            0 AS street_id,
            '' AS street,
            '' AS house_number,
            0 AS settlement_id,
            '' AS settlement,
            0 AS zip,
            updated_at,
            geom
    FROM staging.u_addresses;

    TRUNCATE TABLE staging.u_addresses;

    UPDATE staging.u_addresses2
    SET street = tp.street,
        house_number = tp.house_number,
        settlement = trim(
            both ' ,.' 
            FROM regexp_replace(
                coalesce(tp.settlement,''), 
                '\s*\(.*\)\s*$',
                '',
                'g'
            )
        ),
        zip = tp.zip
    FROM staging.tmp_parsed tp
    WHERE staging.u_addresses2.id = tp.id;

END;
$$ LANGUAGE plpgsql;
