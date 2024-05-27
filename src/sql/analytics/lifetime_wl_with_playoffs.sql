SELECT
    DISTINCT
    wins.Winner,
    lm.RealName,
    wins.TotalWins,
    loser.TotalLosses
FROM (SELECT
    DISTINCT Winner,
    COUNT(*) TotalWins
FROM matchups
GROUP BY Winner) wins
JOIN (SELECT
    DISTINCT Loser,
    COUNT(*) TotalLosses
FROM matchups
GROUP BY Loser) loser
    ON wins.Winner = loser.Loser
JOIN leaguemembers lm
    ON wins.Winner = lm.TeamID