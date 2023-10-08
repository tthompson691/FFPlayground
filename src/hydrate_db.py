import requests
import pandas as pd
import sqlite3
import os
from ffl_requests_new import get_player_meta, get_player_scores, get_matchups, get_members, get_draft


def insert_as_new_table(df, table_name):
    con = sqlite3.connect("FFLPlayground.db")
    df.to_sql(name=table_name, con=con, index=False, if_exists="append")
    con.close()
    
    
def populate_player_meta(year):
    insert_as_new_table(get_player_meta(year), table_name="players")
    
def populate_player_projections(year):
    insert_as_new_table(get_player_scores(year), table_name="playerscores")


def populate_proteams():
    df = pd.read_csv(os.path.abspath(os.path.join(__file__, "..", "..", "data", "proteams.csv")))
    insert_as_new_table(df=df, table_name="proteams")
    
def populate_matchups(year):
    insert_as_new_table(df=get_matchups(year), table_name="matchups")
    
def populate_league_members():
    insert_as_new_table(df=get_members(), table_name="leaguemembers")

def populate_draft_info(year):
    insert_as_new_table(df=get_draft(year), table_name="drafts")

if __name__ == "__main__":
    populate_proteams()
    populate_league_members()
    for year in range(2015, 2023):
        populate_matchups(year)
        populate_draft_info(year)
        populate_player_meta(year)
        populate_player_projections(year)