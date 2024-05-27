import requests
import pandas as pd
import sqlite3
import os
from ffl_requests_new import (
    get_player_meta,
    get_player_scores,
    get_matchups,
    get_members,
    get_draft,
)
from loguru import logger


def create_db_connection():
    db_path = os.path.abspath(os.path.join(__file__, "..", "..", "..", "FFLPlayground.db"))
    return sqlite3.connect(db_path)


def drop_all_tables():
    con = create_db_connection()
    for table in ["leaguemembers", "drafts", "matchups", "players", "playerscores", "proteams"]:
        logger.info(f"Dropping {table}")
        con.execute(f"DROP TABLE IF EXISTS {table};")

    con.close()


def insert_as_new_table(df, table_name):
    logger.info(f"Inserting to {table_name}...")
    con = create_db_connection()
    df.to_sql(name=table_name, con=con, index=False, if_exists="append")
    con.close()
    logger.info("Done")


def populate_player_meta(year):
    insert_as_new_table(get_player_meta(year), table_name="players")


def populate_player_projections(year):
    insert_as_new_table(get_player_scores(year), table_name="playerscores")


def populate_proteams():
    df = pd.read_csv(os.path.abspath(os.path.join(__file__, "../..", "..", "data", "proteams.csv")))
    insert_as_new_table(df=df, table_name="proteams")


def populate_matchups(year):
    insert_as_new_table(df=get_matchups(year), table_name="matchups")


def populate_league_members():
    insert_as_new_table(df=get_members(), table_name="leaguemembers")


def populate_draft_info(year):
    insert_as_new_table(df=get_draft(year), table_name="drafts")


if __name__ == "__main__":
    drop_all_tables()
    populate_proteams()
    populate_league_members()
    for year in range(2015, 2024):
        try:
            populate_matchups(year)
        except Exception as e:
            logger.warning(e)

        try:
            populate_draft_info(year)
        except Exception as e:
            logger.warning(e)

        try:
            populate_player_meta(year)
        except Exception as e:
            logger.warning(e)

        # TODO: figure out scores in < 2019
        if year >= 2019:
            try:
                populate_player_projections(year)
            except Exception as e:
                logger.warning(e)

    # Create views
    con = create_db_connection()
    view_path = os.path.abspath(os.path.join(__file__, "..", "..", "sql", "views"))
    for view_file in os.listdir(view_path):
        view_name = view_file.removesuffix(".sql")
        logger.info(f"Creating view {view_name}")
        con.execute(f"DROP VIEW IF EXISTS {view_name};")
        full_path = os.path.join(view_path, view_file)
        with open(full_path, "r") as f:
            view_def = f.read()

        con.execute(view_def)

    con.close()
