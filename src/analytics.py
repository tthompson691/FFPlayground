import sqlalchemy
import os
import pandas as pd
import numpy as np

SQL_PATH = os.path.abspath(os.path.join(__file__, "..", "sql"))


class SQLConn:
    def __init__(self):
        db_path = os.path.abspath(os.path.join(__file__, "..", "..", "FFLPlayground.db"))
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
    with open(os.path.join(SQL_PATH, "get_matchups_by_year_week.sql"), "r") as f:
        query = f.read().format(year=year, week=week)

    db = SQLConn()
    df = pd.read_sql(query, con=db.conn)

    all_scores = np.array(df["HomeTeamScore"].tolist() + df["AwayTeamScore"].tolist())

    stddev = all_scores.std()
    avg = all_scores.mean()

    df["LuckyWin"] = df[["HomeTeamScore", "AwayTeamScore"]].max(axis=1) <= avg - (stddev / 2)
    df["UnluckyLoss"] = df[["HomeTeamScore", "AwayTeamScore"]].min(axis=1) >= avg + (stddev / 2)

    if df["LuckyWin"].any() or df["UnluckyLoss"].any():
        print("d")


if __name__ == "__main__":
    for week in range(1, 18):
        z = get_luck_scores(2022, week)
        z
