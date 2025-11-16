CREATE OR REPLACE FUNCTION staging.update_staging()
RETURNS VOID AS $$
BEGIN

    SELECT staging.address_splitting();
    SELECT staging.addresses_settlements();
    SELECT staging.settlements_municipalities();
    SELECT staging.municipalities_counties();
    SELECT staging.addresses_streets();
    SELECT staging.set_postal_codes();

END;
$$ LANGUAGE plpgsql;
