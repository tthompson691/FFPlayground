SELECT
	a.RealName,
	COUNT(a.RealName) NumExtremelyUnluckyLosses
FROM
(SELECT
"Year",
"Week",
 RealName
FROM vw_pointsfor_by_week vpbw
WHERE PointsForWeeklyRank = 2
GROUP BY Year, Week
) a
JOIN vw_matchups_with_realnames vmwr
	ON a.RealName = vmwr.LoserName
	AND a.Year = vmwr."Year"
	AND a.Week = vmwr."Week"
GROUP BY a.RealName
ORDER BY NumExtremelyUnluckyLosses DESC;