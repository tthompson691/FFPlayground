import requests
import pandas as pd
from constants import get_base_endpoint, LEAGUE_MEMBERS
from espn_cookies import SWID, ESPN_S2_THEBOYS

cookies = {"swid": SWID, "espn_s2": ESPN_S2_THEBOYS}

def get_r_json(r, year):
    if year < 2018:
        return r.json()[0]
    else:
        return r.json()

def get_player_meta(year):
    url = get_base_endpoint(year)
    params = {"view": "mMatchup", "seasonId": year}
    r = requests.get(url, params=params, verify=False, cookies=cookies)
    r.raise_for_status()
    
    r = get_r_json(r, year)
    
    dfs = []
    for thing in r["teams"]:
        dfs.append(pd.json_normalize(thing["roster"]["entries"]))
        
    return pd.concat(dfs).rename(
        {
            "playerPoolEntry.player.firstName": "FirstName",
            "playerPoolEntry.player.lastName": "LastName",
            "playerPoolEntry.player.fullName": "FullName",
            "playerPoolEntry.player.id": "PlayerID",
            "playerPoolEntry.player.defaultPositionId": "PositionID",
            "playerPoolEntry.player.proTeamId": "ProTeamID",
        },
        axis=1
    ).assign(
        Year=year
    )[["Year", "PlayerID", "PositionID", "ProTeamID", "FirstName", "LastName", "FullName"]]
    
    
def get_player_scores(year):
    url = get_base_endpoint(year)
    slotcodes = {
        0 : 'QB', 2 : 'RB', 4 : 'WR',
        6 : 'TE', 16: 'Def', 17: 'K',
        20: 'Bench', 21: 'IR', 23: 'Flex'
    }
    all_res = []
    
    for week in range(1, 18):
        params = {"view": ["mMatchup", "mMatchupScore"], "scoringPeriodId": week}
        r = requests.get(url, params=params, cookies=cookies, verify=False)
        r = get_r_json(r, year)
        for tm in r['teams']:
            tmid = tm['id']
            for p in tm['roster']['entries']:
                res = {
                    "Week": week,
                    "OnTeamID": tmid,
                    "PlayerID": p['playerPoolEntry']['player']['id'],
                    "LineupSlotID": p['lineupSlotId'],
                    "IsInjured": p['playerPoolEntry']['player']["injured"]
                }
                # injured status (need try/exc bc of D/ST)
                try:
                    res["InjuryStatus"] = p['playerPoolEntry']['player']['injuryStatus']
                except:
                    res["InjuryStatus"] = None

                
                # projected/actual points
                for stat in p['playerPoolEntry']['player']['stats']:
                    if stat['scoringPeriodId'] != week:
                        continue
                    if stat['statSourceId'] == 0:
                        res["ActualScore"] = round(stat['appliedTotal'], 2)
                    elif stat['statSourceId'] == 1:
                        res["ProjectedScore"] = round(stat['appliedTotal'], 2)
                        
                all_res.append(res)
                
    return pd.DataFrame(data=all_res).assign(Year=2022)

def get_matchups(year):
    url = get_base_endpoint(year)
    r = requests.get(url, params={"view": "mMatchup"}, cookies=cookies, verify=False)
    r = get_r_json(r, year)
    matchups = []
    for matchup in r["schedule"]:
            week = matchup["matchupPeriodId"]
            try:
                team1_id = matchup['home']['teamId']
                team1_score = matchup['home']['totalPoints']
            except KeyError:
                # when this happens, it means a first-round playoff bye is happening
                # self.playoff_threshold = week
                team1_id = "NA"
                team1 = "NA"
                # team1_score = np.nan

            try:
                team2_id = matchup['away']['teamId']
                # team2 = self.league_members.loc[team2_id, "member_name"]
                team2_score = matchup['away']["totalPoints"]
            except KeyError:
                # self.playoff_threshold = week
                team2_id = "NA"
                team2 = "NA"
                # team2_score = np.nan

            winner = team1_id if team1_score > team2_score else team2_id
            loser = team1_id if team1_score < team2_score else team2_id

            matchups.append(
                {
                    "Week": week,
                    "HomeTeamID": team1_id,
                    "HomeTeamScore": team1_score,
                    "AwayTeamID": team2_id,
                    "AwayTeamScore": team2_score,
                    "Winner": winner,
                    "Loser": loser
                }
            )

    matchups_df = pd.DataFrame(matchups).assign(Year=2022)
    matchups_df["Margin"] = abs(matchups_df["HomeTeamScore"] - matchups_df["AwayTeamScore"])

    return matchups_df


def get_members():
    members_dfs = []
    for year in range(2015, 2023):
        url = get_base_endpoint(year=year)
        r = requests.get(url, cookies=cookies, verify=False)
        r = get_r_json(r, year)
        members_df = pd.json_normalize(r, record_path="members")
        # members_df["RealName"] = members_df["displayName"].apply(lambda x: LEAGUE_MEMBERS[x])
        members_dfs.append(members_df.set_index("displayName").merge(
            right=pd.Series(LEAGUE_MEMBERS, name="RealName"),
            left_index=True,
            right_index=True).reset_index().rename(
                {"index": "DisplayName", "id": "MemberID"}, axis=1).drop(
                    "isLeagueManager", axis=1
                )
        )
    
    return pd.concat(members_dfs).drop_duplicates()

if __name__ == "__main__":
    df = get_members()
    df