SELECT
    a.RealName,
    SUM(a.PointsFor) TotalPointsFor,
    SUM(a.PointsAgainst) TotalPointsAgainst,
    ROUND(SUM(A.PointsFor) / SUM(A.PointsAgainst), 2) Ratio
FROM
(SELECT
    pf.RealName,
    pf.PointsFor PointsFor,
    pa.PointsAgainst PointsAgainst
FROM vw_pointsfor_by_week pf
JOIN vw_pointsagainst_by_week pa
    ON pf.Year = pa.Year
    AND pf.Week = pa.Week
    AND pf.RealName = pa.RealName) a
GROUP BY RealName
ORDER BY Ratio DESC