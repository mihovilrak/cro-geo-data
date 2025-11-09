CREATE OR REPLACE FUNCTION staging.addresses_streets()
RETURNS void
AS $$
BEGIN;

    CREATE UNLOGGED TABLE staging.u_streets_tmp AS
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
      FROM staging.u_addresses2 a
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
    UPDATE staging.u_addresses2 a
    SET street_id = upd.street_id
    FROM upd
    WHERE a.id = upd.a_id;

    WITH combined AS (
      SELECT street_id, geom
      FROM staging.u_addresses2
      WHERE street_id IS NOT NULL
        AND geom IS NOT NULL

      UNION ALL

      SELECT a.street_id, a.geom
      FROM rpj.addresses a
      WHERE a.street_id IS NOT NULL
        AND a.geom IS NOT NULL
        AND NOT EXISTS (
          SELECT 1
          FROM staging.u_addresses2 u
          WHERE u.id = a.id
        )
    ),
    b AS (
      SELECT
        street_id,
        MIN(ST_X(geom)) AS xmin,
        MIN(ST_Y(geom)) AS ymin,
        MAX(ST_X(geom)) AS xmax,
        MAX(ST_Y(geom)) AS ymax
      FROM combined
      GROUP BY street_id
    ),
    geomcalc AS (
      SELECT
        street_id,
        ST_Buffer(
          ST_MakeEnvelope(xmin, ymin, xmax, ymax, 3765),
          10
        ) AS geom
      FROM b
    ),
    upd AS (
      UPDATE staging.u_streets s
      SET geom = g.geom
      FROM geomcalc g
      WHERE s.id = g.street_id
      RETURNING s.id, g.geom
    ),
    UPDATE rpj.streets s
      SET geom = g.geom
      FROM geomcalc g
      WHERE s.id = g.street_id
      AND NOT EXISTS (
        SELECT 1
        FROM upd u
        WHERE u.id = s.id
      );

    CREATE INDEX IF NOT EXISTS idx_u_streets_geom 
    ON staging.u_streets (geom) USING GIST;
    CREATE INDEX IF NOT EXISTS idx_u_addresses2_street_id 
    ON staging.u_addresses2 (street_id);

    ANALYZE staging.u_streets;
    ANALYZE staging.u_addresses2;
END;
$$ LANGUAGE plpgsql;
