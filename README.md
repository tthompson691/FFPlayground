# Welcome to FFL Playground!

The goal of this project is to minimize the number of calls we make to the bottomless void that is the ESPN FFL API - rather, we get the raw data up front into a local db, and run analytics locally rather than by hitting the API over and over.

Steps to get this repo working locally:

1) Create file under `src` called `league_secrets.py`
2) Declare the following variables in `league_secrets.py`:
    a) `LEAGUE_ID`: your fantasy league's ID. Can be found in the URL when viewing your league in the browser.
    b) `SWID`: One of the two ESPN cookies you'll have to find via "inspect" in your browser
    c) `ESPN_S2`: The other ESPN cookie to find
    d) `LEAGUE_MEMBERS`: `dict` whose keys are the ESPN usernames of your league members (can be seen in API responses), and values are real names. Just a personal touch. If you don't want to bother with this, just set it to an empty dict.
3) Run `hydrate_db.py` in `scripts`. It will create a sqlite DB file that's stored (untracked) in the repo.


# DB Table Schemas