CREATE VIEW vw_pointsfor_by_week AS
SELECT
    DISTINCT lm.RealName,
    vm.Year,
    vm.Week,
    CASE
        WHEN vm.AwayName = lm.RealName THEN AwayTeamScore
        WHEN vm.HomeName = lm.RealName THEN HomeTeamScore
    END PointsFor,
    RANK() OVER(
    PARTITION BY vm."Year", vm."Week"
    ORDER BY (CASE
        WHEN vm.AwayName = lm.RealName THEN AwayTeamScore
        WHEN vm.HomeName = lm.RealName THEN HomeTeamScore
    END) DESC
    ) PointsForWeeklyRank,
    RANK() OVER(
    PARTITION BY vm."Year", vm."Week"
    ORDER BY (CASE
        WHEN vm.AwayName = lm.RealName THEN AwayTeamScore
        WHEN vm.HomeName = lm.RealName THEN HomeTeamScore
    END) ASC
    ) PointsForWeeklyRankReverse
FROM vw_matchups_with_realnames vm
JOIN leaguemembers lm
    ON vm.Year = lm.Year
    AND (vm.AwayTeamID = lm.TeamID OR vm.HomeTeamID = lm.TeamID);