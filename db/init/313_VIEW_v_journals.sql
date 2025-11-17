CREATE OR REPLACE VIEW journal.v_journals AS
SELECT 'Country' AS table_name, * FROM journal.j_country
UNION ALL
SELECT 'Counties' AS table_name, * FROM journal.j_counties
UNION ALL
SELECT 'Municipalities' AS table_name, * FROM journal.j_municipalities
UNION ALL
SELECT 'Settlements' AS table_name, * FROM journal.j_settlements
UNION ALL
SELECT 'Postal Offices' AS table_name, * FROM journal.j_postal_offices
UNION ALL
SELECT 'Streets' AS table_name, * FROM journal.j_streets
UNION ALL
SELECT 'Addresses' AS table_name, * FROM journal.j_addresses
UNION ALL
SELECT 'Cadastral Municipalities' AS table_name, * FROM journal.j_cadastral_municipalities
UNION ALL
SELECT 'Cadastral Parcels' AS table_name, * FROM journal.j_cadastral_parcels
UNION ALL
SELECT 'Buildings' AS table_name, * FROM journal.j_buildings
UNION ALL
SELECT 'Usages' AS table_name, * FROM journal.j_usages;
ORDER BY created_at DESC;
