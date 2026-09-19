-- rpc function to REFRESH MATERIALIZED VIEW screener_view;

CREATE OR REPLACE FUNCTION refresh_screener_view()
RETURNS VOID AS $$
BEGIN
    -- Refresh the screener_view materialized view
    REFRESH MATERIALIZED VIEW screener_view;
END;
$$ LANGUAGE plpgsql;

