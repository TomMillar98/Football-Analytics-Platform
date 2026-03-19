-- fact_player_match merge
MERGE dbo.fact_player_match AS tgt
USING (
    SELECT *
    FROM staging.player_match_stats
) AS src
ON tgt.fixture_id = src.fixture_id
AND tgt.player_id = src.player_id

WHEN MATCHED THEN
    UPDATE SET
        team_id = src.team_id,
        minutes = src.minutes,
        rating = src.rating,
        shots_total = src.shots_total,
        shots_on = src.shots_on,
        passes_total = src.passes_total,
        passes_accuracy = src.passes_accuracy,
        duels_total = src.duels_total,
        duels_won = src.duels_won,
        dribbles_attempts = src.dribbles_attempts,
        dribbles_success = src.dribbles_success,
        tackles = src.tackles,
        interceptions = src.interceptions,
        fouls_committed = src.fouls_committed,
        fouls_drawn = src.fouls_drawn,
        saves = src.saves

WHEN NOT MATCHED THEN
    INSERT (fixture_id, player_id, team_id, minutes, rating,
            shots_total, shots_on, passes_total, passes_accuracy,
            duels_total, duels_won, dribbles_attempts, dribbles_success,
            tackles, interceptions, fouls_committed, fouls_drawn, saves)
    VALUES (
        src.fixture_id, src.player_id, src.team_id, src.minutes, src.rating,
        src.shots_total, src.shots_on, src.passes_total, src.passes_accuracy,
        src.duels_total, src.duels_won, src.dribbles_attempts, src.dribbles_success,
        src.tackles, src.interceptions, src.fouls_committed, src.fouls_drawn, src.saves
    );