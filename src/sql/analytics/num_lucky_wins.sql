SELECT
	a.RealName,
	COUNT(a.RealName) NumLuckyWins
FROM
(SELECT
    RealName,
    Year,
    Week,
    MIN(PointsFor)
FROM vw_pointsfor_by_week v
WHERE PointsFor > (
    SELECT MIN(PointsFor)
    FROM vw_pointsfor_by_week
    WHERE Week = v.Week AND Year = V.Year
    )
GROUP BY Year, Week) a
JOIN vw_matchups_with_realnames vmwr
	ON a.RealName = vmwr.WinnerName
	AND a.Year = vmwr."Year"
	AND a.Week = vmwr.Week
GROUP BY a.RealName
ORDER BY NumLuckyWins DESC;