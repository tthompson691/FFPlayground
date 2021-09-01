import pandas as pd
import os
import requests
from constants import *
from ffl_requests import ESPNFFLRequest, Season


year_2020 = ESPNFFLRequest(2019, LEAGUE_ID)
season = Season(year_2020.members_request, year_2020.matchups_request)

print("debug")