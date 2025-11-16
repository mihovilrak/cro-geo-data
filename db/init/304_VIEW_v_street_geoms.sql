CREATE OR REPLACE VIEW gs.v_street_geoms AS
    SELECT street_id,
        ST_Buffer(
            ST_MakeEnvelope(xmin, ymin, xmax, ymax, 3765),
            10
        ) AS geom
    FROM gs.v_street_extents;
