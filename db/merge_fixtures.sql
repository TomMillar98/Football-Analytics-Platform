-- fact_match merge
MERGE dbo.fact_match AS tgt
USING (
    SELECT DISTINCT
        fixture_id,
        comp_id,
        season,
        date_utc,
        status,
        round,
        home_team_id,
        away_team_id,
        score_home,
        score_away
    FROM staging.fixtures
) AS src
ON tgt.fixture_id = src.fixture_id

WHEN MATCHED THEN
    UPDATE SET
        comp_id = src.comp_id,
        season = src.season,
        date_utc = src.date_utc,
        status = src.status,
        round = src.round,
        home_team_id = src.home_team_id,
        away_team_id = src.away_team_id,
        score_home = src.score_home,
        score_away = src.score_away,
        last_updated = SYSUTCDATETIME()

WHEN NOT MATCHED THEN
    INSERT (fixture_id, comp_id, season, date_utc, status, round, home_team_id, away_team_id, score_home, score_away, last_updated)
    VALUES (src.fixture_id, src.comp_id, src.season, src.date_utc, src.status, src.round, src.home_team_id, src.away_team_id, src.score_home, src.score_away, SYSUTCDATETIME());