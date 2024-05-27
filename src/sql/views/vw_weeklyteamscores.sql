CREATE VIEW vw_weeklyteamscores AS
SELECT
    ps.Year,
    ps.Week,
    lm.RealName,
    lm.TeamID,
    p.Position,
    CASE
        WHEN ps.LineupSlotID IN (0, 2, 4, 6, 16, 17, 23) THEN 1
        ELSE 0
    END IsStarting,
    CASE
        WHEN ps.LineupSlotID = 23 THEN 1
        ELSE 0
    END IsFlex,
--     ps.LineupSlotID,
    p.FullName,
    ps.ProjectedScore,
    ps.ActualScore
FROM playerscores ps
LEFT JOIN players p
    ON ps.PlayerID = p.PlayerID
    AND ps.Year = p.Year
JOIN leaguemembers lm
    ON lm.TeamID = ps.OnTeamID
    AND lm.Year = ps.Year;

