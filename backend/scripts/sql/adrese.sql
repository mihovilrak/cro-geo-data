SELECT  CAST(SUBSTR(localId, instr(localId, '.') + 1) AS INTEGER) as id,
        AlternateAddress as alternativna_adresa,
        geom
FROM Addresses;