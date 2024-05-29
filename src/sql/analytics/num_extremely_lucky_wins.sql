SELECT
	a.RealName,
	COUNT(a.RealName) NumExtremelyLuckyWins
FROM
(SELECT
"Year",
"Week",
 RealName
FROM vw_pointsfor_by_week vpbw
WHERE PointsForWeeklyRankReverse = 2) a
JOIN vw_matchups_with_realnames vmwr
	ON a.RealName = vmwr.WinnerName
	AND a."Year" = vmwr."Year"
	AND a."Week" = vmwr."Week"
GROUP BY a.RealName
ORDER BY NumExtremelyLuckyWins DESC;