SELECT
    RealName,
    SUM(ActualScoreTotal) TotalActualScore,
    SUM(ProjectedScoreTotal) TotalProjectedScore,
    ROUND(SUM(ActualScoreTotal) - SUM(ProjectedScoreTotal), 2) TotalDiff
FROM vw_weekly_projected_vs_actual
GROUP BY RealName
ORDER BY TotalDiff DESC