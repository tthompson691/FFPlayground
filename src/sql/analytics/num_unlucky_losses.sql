SELECT
	a.RealName,
	COUNT(a.RealName) NumUnluckyLosses
FROM
(SELECT
    RealName,
    Year,
    Week,
    MAX(PointsFor) PointsFor
FROM vw_pointsfor_by_week v
WHERE PointsFor  < (
    SELECT MAX(PointsFor)
    FROM vw_pointsfor_by_week
    WHERE Week = v.Week AND Year = V.Year
    )
GROUP BY Year, Week
) a
JOIN vw_matchups_with_realnames vmwr
	ON a.RealName = vmwr.LoserName
	AND a.Year = vmwr."Year"
	AND a.Week = vmwr.Week
GROUP BY a.RealName
ORDER BY NumUnluckyLosses DESC