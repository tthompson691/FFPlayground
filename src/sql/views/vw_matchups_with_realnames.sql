CREATE VIEW vw_matchups_with_realnames AS
SELECT
    m.*,
    lmw.RealName WinnerName,
    lml.RealName LoserName,
    lmh.RealName HomeName,
    lma.RealName AwayName,
    MAX(lmw.RealName || lml.RealName, lml.RealName || lmw.RealName) MatchupID
FROM matchups m
JOIN leaguemembers lmw
    ON m.Year = lmw.Year
    AND m.Winner = lmw.TeamID
JOIN leaguemembers lml
    ON m.Year = lml.Year
    AND m.Loser = lml.TeamID
JOIN leaguemembers lma
    ON m.Year = lma.Year
    AND m.AwayTeamID = lma.TeamID
JOIN leaguemembers lmh
    ON m.Year = lmh.Year
    AND m.HomeTeamID = lmh.TeamID