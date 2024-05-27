from league_secrets import LEAGUE_ID


def get_base_endpoint(year):
    if year > 2018:
        return f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{LEAGUE_ID}"
    else:
        return f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{LEAGUE_ID}?seasonId={year}"
