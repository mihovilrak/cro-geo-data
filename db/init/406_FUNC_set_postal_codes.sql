CREATE OR REPLACE FUNCTION staging.set_postal_codes()
RETURNS VOID AS $$
BEGIN;

    WITH cte AS (
        SELECT street_id, postal_code
        FROM staging.u_addresses
        WHERE postal_code IS NOT NULL
        AND street_id IS NOT NULL
        GROUP BY street_id, postal_code

        UNION

        SELECT id AS street_id, postal_code
        FROM rpj.streets
        WHERE postal_code IS NOT NULL

    )
    UPDATE staging.u_streets
    SET postal_code = cte.postal_code
    FROM cte
    WHERE staging.u_streets.id = cte.street_id;

END;
$$ LANGUAGE plpgsql;