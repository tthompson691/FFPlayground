from constants import *
import requests
import pandas as pd
import numpy as np

class ESPNFFLRequest:
    def __init__(self, year, league_id):
        # self.endpoint = f"{FANTASY_BASE_ENDPOINT}{str(league_id)}?seasonID={str(year)}"
        self.endpoint = f"{FANTASY_BASE_ENDPOINT}{str(league_id)}"
        self.year = year
        self.league_id = league_id
        self.members_request = self.get_members_request()
        self.matchups_request = self.get_matchups_request()

    def get_members_request(self):
        params = {"seasonId": self.year}

        return requests.get(self.endpoint, params=params, verify=False).json()[0]

    def get_matchups_request(self):
        params = {
            "seasonId": self.year,
            "view": "mMatchup"
        }

        return requests.get(self.endpoint, params=params, verify=False).json()[0]


class Season:
    def __init__(self, members_r, matchups_r):
        self.league_members = self.get_members(members_r)
        self.all_matchups = self.get_matchups(matchups_r)
        self.playoff_threshold = None
        self.cumulative_results = self.get_cumulative_results(self.all_matchups)
        self.winner = self.determine_winner(self.all_matchups)

    def get_members(self, r):
        league_members = []

        for member in r["members"]:
            try:
                member_name = LEAGUE_MEMBERS[member["displayName"]]
            except KeyError:
                print(f"No member name found for {member['displayName']}")
                member_name = member["displayName"]

            owner_id = member["id"]

            for team in r["teams"]:
                if team["owners"][0] == owner_id:
                    team_name = team["location"] + " " + team["nickname"]
                    short_id = team["id"]

            league_members.append(
                {
                    "owner_id": owner_id,
                    "member_name": member_name,
                    "team_name": team_name,
                    "short_id": short_id
                }
            )

        member_df = pd.DataFrame(league_members)
        member_df.set_index("short_id", inplace=True)

        return member_df

    def get_matchups(self, r):
        matchups = []
        for matchup in r["schedule"]:
            week = matchup["matchupPeriodId"]
            try:
                team1_id = matchup['home']['teamId']
                team1 = self.league_members.loc[team1_id, "member_name"]
                team1_score = matchup['home']['totalPoints']
            except KeyError:
                # when this happens, it means a first-round playoff bye is happening
                self.playoff_threshold = week
                team1_id = "NA"
                team1 = "NA"
                team1_score = np.nan

            try:
                team2_id = matchup['away']['teamId']
                team2 = self.league_members.loc[team2_id, "member_name"]
                team2_score = matchup['away']["totalPoints"]
            except KeyError:
                self.playoff_threshold = week
                team2_id = "NA"
                team2 = "NA"
                team2_score = np.nan

            winner = team1 if team1_score > team2_score else team2
            loser = team1 if team1_score < team2_score else team2

            matchups.append(
                {
                    "week": week,
                    "team 1": team1,
                    "team 1 score": team1_score,
                    "team 2": team2,
                    "team 2 score": team2_score,
                    "winner": winner,
                    "loser": loser
                }
            )

        matchups_df = pd.DataFrame(matchups)

        return matchups_df

    def get_cumulative_results(self, matchups: pd.DataFrame):
        for team in matchups["team 1"].unique():
            _filter = (matchups["team 1"] == team) | (matchups["team 2"] == team)

            team_df = matchups[_filter]

            mean_score = self.get_mean_score(team, team_df)
            wins, losses = self.determine_record(team, team_df)

    def determine_winner(self, matchups: pd.DataFrame):
        final_week_df = matchups[matchups["week"] == matchups["week"].max()]
        final_week_df.reset_index(drop=True, inplace=True)
        return final_week_df.loc[0, "winner"]

    def determine_record(self, team, team_df: pd.DataFrame):
        wins = losses = 0
        if self.playoff_threshold is not None:
            reg_season_df = team_df[team_df["week"] < self.playoff_threshold]
        else:
            reg_season_df = team_df

        for i, row in reg_season_df.iterrows():
            if row["winner"] == team:
                wins += 1
            else:
                losses += 1

        return wins, losses

    def get_mean_score(self, team, team_df: pd.DataFrame):
        scores = []

        if self.playoff_threshold is not None:
            reg_season_df = team_df[team_df["week"] < self.playoff_threshold]
        else:
            reg_season_df = team_df

        for i, row in reg_season_df.iterrows():
            if row["team 1"] == team:
                scores.append(row["team 1 score"])
            else:
                scores.append(row["team 2 score"])

        return np.mean(scores)

