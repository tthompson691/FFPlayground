SELECT
    RealName,
    SUM(Wins) TotalWins,
    SUM(Losses) TotalLosses,
    ROUND(SUM(WINS) * 1.0 / (SUM(Wins) + SUM(Losses)), 2) WinPct
FROM leaguemembers
GROUP BY RealName
ORDER BY WinPct DESC