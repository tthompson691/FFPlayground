CREATE VIEW vw_weekly_projected_vs_actual AS
SELECT
    Year,
    Week,
    RealName,
    SUM(ProjectedScore) ProjectedScoreTotal,
    SUM(ActualScore) ActualScoreTotal
FROM vw_weeklyteamscores
WHERE IsStarting = 1
GROUP BY Year, Week, RealName