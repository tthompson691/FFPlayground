SELECT
	d."Round",
	d.RoundPickNumber,
	d.OverallPickNumber,
	p.FullName,
	p.Position,
	l.RealName,
	l.FullTeamName
FROM drafts d
JOIN leaguemembers l
	ON d.MemberID = l.MemberID
	AND d."Year" = l."Year"
JOIN players p
	ON d.PlayerID = p.PlayerID
WHERE d."Year" = {year}