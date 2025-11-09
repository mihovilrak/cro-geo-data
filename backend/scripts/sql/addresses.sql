SELECT CAST(
        SUBSTR(
            localId,
            instr(localId, '.') + 1
        ) AS INTEGER
    ) AS id,
    AlternateAddress AS alternate_address,
    NULL AS street_id,
    NULL AS street_name,
    NULL AS house_number,
    NULL AS settlement_id,
    NULL AS settlement_name,
    NULL AS zip,
    beginLifespanVersion AS updated_at,
    geom
FROM Addresses;