SELECT
pfa.RealName,
pfa.Ratio,
wl.WinPct
FROM
(SELECT
    a.RealName,
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
GROUP BY RealName) pfa
JOIN
(SELECT
    RealName,
    ROUND(SUM(WINS) * 1.0 / (SUM(Wins) + SUM(Losses)), 2) WinPct
FROM leaguemembers
GROUP BY RealName
ORDER BY WinPct DESC) wl
ON pfa.RealName = wl.RealName