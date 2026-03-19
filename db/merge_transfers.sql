--fact_transfer merge
INSERT INTO dbo.fact_transfer (
    player_id, date, transfer_type, from_team, to_team
)
SELECT 
    player_id,
    date,
    type,
    from_team,
    to_team
FROM staging.transfers;