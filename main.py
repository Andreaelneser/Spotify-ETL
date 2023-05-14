import sqlalchemy
from sqlalchemy.orm import sessionmaker
import pandas as pd
import requests
import json
from datetime import datetime
import datetime 
import sqlite3
import lyricsgenius
import time
import random
from textblob import TextBlob
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


DATABASE_LOCATION = "sqlite:///trackssentiment.sqlite"
USER_ID = "******"

def Transform(df):
    #duration_ms to minutes
    df["duration_ms"] = df["duration_ms"] / 60000
    #rename columns
    df.rename(columns={"duration_ms" : "duration_min"}, inplace=True)
    return df

def API():
    refresh_token = "***************"
    base_64 = "*********="

    query = "https://accounts.spotify.com/api/token"

    response = requests.post(query,
                            data={"grant_type": "refresh_token",
                                "refresh_token": refresh_token},
                            headers={"Authorization": "Basic " + base_64})

    response_json = response.json()
    print(response_json)
    
    return response_json["access_token"]


TOKEN = API()

if __name__ == "__main__":

    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=TOKEN)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after{time}&limit=50".format(time=yesterday_unix_timestamp), headers=headers)

    print(r.status_code)

    data = r.json()

    song_names = []
    spotify_song_ids = []
    artist_names = []
    played_at_list = []
    timestamps = []
    release_date = []
    album_name = []
    popularity = []
    duration_ms = []
    song_lyrics = []
    sentiment = []
    context = []
    context_type = []

    previous_id = None

    for song in data["items"]:
        song_id = song["track"]["id"]
        if song_id == previous_id:
            continue  # skip this song if it's the same as the previous one
        previous_id = song_id
        song_names.append(song["track"]["name"])
        spotify_song_ids.append(song["track"]["id"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])
        release_date.append(song["track"]["album"]["release_date"])
        album_name.append(song["track"]["album"]["name"])
        popularity.append(song["track"]["popularity"])
        duration_ms.append(song["track"]["duration_ms"])
        if song.get("context") is not None:
            context.append(song["context"]["external_urls"]["spotify"])
            context_type.append(song["context"]["type"])
        else:
            context.append("PC")
            context_type.append("PC")
        genius = lyricsgenius.Genius('JcjJTXHKBjEUT0v4bfSGmEPMjISnDpunjTlBmXKsyl6e0rsrm61PxrxXgiF_D_Up')
        lyrics = genius.search_song(song_names[-1], artist_names[-1])
        if lyrics:
            print("Lyrics found!")
            song_lyrics.append(lyrics.lyrics)
        else:
            print("No lyrics found.")
            song_lyrics.append(None)

        # Add a delay to avoid hitting API rate limits
        time.sleep(5+ random.randint(0, 10))

        sentiment.append(TextBlob(song_lyrics[-1]).sentiment.polarity if song_lyrics[-1] is not None else None)
        


    song_dict = {
        "song_name" : song_names,
        "spotify_song_id" : spotify_song_ids,
        "artist_name" : artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps,
        "release_date" : release_date,
        "album_name" : album_name,
        "popularity" : popularity,
        "duration_ms" : duration_ms, 
        "context" : context,
        "context_type" : context_type,
        "song_lyrics" : song_lyrics,
        "sentiment" : sentiment
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "spotify_song_id", "artist_name", "played_at", "timestamp", "release_date", "album_name", "popularity", "duration_ms", "context", "context_type", "song_lyrics", "sentiment"])

    #Transform
    transformed = Transform(song_df)
    print(transformed)

    #Load
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect(r"C:\Users\Andrea bb\Downloads\Spotify\trackssentiment.sqlite")
    cursor = conn.cursor()

    sql_query = """    
    CREATE TABLE IF NOT EXISTS trackssentiment(
        song_name VARCHAR(200),
        spotify_song_id VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        release_date VARCHAR(200),
        album_name VARCHAR(200),
        popularity VARCHAR(200),
        duration VARCHAR(200),
        context VARCHAR(200),
        context_type VARCHAR(200),
        song_lyrics TEXT,
        sentiment VARCHAR(200),
        full_song_name TEXT AS (song_name || ' - ' || artist_name),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_query)
    print("Opened database successfully")

    for index, row in transformed.iterrows():
        played_at = row['played_at']
        #print(row)
        if cursor.execute(f"SELECT COUNT(*) FROM trackssentiment WHERE played_at=?", (played_at,)).fetchone()[0] == 0:
            sql_insert = """
            INSERT INTO trackssentiment (
                song_name, spotify_song_id, artist_name, played_at, timestamp, release_date, album_name, popularity, duration, context, context_type, song_lyrics, sentiment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            values = (
                row['song_name'], row['spotify_song_id'], row['artist_name'], row['played_at'], row['timestamp'],
                row['release_date'], row['album_name'], row['popularity'], row['duration_min'], row['context'], row['context_type'], row['song_lyrics'], row['sentiment'] 
            )
            cursor.execute(sql_insert, values)
            conn.commit()

            print(f"New row added for played_at: {played_at}")
        else:
            print(f"Data already exists for played_at: {played_at}")

    conn.close()
    print("Close database successfully")
    

