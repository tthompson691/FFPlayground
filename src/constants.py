FANTASY_BASE_ENDPOINT_NEW = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/"

LEAGUE_ID = 331354

LEAGUE_MEMBERS = {
    "mgmcqu1882373": "Gray",
    "navyfootball619": "Travis",
    "harrisonsharp": "Harry",
    "drewpo3479634": "Drew",
    "jrcagnina": "Jefferson",
    "jasonba25": "The J",
    "keepdigginwatson": "Zac",
    "cal.wheeless@gmail.com": "Cal",
    "schenk3536110": "Schenkey",
    "jackthweatt": "Jack",
    "Acompton101": "A Comp",
    "wilcannotspell": "Wil G",
    "mustang22292": "Johnny",
    "Lahafreak": "Devin",
    "Nude Tayne": "Chris gitndat cash money?",
    "conko bob 43": "Collin"
}

def get_base_endpoint(year):
    if year > 2018:
        return f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{LEAGUE_ID}"
    else:
        return f"https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{LEAGUE_ID}?seasonId={year}"
    
   