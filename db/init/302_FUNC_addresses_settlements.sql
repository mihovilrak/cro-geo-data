CREATE OR REPLACE FUNCTION staging.addresses_settlements()
RETURNS VOID AS $$
BEGIN;

    CREATE INDEX IF NOT EXISTS idx_u_addresses_geom 
    ON staging.u_addresses(geom) USING GIST;

    CREATE INDEX IF NOT EXISTS idx_u_settlements_geom 
    ON staging.u_settlements(geom) USING GIST;

    WITH cte AS (
    SELECT a.id,
           s.id AS settlement_id
    FROM staging.u_addresses a
    LEFT JOIN staging.u_settlements s
      ON s.geom && a.geom
     AND ST_Contains(s.geom, a.geom);
    )
    UPDATE staging.u_addresses a
    SET settlement_id = cte.settlement_id
    FROM cte
    WHERE a.id = cte.id;

END;
$$ LANGUAGE plpgsql;
