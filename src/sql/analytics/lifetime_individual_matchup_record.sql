SELECT
MAX(HomeName, AwayName) Team1,
    (SELECT COUNT(*)
    FROM vw_matchups_with_realnames b
    WHERE WinnerName = MAX(HomeName, AwayName)
    AND b.MatchupID = a.MatchupID) Team1Wins,
    (SELECT COUNT(*)
    FROM vw_matchups_with_realnames b
    WHERE WinnerName = MIN(HomeName, AwayName)
    AND b.MatchupID = a.MatchupID) Team2Wins,
MIN(HomeName, AwayName) Team2
FROM vw_matchups_with_realnames a
GROUP BY a.MatchupID