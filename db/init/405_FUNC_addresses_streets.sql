CREATE OR REPLACE FUNCTION staging.addresses_streets()
RETURNS void
AS $$
BEGIN

    CREATE TEMPORARY TABLE staging.u_streets_tmp AS
      SELECT
        MIN(id) AS street_id,
        settlement_id,
        lower(regexp_replace(trim(name), '\s+', ' ', 'g')) AS norm_name
    FROM staging.u_streets
    GROUP BY settlement_id, lower(
      regexp_replace(
        trim(name),
        '\s+',
        ' ',
        'g'
      )
    )
    ON COMMIT DROP;

    CREATE INDEX ON staging.u_streets_tmp (settlement_id, norm_name);

    WITH upd AS (
      SELECT a.id AS a_id, 
        t.street_id
      FROM staging.u_addresses a
      JOIN staging.u_streets_tmp t
        ON a.settlement_id = t.settlement_id
        AND lower(
          regexp_replace(
            trim(a.street_name),
            '\s+',
            ' ',
            'g'
          )
        ) = t.norm_name
      WHERE a.street_id IS DISTINCT FROM t.street_id
    )
    UPDATE staging.u_addresses a
    SET street_id = upd.street_id
    FROM upd
    WHERE a.id = upd.a_id;

    ANALYZE staging.u_addresses;
END;
$$ LANGUAGE plpgsql;
