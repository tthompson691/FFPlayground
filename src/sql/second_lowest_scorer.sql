SELECT
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
GROUP BY Year, Week