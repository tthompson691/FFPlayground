from constants import FANTASY_BASE_ENDPOINT, LEAGUE_ID
import requests
import pandas as pd
from espn_cookies import ESPN_S2_THEBOYS, SWID

league_url = FANTASY_BASE_ENDPOINT + str(LEAGUE_ID)

cookies = {"swid": SWID, "espn_s2": ESPN_S2_THEBOYS}

def get_projected_vs_actual():
    params = {"view": "kona_player_info", "seasonId": 2022}
    headers = {
            "User-Agent": "PostmanRuntime/7.33.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip deflate br",
            "Connection": "keep-alive"
        }
    r = requests.get(league_url, params=params, headers=headers, verify=False, cookies=cookies)
    
    r
    
    
if __name__ == "__main__":
    get_projected_vs_actual()