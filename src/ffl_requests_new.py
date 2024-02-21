import requests
import pandas as pd
from constants import get_base_endpoint
from league_secrets import SWID, ESPN_S2_THEBOYS, LEAGUE_MEMBERS

cookies = {"swid": SWID, "espn_s2": ESPN_S2_THEBOYS}


def get_r_json(r, year):
    if year <= 2018:
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

    positions = pd.Series(
        {2: "RB", 3: "WR", 1: "QB", 4: "TE", 5: "K", 16: "D/ST"}, name="PositionID"
    )

    res = (
        pd.concat(dfs)
        .rename(
            {
                "playerPoolEntry.player.firstName": "FirstName",
                "playerPoolEntry.player.lastName": "LastName",
                "playerPoolEntry.player.fullName": "FullName",
                "playerPoolEntry.player.id": "PlayerID",
                "playerPoolEntry.player.defaultPositionId": "PositionID",
                "playerPoolEntry.player.proTeamId": "ProTeamID",
            },
            axis=1,
        )
        .assign(Year=year)[
            ["Year", "PlayerID", "PositionID", "ProTeamID", "FirstName", "LastName", "FullName"]
        ]
    )

    return res.join(positions, on="PositionID", lsuffix="l", rsuffix="r").rename(
        {"PositionIDl": "PositionID", "PositionIDr": "Position"}, axis=1
    )


def parse_player_stats(player_stats, year, week):
    act_score = proj_score = None
    if year <= 2018:
        player_stats = player_stats[0]
        if player_stats["scoringPeriodId"] != week:
            return None, None

    else:
        # projected/actual points
        for stat in player_stats:
            if stat["scoringPeriodId"] != week:
                continue
            if stat["statSourceId"] == 0:
                act_score = round(stat["appliedTotal"], 2)
            elif stat["statSourceId"] == 1:
                proj_score = round(stat["appliedTotal"], 2)

    return act_score, proj_score


def get_player_scores(year):
    url = get_base_endpoint(year)
    # slotcodes = {
    #     0 : 'QB', 2 : 'RB', 4 : 'WR',
    #     6 : 'TE', 16: 'Def', 17: 'K',
    #     20: 'Bench', 21: 'IR', 23: 'Flex'
    # } #noqa
    all_res = []

    for week in range(1, 18):
        params = {"view": ["mMatchup", "mMatchupScore"], "scoringPeriodId": week}
        r = requests.get(url, params=params, cookies=cookies, verify=False)
        r = get_r_json(r, year)
        for tm in r["teams"]:
            tmid = tm["id"]
            if tmid == 1:
                tmid
            for p in tm["roster"]["entries"]:
                res = {
                    "Week": week,
                    "OnTeamID": tmid,
                    "PlayerID": p["playerPoolEntry"]["player"]["id"],
                    "LineupSlotID": p["lineupSlotId"],
                    "IsInjured": p["playerPoolEntry"]["player"]["injured"],
                }
                # injured status (need try/exc bc of D/ST)
                try:
                    res["InjuryStatus"] = p["playerPoolEntry"]["player"]["injuryStatus"]
                except KeyError:
                    res["InjuryStatus"] = None

                act_score, proj_score = parse_player_stats(
                    p["playerPoolEntry"]["player"]["stats"], year, week
                )
                #
                if act_score:
                    res["ActualScore"] = act_score

                if proj_score:
                    res["ProjectedScore"] = proj_score

                all_res.append(res)

    return pd.DataFrame(data=all_res).assign(Year=year)


def get_matchups(year):
    url = get_base_endpoint(year)
    r = requests.get(url, params={"view": "mMatchup"}, cookies=cookies, verify=False)
    r = get_r_json(r, year)
    matchups = []
    for matchup in r["schedule"]:
        week = matchup["matchupPeriodId"]
        try:
            team1_id = matchup["home"]["teamId"]
            team1_score = matchup["home"]["totalPoints"]
        except KeyError:
            # when this happens, it means a first-round playoff bye is happening
            # self.playoff_threshold = week
            team1_id = "NA"
            # team1 = "NA"
            # team1_score = np.nan

        try:
            team2_id = matchup["away"]["teamId"]
            # team2 = self.league_members.loc[team2_id, "member_name"]
            team2_score = matchup["away"]["totalPoints"]
        except KeyError:
            # self.playoff_threshold = week
            team2_id = "NA"
            # team2 = "NA"
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
                "Loser": loser,
            }
        )

    matchups_df = pd.DataFrame(matchups).assign(Year=year)
    matchups_df["Margin"] = abs(matchups_df["HomeTeamScore"] - matchups_df["AwayTeamScore"])

    return matchups_df


def get_final_ranks(year):
    url = get_base_endpoint(year)
    params = {"view": "mScoreboard"}
    r = requests.get(url, params=params, cookies=cookies, verify=False)
    r = get_r_json(r, year)
    return (
        pd.json_normalize(r, record_path="teams")
        .rename(
            {
                "id": "TeamID",
                "rankCalculatedFinal": "FinalRank",
                "record.overall.losses": "Losses",
                "record.overall.wins": "Wins",
                "record.overall.ties": "Ties",
            },
            axis=1,
        )
        .drop(
            ["abbrev", "divisionId", "location", "logo", "name", "nickname"],
            axis=1,
            errors="ignore",
        )
    )


def get_members():
    members_dfs = []
    for year in range(2015, 2024):
        url = get_base_endpoint(year=year)
        r = requests.get(url, cookies=cookies, verify=False)
        r = get_r_json(r, year)
        members_df = pd.json_normalize(r, record_path="members")
        teams_df = pd.json_normalize(r, record_path="teams").rename({"id": "TeamID"}, axis=1)
        teams_df["MemberID"] = teams_df["owners"].apply(lambda x: x[0])
        teams_df["Year"] = year
        # members_df["RealName"] = members_df["displayName"].apply(lambda x: LEAGUE_MEMBERS[x])
        members_df = (
            members_df.set_index("displayName")
            .merge(
                right=pd.Series(LEAGUE_MEMBERS, name="RealName"), left_index=True, right_index=True
            )
            .reset_index()
            .rename({"index": "DisplayName", "id": "MemberID"}, axis=1)
            .drop("isLeagueManager", axis=1)
        )
        members_df["MemberID"] = members_df["MemberID"].astype(str)
        # members_df = members_df.join(other=teams_df.assign(MemberID=teams_df["MemberID"].astype(str)), on="MemberID")
        members_df = pd.merge(
            left=members_df.assign(MemberID=members_df["MemberID"].astype(str)),
            right=teams_df.assign(MemberID=teams_df["MemberID"].astype(str)),
            on="MemberID",
        )

        league_res_df = get_final_ranks(year)

        members_df = pd.merge(left=members_df, right=league_res_df, on="TeamID")

        members_dfs.append(members_df)

    res = pd.concat(members_dfs)
    res["owners"] = res["owners"].astype(str)

    return res  # .assign(FullTeamName=res["location"] + " " + res["nickname"]).drop(
    #     ["location", "nickname", "owners"], axis=1
    # )


def fix_owning_team_id(df):
    df["TeamID"] = df["owningTeamIds"].apply(lambda x: x[0]).astype(int)

    return df.drop("owningTeamIds", axis=1)


def get_draft(year):
    url = get_base_endpoint(year)
    params = {"view": "mDraftDetail"}
    r = requests.get(url, params=params, cookies=cookies, verify=False)
    r = get_r_json(r, year)
    df = pd.DataFrame(r["draftDetail"]["picks"])
    if year <= 2018:
        df = df.drop("owningTeamIds", axis=1)
    return (
        df.rename(
            {
                "autoDraftTypeId": "AutoDraftTypeID",
                "bidAmount": "BidAmount",
                "keeper": "IsKeeper",
                "lineupSlotId": "LineupSlotID",
                "memberId": "MemberID",
                "nominatingTeamId": "NominatingTeamID",
                "overallPickNumber": "OverallPickNumber",
                "playerId": "PlayerID",
                "reservedForKeeper": "IsReservedForKeeper",
                "roundId": "Round",
                "roundPickNumber": "RoundPickNumber",
                "teamId": "TeamID",
                "tradeLocked": "IsTradeLocked",
            },
            axis=1,
        )
        .drop("id", axis=1)
        .assign(Year=year)
    )


if __name__ == "__main__":
    year = 2015
    bigres = get_player_scores(year)
    bigres
