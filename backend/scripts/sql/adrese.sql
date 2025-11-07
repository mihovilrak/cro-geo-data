SELECT  CAST(SUBSTR(localId, instr(localId, '.') + 1) AS INTEGER) as id,
        AlternateAddress as alternate_address,
        geom
FROM Addresses;