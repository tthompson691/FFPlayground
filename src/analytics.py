import sqlalchemy
import os
import pandas as pd
import numpy as np
import sys
import emoji
from scripts.hydrate_db import create_db_connection
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms
import streamlit as st

SQL_PATH = os.path.abspath(os.path.join(__file__, "..", "sql"))
# SQL_PATH = os.path.join(os.path.abspath(""), "sql")


class SQLConn:
    def __init__(self):
        db_path = os.path.abspath(os.path.join(__file__, "..", "..", "FFLPlayground.db"))
        if "win" in sys.platform:
            conn_str = f"sqlite:///{db_path}"
        else:
            conn_str = f"sqlite:////{db_path}"

        engine = sqlalchemy.create_engine(conn_str)
        self.conn = engine.connect()

    def close_connection(self):
        self.conn.close()


def get_league_leaderboard():
    db = SQLConn()
    with open(os.path.join(SQL_PATH, "avg_final_rank.sql"), "r") as f:
        query = f.read()

    res = pd.read_sql(query, con=db.conn).fillna(0)
    res["LeagueWins"] = res["LeagueWins"].astype(int)
    res["AvgFinalRank"] = res["AvgFinalRank"].round(2)
    db.close_connection()
    return res


def get_luck_scores(year, week):
    con = create_db_connection()
    with open(os.path.join(SQL_PATH, "get_matchups_by_year_week.sql"), "r") as f:
        query = f.read().format(year=year, week=week)

    df = pd.read_sql(query, con=con)

    all_scores = np.array(df["HomeTeamScore"].tolist() + df["AwayTeamScore"].tolist())

    stddev = all_scores.std()
    avg = all_scores.mean()

    df["LuckyWin"] = df[["HomeTeamScore", "AwayTeamScore"]].max(axis=1) <= avg - (stddev / 2)
    df["UnluckyLoss"] = df[["HomeTeamScore", "AwayTeamScore"]].min(axis=1) >= avg + (stddev / 2)

    return df


def get_alltime_podium():
    con = create_db_connection()
    ## SELECT PODIUM BY YEAR ##
    with open(os.path.join(SQL_PATH, "analytics", "select_podium_by_year.sql"), "r") as f:
        query = f.read()

    podium = pd.read_sql(query, con=con)
    all_player_names = pd.read_sql("SELECT DISTINCT RealName FROM leaguemembers", con=con)[
        "RealName"
    ].to_list()

    cumulative_podium_df = pd.DataFrame(
        {
            "RealName": n,
            "FirstPlaceFinishes": [
                f'{emoji.emojize(":1st_place_medal:")} {y}'
                for y in list(
                    podium[(podium["RealName"] == n) & (podium["FinalRank"] == 1)]["Year"]
                )
            ],
            "SecondPlaceFinishes": [
                f'{emoji.emojize(":2nd_place_medal:")} {y}'
                for y in list(
                    podium[(podium["RealName"] == n) & (podium["FinalRank"] == 2)]["Year"]
                )
            ],
            "ThirdPlaceFinishes": [
                f'{emoji.emojize(":3rd_place_medal:")} {y}'
                for y in list(
                    podium[(podium["RealName"] == n) & (podium["FinalRank"] == 3)]["Year"]
                )
            ],
        }
        for n in all_player_names
    )
    cumulative_podium_df["OverallScore"] = (
        3 * cumulative_podium_df["FirstPlaceFinishes"].str.len()
        + 2 * cumulative_podium_df["SecondPlaceFinishes"].str.len()
        + cumulative_podium_df["ThirdPlaceFinishes"].str.len()
    )
    cumulative_podium_df["Rank"] = (
        cumulative_podium_df["OverallScore"].rank(method="min", ascending=False).astype(int)
    )
    cumulative_podium_df = cumulative_podium_df.sort_values(
        by="OverallScore", ascending=False
    ).reset_index(drop=True)[
        [
            "Rank",
            "RealName",
            "OverallScore",
            "FirstPlaceFinishes",
            "SecondPlaceFinishes",
            "ThirdPlaceFinishes",
        ]
    ]
    return cumulative_podium_df


def get_over_under_perform_df():
    def get_colors(df):
        df["diffs"] = df["WinPct"] - df["ExpectedWinPct"]
        max_success = df["diffs"].max()
        max_fail = df["diffs"].min()
        df["Color"] = df.apply(
            lambda x: (0, x["diffs"] / max_success, 0)
            if x["diffs"] > 0
            else (x["diffs"] / max_fail, 0, 0),
            axis=1,
        )
        return df

    con = create_db_connection()
    with open(os.path.join(SQL_PATH, "analytics", "lifetime_pfa_vs_winpct.sql"), "r") as f:
        query = f.read()

    df = pd.read_sql(sql=query, con=con)

    z = np.polyfit(df["Ratio"], df["WinPct"], 1)
    p = np.poly1d(z)
    df["ExpectedWinPct"] = p(df["Ratio"])
    return get_colors(df)


def get_over_under_perform_plot():
    df = get_over_under_perform_df()
    fig, ax = plt.subplots()
    x_spot = 1
    y_spot = 0.5
    ax.scatter(x=df["Ratio"], y=df["WinPct"], color=df["Color"])
    line = mlines.Line2D([x_spot, x_spot], [0, 0.8], color="black")
    line2 = mlines.Line2D([0.6, 1.2], [y_spot, y_spot], color="black")
    ax.add_line(line)
    ax.add_line(line2)

    ax.plot(df["Ratio"], df["ExpectedWinPct"], "b--")
    ax.set_xlabel("PointsFor:PointsAgainst ratio")
    ax.set_ylabel("WinPct")
    fig.set_figwidth(5)
    fig.set_figheight(5)
    ax.set_title(
        "Have you over or underperformed based on your PointsFor:PointsAgainst ratio? (2015-2023)"
    )
    for i, name in enumerate(df["RealName"]):
        ax.annotate(name, (df.loc[i, "Ratio"], df.loc[i, "WinPct"]))
    return fig


def streamlit_over_under_perform():
    df = get_over_under_perform_df()
    st.scatter_chart(data=df, x="Ratio", y="WinPct", color="Color")


if __name__ == "__main__":
    streamlit_over_under_perform()
