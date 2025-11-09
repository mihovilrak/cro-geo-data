SELECT CAST(
        SUBSTR(
            localId,
            instr(localId, '.') + 1
        ) AS INTEGER
    ) AS id,
    CAST(
        nationalCode AS INTEGER
    ) AS national_code,
    NULL AS $PARENT_id,
    text AS name,
    beginLifespanVersion AS updated_at,
    geometry AS geom
FROM AdministrativeUnit
WHERE LocalisedCharacterString = '$AU_TYPE';