-- Competition
MERGE dbo.dim_competition AS tgt
USING (SELECT comp_id, comp_name, comp_type, area_name, code FROM staging.leagues) AS src
ON (tgt.comp_id = src.comp_id)
WHEN MATCHED THEN
  UPDATE SET comp_name = src.comp_name, comp_type = src.comp_type, area_name = src.area_name,
             code = src.code, last_updated = SYSUTCDATETIME()
WHEN NOT MATCHED THEN
  INSERT (comp_id, comp_name, comp_type, area_name, code, last_updated)
  VALUES (src.comp_id, src.comp_name, src.comp_type, src.area_name, src.code, SYSUTCDATETIME());

-- Team
MERGE dbo.dim_team AS tgt
USING (SELECT team_id, team_name, tla, country, founded FROM staging.teams) AS src
ON (tgt.team_id = src.team_id)
WHEN MATCHED THEN
  UPDATE SET team_name = src.team_name, tla = src.tla, country = src.country,
             founded = src.founded, last_updated = SYSUTCDATETIME()
WHEN NOT MATCHED THEN
  INSERT (team_id, team_name, tla, country, founded, last_updated)
  VALUES (src.team_id, src.team_name, src.tla, src.country, src.founded, SYSUTCDATETIME());

-- Match (fixtures)
MERGE dbo.fact_match AS tgt
USING (
  SELECT match_id, comp_id, season, utc_date, status, round,
         home_team_id, away_team_id, ft_home_goals, ft_away_goals, winner
  FROM staging.fixtures
) AS src
ON (tgt.match_id = src.match_id)
WHEN MATCHED THEN
  UPDATE SET comp_id = src.comp_id, season = src.season, utc_date = src.utc_date,
             status = src.status, round = src.round,
             home_team_id = src.home_team_id, away_team_id = src.away_team_id,
             ft_home_goals = src.ft_home_goals, ft_away_goals = src.ft_away_goals,
             winner = src.winner, last_updated = SYSUTCDATETIME()
WHEN NOT MATCHED THEN
  INSERT (match_id, comp_id, season, utc_date, status, round, home_team_id, away_team_id,
          ft_home_goals, ft_away_goals, winner, last_updated)
  VALUES (src.match_id, src.comp_id, src.season, src.utc_date, src.status, src.round,
          src.home_team_id, src.away_team_id, src.ft_home_goals, src.ft_away_goals,
          src.winner, SYSUTCDATETIME());

-- Standings
MERGE dbo.fact_standing AS tgt
USING (
  SELECT comp_id, season, team_id, position, points, played, won, draw, lost, goals_for, goals_against
  FROM staging.standings
) AS src
ON (tgt.comp_id = src.comp_id AND tgt.season = src.season AND tgt.team_id = src.team_id)
WHEN MATCHED THEN
  UPDATE SET position = src.position, points = src.points, played = src.played,
             won = src.won, draw = src.draw, lost = src.lost,
             goals_for = src.goals_for, goals_against = src.goals_against,
             last_updated = SYSUTCDATETIME()
WHEN NOT MATCHED THEN
  INSERT (comp_id, season, team_id, position, points, played, won, draw, lost, goals_for, goals_against, last_updated)
  VALUES (src.comp_id, src.season, src.team_id, src.position, src.points, src.played, src.won,
          src.draw, src.lost, src.goals_for, src.goals_against, SYSUTCDATETIME());