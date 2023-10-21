SELECT
	RealName,
	AVG(FinalRank) AvgFinalRank,
	(
		SELECT COUNT(*)
		FROM leaguemembers l2
		WHERE FinalRank = 1 AND l2.Realname = l.RealName
		GROUP BY RealName
	) LeagueWins
FROM leaguemembers l
GROUP BY l.RealName
ORDER BY AVG(FinalRank) DESC