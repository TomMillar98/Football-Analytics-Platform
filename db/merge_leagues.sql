MERGE dbo.dim_competition AS tgt
USING (
    SELECT DISTINCT
        comp_id,
        comp_name,
        type,
        area,
        logo_url
    FROM staging.leagues
) AS src
ON tgt.comp_id = src.comp_id

WHEN MATCHED THEN
    UPDATE SET
        name = src.comp_name,
        type = src.type,
        area = src.area,
        logo_url = src.logo_url,
        last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (comp_id, name, type, area, logo_url, last_updated)
    VALUES (src.comp_id, src.comp_name, src.type, src.area, src.logo_url, SYSUTCDATETIME());