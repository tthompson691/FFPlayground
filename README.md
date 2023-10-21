Steps to get this repo working locally:

1) Create file under `src` called `secrets.py`
2) Declare the following variables in `secrets.py`:
    a) `LEAGUE_ID`: your fantasy league's ID. Can be found in the URL when viewing your league in the browser.
    b) `SWID`: One of the two ESPN cookies you'll have to find via "inspect" in your browser
    c) `ESPN_S2`: The other ESPN cookie to find
    d) `LEAGUE_MEMBERS`: `dict` whose keys are the ESPN usernames of your league members (can be seen in API responses), and values are real names. Just a personal touch. If you don't want to bother with this, just set it to an empty dict.
3) Run `hydrate_db.py` in `scripts`. It will create a sqlite DB file that's stored (untracked) in the repo.