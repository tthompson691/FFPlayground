SELECT
    DISTINCT
    w.RealName,
    (SELECT
        SUM(ActualScore)
    FROM vw_weeklyteamscores w1
    WHERE w1.RealName = w.RealName
        AND w1.IsStarting = 1) StarterPoints,
    (SELECT
        SUM(ActualScore)
    FROM vw_weeklyteamscores w1
    WHERE w1.RealName = w.RealName
        AND w1.IsStarting = 0) BenchPoints
FROM vw_weeklyteamscores w