CREATE VIEW vw_pointsagainst_by_week AS
SELECT
    DISTINCT lm.RealName,
    vm.Year,
    vm.Week,
    CASE
        WHEN vm.AwayName = lm.RealName THEN HomeTeamScore
        WHEN vm.HomeName = lm.RealName THEN AwayTeamScore
    END PointsAgainst,
    RANK() OVER(
    PARTITION BY vm."Year", vm."Week"
    ORDER BY (CASE
        WHEN vm.AwayName = lm.RealName THEN HomeTeamScore
        WHEN vm.HomeName = lm.RealName THEN AwayTeamScore
    END) DESC
    ) PointsAgainstWeeklyRank,
    RANK() OVER(
    PARTITION BY vm."Year", vm."Week"
    ORDER BY (CASE
        WHEN vm.AwayName = lm.RealName THEN HomeTeamScore
        WHEN vm.HomeName = lm.RealName THEN AwayTeamScore
    END) ASC
    ) PointsAgainstWeeklyRankReverse
FROM vw_matchups_with_realnames vm
JOIN leaguemembers lm
    ON vm.Year = lm.Year
    AND (vm.AwayTeamID = lm.TeamID OR vm.HomeTeamID = lm.TeamID);