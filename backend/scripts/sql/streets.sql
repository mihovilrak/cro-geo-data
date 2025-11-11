SELECT CAST(
        SUBSTR(
            localId,
            instr(localId, '.') + 1
        ) AS INTEGER
    ) AS id,
    CAST(alternativeIdentifier AS INTEGER) AS unique_identifier,
    text AS name,
    CAST(
        SUBSTR(
            alternativeIdentifier,
            1,
            6
        ) AS INTEGER
    ) AS settlement_code,
    NULL AS postal_code,
    CURRENT_TIMESTAMP AS updated_at
FROM Street;