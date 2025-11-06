SELECT  CAST(SUBSTR(localId, instr(localId, '.') + 1) AS INTEGER) as id,
        CAST(nationalCode AS INTEGER) as maticni_broj,
        text as naziv,
        beginLifespanVersion as datum_promjene,
        geometry as geom
FROM AdministrativeUnit
WHERE LocalisedCharacterString = '$AU_TYPE';