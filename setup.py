import sqlite3
import yaml


def create_db():
    db_info = yaml.safe_load(open("config/db.yml"))

    conn = sqlite3.connect(db_info["database_name"])
    c = conn.cursor()

    try:
        c.execute("drop table tweet_data")
    except:
        print("tweet_data already dropped")
        pass

    cmd = "CREATE TABLE tweet_data (id TEXT, text TEXT, created_at TEXT, fav_count INTEGER, lang TEXT, retweet_count INTEGER, coordinates TEXT, sentiment REAL)"
    c.execute(cmd)

    conn.commit()

    conn.close()


if __name__ == "__main__":
    create_db()
