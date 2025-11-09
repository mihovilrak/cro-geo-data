SELECT CAST(
        SUBSTR(
            localId,
            instr(localId, '.') + 1
        ) AS INTEGER
    ) AS id,
    text AS name,
    CAST(
        SUBSTR(
            alternativeIdentifier,
            1,
            6
        ) AS INTEGER
    ) AS settlement_code,
    CAST(alternativeIdentifier AS INTEGER) AS alternate_code,
    CURRENT_TIMESTAMP AS updated_at,
    NULL AS geom
FROM Street;