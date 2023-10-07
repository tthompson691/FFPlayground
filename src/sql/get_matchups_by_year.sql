SELECT
	m."Year",
	m.Week,
	lh.FullTeamName HomeTeam,
	m.HomeTeamScore,
	la.FullTeamName AwayTeam,
	m.AwayTeamScore
FROM matchups m
JOIN leaguemembers lh
	ON m."Year" = lh."Year"
	AND m.HomeTeamID = lh.TeamID
JOIN leaguemembers la
	ON m."Year" = la."Year"
	AND m.AwayTeamID = la.TeamID
WHERE m."Year" = {year}