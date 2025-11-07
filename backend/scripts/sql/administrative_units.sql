SELECT  CAST(SUBSTR(localId, instr(localId, '.') + 1) AS INTEGER) as id,
        CAST(nationalCode AS INTEGER) as national_code,
        text as name,
        beginLifespanVersion as updated_at,
        geometry as geom
FROM AdministrativeUnit
WHERE LocalisedCharacterString = '$AU_TYPE';