CREATE OR REPLACE VIEW gs.v_addresses AS
    SELECT a.id,
        a.street_id,
        str.name AS street_name,
        a.house_number,
        str.settlement_id,
        stl.name AS settlement_name,
        str.postal_code AS zip,
        pos.name AS postal_office_name,
        cnt.name AS county_name,
        concat(
            str.name,
            ' ',
            a.house_number,
            ', ',
            str.postal_code,
            ' ',
            pos.name
        ) AS address,
        a.geom
    FROM rpj.addresses a
    LEFT JOIN rpj.streets str ON a.street_id = str.id
    LEFT JOIN rpj.settlements stl ON str.settlement_code = stl.national_code
    LEFT JOIN rpj.postal_offices pos ON str.postal_code = pos.postal_code
    LEFT JOIN rpj.counties cnt ON stl.county_code = cnt.national_code;
