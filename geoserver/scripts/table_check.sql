SELECT EXISTS (
    SELECT 1 
    FROM information_schema.tables 
    WHERE table_schema = 'gs' 
        AND table_name = 'v_counties'
);	