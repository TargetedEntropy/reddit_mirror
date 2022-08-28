from config import Config
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Table,
    Column,
    Integer,
    MetaData,
    DateTime,
    create_engine,
    String,
    Text,
)

metadata = MetaData()
subreddit_posts = Table(
    "subreddit_posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", String),
    Column("post_title", Text),
    Column("post_url", String),
    Column("subreddit_name", String),
    Column("post_datetime", DateTime),
)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()


def does_post_exist(post_id: str):
    cursor = connection.execute(f"SELECT post_id from subreddit_posts where post_id = '{post_id}'")
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False


async def insert_post_to_db(submission):
    ins = subreddit_posts.insert().values(
        post_id=submission.id,
        post_title=submission.title,
        post_url=submission.url,
        subreddit_name=submission.subreddit.display_name,
    )
    try:
        connection.execute(ins)
    except Exception as e:
        print(f"Failed: {e} \nQ:{ins}")
