SELECT
    Year,
    FinalRank,
    RealName
FROM leaguemembers
WHERE FinalRank IN (1, 2, 3)
ORDER BY Year, FinalRank ASC