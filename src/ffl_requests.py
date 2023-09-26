from constants import *
import requests
import pandas as pd
import numpy as np
import os

data_path = os.path.abspath(os.path.join(__file__, "..", "..", "data"))

class ESPNFFLRequest:
    def __init__(self, year, league_id):
        # self.endpoint = f"{FANTASY_BASE_ENDPOINT}{str(league_id)}?seasonID={str(year)}"
        self.endpoint = f"{FANTASY_BASE_ENDPOINT}{str(league_id)}"
        self.year = year
        self.league_id = league_id
        self.members_request = self.get_members_request()
        self.matchups_request = self.get_matchups_request()
        self.boxscore_request = self.get_boxscore_request()
        self.player_scores_request = self.get_player_scores_request()
        self.roster_request = self.get_roster_request()
        self.schedule_request = self.get_schedule_request()
        self.draft_request = self.get_draft_request()

    def get_members_request(self):
        params = {"seasonId": self.year}

        return requests.get(self.endpoint, params=params, verify=False).json()[0]

    def get_matchups_request(self):
        params = {
            "seasonId": self.year,
            "view": ["mMatchup", "mMatchupScore"]
        }

        return requests.get(self.endpoint, params=params, verify=False).json()[0]

    def get_boxscore_request(self):
        params = {
            "seasonId": self.year,
            "view": "mBoxscore"
        }

        return requests.get(self.endpoint, params=params, verify=False).json()[0]

    def get_player_scores_request(self):

        all_weeks = {i: requests.get(self.endpoint, params={"scoringPeriodId": i, "view": ["mMatchup", "mMatchupScore"]}, verify=False).json()[0]
                     for i in range(1, 17)}

        return all_weeks

    def get_roster_request(self):
        params = {
            "seasonId": self.year,
            "view": "mRoster"
        }

        return requests.get(self.endpoint, params=params, verify=False).json()[0]

    def get_schedule_request(self):
        params = {
            "seasonId": self.year,
            "view": "mSchedule"
        }

        return requests.get(self.endpoint, params=params, verify=False).json()[0]

    def get_draft_request(self):
        params = {
            "seasonId": self.year,
            "view": "mDraftDetail"
        }

        return requests.get(self.endpoint, params=params, verify=False).json()[0]


class Season:
    def __init__(self, members_r, matchups_r):
        self.matchups_r = matchups_r
        self.playoff_threshold = None
        self.league_members = self.get_members(members_r)
        self.all_matchups = self.get_matchups(matchups_r)
        self.season_average_score = self.determine_league_average_score()
        self.cumulative_results = self.get_cumulative_results(self.all_matchups)
        self.determine_luck_measures()
        self.winner = self.determine_winner()

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
        matchups_df["margin"] = abs(matchups_df["team 1 score"] - matchups_df["team 2 score"])

        return matchups_df

    def get_cumulative_results(self, matchups: pd.DataFrame):
        teams = []
        for team in matchups["team 1"].unique():
            _filter = (matchups["team 1"] == team) | (matchups["team 2"] == team)

            team_df = matchups[_filter]

            mean_score, mean_points_against, points_for, points_against = self.get_mean_score(team, team_df)
            wins, losses = self.determine_record(team, team_df)
            win_pct = wins / (wins + losses)

            teams.append(
                {
                    "team": team,
                    "average score": mean_score,
                    "total points for": points_for,
                    "avg points against": mean_points_against,
                    "total points against": points_against,
                    "wins": wins,
                    "losses": losses,
                    "win%": win_pct * 100,
                }
            )

        results = pd.DataFrame(teams)
        results.set_index("team", drop=True, inplace=True)
        results.sort_values(by="wins", ascending=False, inplace=True)
        return results

    def determine_winner(self):
        schedule = self.matchups_r["schedule"]
        final_week = schedule[-1]["matchupPeriodId"]
        cship_results = [i for i in schedule
                        if i["matchupPeriodId"] == final_week
                        and i["playoffTierType"] == "WINNERS_BRACKET"][0]
        winning_team_id = cship_results[cship_results["winner"].lower()]["teamId"]
        return self.league_members.loc[winning_team_id, "member_name"]

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
        avg_points_against = []
        points_for = points_against = 0

        if self.playoff_threshold is not None:
            reg_season_df = team_df[team_df["week"] < self.playoff_threshold]
        else:
            reg_season_df = team_df

        for i, row in reg_season_df.iterrows():
            if row["team 1"] == team:
                scores.append(row["team 1 score"])
                avg_points_against.append(row["team 2 score"])
                points_for += row["team 1 score"]
                points_against += row["team 2 score"]
            else:
                scores.append(row["team 2 score"])
                avg_points_against.append(row["team 1 score"])
                points_for += row["team 2 score"]
                points_against += row["team 1 score"]

        return np.mean(scores), np.mean(avg_points_against), points_for, points_against

    def determine_league_average_score(self):
        if self.playoff_threshold is not None:
            reg_season_df = self.all_matchups[self.all_matchups["week"] < self.playoff_threshold]
        else:
            reg_season_df = self.all_matchups

        return (reg_season_df["team 1 score"].sum() + reg_season_df["team 2 score"].sum()) / \
               (2 * reg_season_df.shape[0])

    def determine_luck_measures(self):
        self.determine_luck_measure_1()
        self.determine_luck_measure_2()
        self.determine_luck_measure_3()

    def determine_luck_measure_1(self):
        # difference between points for rank and win% rank
        self.cumulative_results["points_for rank"] = self.cumulative_results["total points for"].\
            rank(method='min', ascending=False)

        self.cumulative_results["win% rank"] = self.cumulative_results["win%"].\
            rank(method='min', ascending=False)

        self.cumulative_results["luck measure 1"] = self.cumulative_results["points_for rank"] - \
                                                    self.cumulative_results["win% rank"]

    def determine_luck_measure_2(self):
        # ratio of your average points against to the league average score
        self.cumulative_results["luck measure 2"] = self.season_average_score /\
            self.cumulative_results["avg points against"]

    def determine_luck_measure_3(self):
        # number of top-3 losses and bottom-3 wins
        # final value for each person is (lucky wins - unlucky losses)
        unlucky_losses = []
        lucky_wins = []
        for week in self.all_matchups["week"].unique():
            if self.playoff_threshold is not None and week < self.playoff_threshold:
                week_df = self.rearrange_week_df(self.all_matchups[self.all_matchups["week"] == week], week)
                week_unlucky_losses, week_lucky_wins = self.determine_unlucky_losses_lucky_wins(week_df)

                if week_unlucky_losses.shape[0] != 0:
                    unlucky_losses.append(week_unlucky_losses)

                if week_lucky_wins.shape[0] != 0:
                    lucky_wins.append(week_lucky_wins)

        unlucky_losses_df = pd.concat(unlucky_losses)
        lucky_wins_df = pd.concat(lucky_wins)

        unlucky_losses_count = unlucky_losses_df.value_counts("team")
        unlucky_losses_count.rename("UL", inplace=True)
        lucky_wins_count = lucky_wins_df.value_counts("team")
        lucky_wins_count.rename("LW", inplace=True)

        self.join_counts_to_cumulative_data(unlucky_losses_count, lucky_wins_count)

        print("debug")

    def join_counts_to_cumulative_data(self, losses, wins):
        self.cumulative_results = pd.concat([self.cumulative_results, losses, wins], axis=1)
        self.cumulative_results.fillna(0, inplace=True)
        self.cumulative_results["luck measure 3"] = self.cumulative_results["LW"] - self.cumulative_results["UL"]
        print("debug")

    @staticmethod
    def rearrange_week_df(df, week):
        week_df = pd.DataFrame(columns=["week", "team", "score", "win"])
        week_df["team"] = pd.concat([df["team 1"], df["team 2"]])
        week_df["score"] = pd.concat([df["team 1 score"], df["team 2 score"]])
        winners = list(df["winner"].values)
        week_df["win"] = [True if row["team"] in winners else False for i, row in week_df.iterrows()]
        week_df["week"] = week
        week_df.sort_values(by="score", ascending=False, inplace=True)
        week_df.reset_index(drop=True, inplace=True)
        return week_df

    @staticmethod
    def determine_unlucky_losses_lucky_wins(week_df):
        unlucky_losses = week_df.head(3)[week_df["win"] == False]
        lucky_wins = week_df.tail(3)[week_df["win"] == True]

        return unlucky_losses, lucky_wins


class Draft:
    def __init__(self):
        self.draft_summary = None
        # self.player_df = self.get_player_df()

    def get_draft_summary(self, r, members: pd.DataFrame):
        members.reset_index(drop=False, inplace=True)
        members.drop(labels="owner_id", axis=1, inplace=True)
        players = pd.read_csv(os.path.join(data_path, "player_ids.csv"))
        draft_raw = r["draftDetail"]["picks"]
        all_picks = [
            {
                "round": pick["roundId"],
                "round pick": pick["roundPickNumber"],
                "overall pick": pick["id"],
                "player_id": pick["playerId"],
                "short_id": pick["teamId"]
            }
            for pick in draft_raw
        ]

        draft_summary = pd.DataFrame(all_picks)
        res = pd.merge(left=draft_summary, right=members, on="short_id", how="left")

        self.draft_summary = pd.merge(left=res, right=players, on="player_id", how="left")


    @staticmethod
    def get_player_df(r):
        all_players = []
        for team in r["teams"]:
            for player in team["roster"]["entries"]:
                player_name = player["playerPoolEntry"]["player"]["fullName"]
                player_id = player["playerPoolEntry"]["player"]["id"]
                all_players.append({
                    "player_name": player_name,
                    "player_id": player_id
                })

        if "player_ids.csv" in os.listdir(data_path):
            existing_df = pd.read_csv(os.path.join(data_path, "player_ids.csv"))
            new_df = pd.concat([pd.DataFrame(all_players), existing_df], ignore_index=True).\
                drop_duplicates().\
                reset_index(drop=True)
            new_df.to_csv(os.path.join(data_path, "player_ids.csv"), index=False)
        else:
            new_df = pd.DataFrame(all_players)
            new_df.to_csv(os.path.join(data_path, "player_ids.csv"), index=False)

