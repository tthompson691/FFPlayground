import sqlalchemy
import os
import pandas as pd

SQL_PATH = os.path.abspath(os.path.join(__file__, "..", "sql"))

class SQLConn:
    def __init__(self):
        db_path = os.path.abspath(os.path.join(__file__, "..", "FFLPlayground.db"))
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


if __name__ == "__main__":
    z = get_league_leaderboard()
    z