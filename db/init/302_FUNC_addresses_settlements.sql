CREATE OR REPLACE FUNCTION staging.addresses_settlements()
RETURNS VOID AS $$
BEGIN;

    CREATE INDEX IF NOT EXISTS idx_u_addresses2_geom 
    ON staging.u_addresses2(geom) USING GIST;
    CREATE INDEX IF NOT EXISTS idx_u_settlements_geom 
    ON staging.u_settlements(geom) USING GIST;

    WITH cte AS (
    SELECT a.id,
           s.id AS settlement_id
    FROM staging.u_addresses2 a
    LEFT JOIN staging.u_settlements s
      ON s.geom && a.geom
     AND ST_Contains(s.geom, a.geom);
    )
    UPDATE staging.u_addresses2 a
    SET settlement_id = cte.settlement_id
    FROM cte
    WHERE a.id = cte.id;
END;
$$ LANGUAGE plpgsql;
