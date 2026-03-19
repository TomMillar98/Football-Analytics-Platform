MERGE dbo.dim_team AS tgt
USING (
    SELECT DISTINCT
        team_id,
        name,
        short_name,
        country,
        founded,
        logo_url
    FROM staging.teams
) AS src
ON tgt.team_id = src.team_id

WHEN MATCHED THEN
    UPDATE SET
        name = src.name,
        short_name = src.short_name,
        country = src.country,
        founded = src.founded,
        logo_url = src.logo_url,
        last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (team_id, name, short_name, country, founded, logo_url, last_updated)
    VALUES (src.team_id, src.name, src.short_name, src.country, src.founded, src.logo_url, SYSUTCDATETIME());