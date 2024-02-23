CREATE VIEW vw_matchups_with_realnames AS
SELECT
    m.*,
    lma.RealName AwayName,
    lmh.RealName HomeName
FROM matchups m
JOIN leaguemembers lma
    ON m.Year = lma.Year
    AND m.AwayTeamID = lma.TeamID
JOIN leaguemembers lmh
    ON m.Year = lmh.Year
    AND m.HomeTeamID = lmh.TeamID;

