import pandas as pd
import os
import requests
from constants import *
from ffl_requests import ESPNFFLRequest, Season, Draft


year_2020 = ESPNFFLRequest(2019, LEAGUE_ID)
# season = Season(year_2020.members_request, year_2020.matchups_request)
# draft = Draft()
# draft.get_player_df(year_2020.roster_request)
# draft.get_draft_summary(year_2020.draft_request, season.league_members)

# print("debug")

all_weeks = year_2020.get_player_scores_request()
all_weeks