SELECT CAST(
        SUBSTR(
            localId,
            instr(localId, '.') + 1
        ) AS INTEGER
    ) AS id,
    postCode AS postal_code,
    text AS name,
    CURRENT_TIMESTAMP AS updated_at
FROM PostalDescriptor;
