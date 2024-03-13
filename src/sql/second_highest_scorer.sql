SELECT
    RealName,
    Year,
    Week,
    MAX(score)
FROM vw_pointsfor_by_week v
WHERE score < (
    SELECT MAX(score)
    FROM vw_pointsfor_by_week
    WHERE Week = v.Week AND Year = V.Year
    )
GROUP BY Year, Week