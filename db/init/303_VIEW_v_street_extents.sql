CREATE OR REPLACE VIEW gs.v_street_extents AS
    SELECT street_id,
        MIN(ST_X(geom)) AS xmin,
        MIN(ST_Y(geom)) AS ymin,
        MAX(ST_X(geom)) AS xmax,
        MAX(ST_Y(geom)) AS ymax
    FROM gs.address_geoms
    GROUP BY street_id;