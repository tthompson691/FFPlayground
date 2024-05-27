SELECT
    RealName,
    Year,
    Week,
    MAX(PointsFor)
FROM vw_pointsfor_by_week v
WHERE PointsFor < (
    SELECT MAX(PointsFor)
    FROM vw_pointsfor_by_week
    WHERE Week = v.Week AND Year = V.Year
    )
GROUP BY Year, Week