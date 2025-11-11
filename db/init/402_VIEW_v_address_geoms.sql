CREATE OR REPLACE VIEW gs.v_address_geoms AS
    SELECT street_id, geom
    FROM rpj.addresses
    WHERE geom IS NOT NULL AND street_id IS NOT NULL;