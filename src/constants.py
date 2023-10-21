from secrets import LEAGUE_ID

FANTASY_BASE_ENDPOINT_NEW = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/"

def get_base_endpoint(year):
    if year > 2018:
        return f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{LEAGUE_ID}"
    else:
        return f"https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{LEAGUE_ID}?seasonId={year}"

    # return f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{LEAGUE_ID}"
   