import sqlite3
from sqlite3 import Error
import pandas as pd
import base64
import requests
import json 
import time
import random
import numpy as np
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Opened database successfully")
    except Error as e:
        print(e)

    return conn
    

def select_counts(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param month: the month to filter on
    :return: rows from the query result
    """
    cur = conn.cursor()
    cur.execute("SELECT spotify_song_id, song_name, artist_name FROM trackssentiment t")

    rows = cur.fetchall()

    return rows

def extract_ids(dataframe):
    """
    Extracts id of the songs that were played more times that the given number
    :param dataframe: the dataframe to filter on
    :param number of times played: number of times played to filter on
    :return: list of song ids
    """
    song_ids = []
    for _, row in dataframe.iterrows():
            song_ids.append(row["spotify_song_id"])
    return song_ids

def API_call():

    auth_endpoint = "https://accounts.spotify.com/api/token"
    client_id = "50b5d7d27ccf4be9b5692e82e90e7237"
    client_secret = "0b057df10ebc4d59b8400ad3b4c6d85b"

    # Encode the client ID and client secret as base64
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    headers = {
    "Authorization": f"Basic {client_creds_b64.decode()}",
    "Content-Type": "application/x-www-form-urlencoded"}

    # Set the grant type for the token request
    data = {
        "grant_type": "client_credentials"
    }

    # Make the API request to retrieve the access token
    response = requests.post(auth_endpoint, headers=headers, data=data)

    # Parse the JSON response into a Python dictionary
    token_data = response.json()

    # Extract the access token from the token data
    access_token = token_data["access_token"]

    # Print the access token
    print(access_token)

    return access_token

 

def extract_each_song(ids, access_token):

    song_name = []
    spotify_song_ids = []
    artist_name = []
    release_date = []
    popularity = []
    duration_ms = []
    explicit = []
    track_number = []
    album_name = []
    total_tracks = []
    album_type = []
    album_genre = []
    artist_followers = []
    artist_popularity = []
    artist_genre = []
    acousticness = []
    danceability = []
    energy = []
    instrumentalness = []
    liveness = []
    loudness = []
    speechiness = []
    tempo = []
    time_signature = []
    valence = []


    for id in ids:
        track_url = "https://api.spotify.com/v1/tracks/{}".format(id)
        headers = { "Authorization": f"Bearer {access_token}",
                     "Accept": "application/json"}
        r = requests.get(track_url, headers=headers)
        track_data = r.json()

        features_url = "https://api.spotify.com/v1/audio-features/{}".format(id)
        r = requests.get(features_url, headers=headers)
        features_data = r.json()   

        song_name.append(track_data["name"])
        spotify_song_ids.append(track_data["id"])
        artist_name.append(track_data["artists"][0]["name"])
        release_date.append(track_data["album"]["release_date"])
        popularity.append(track_data["popularity"])
        duration_ms.append(track_data["duration_ms"])
        explicit.append(track_data["explicit"])
        track_number.append(track_data["track_number"])
        album_name.append(track_data["album"]["name"])
        total_tracks.append(track_data["album"]["total_tracks"])
        album_type.append(track_data["album"]["album_type"])
        album_genre.append(track_data["album"].get("genres"))
        artist_followers.append(track_data["artists"][0].get("followers", {}).get("total"))
        artist_popularity.append(track_data["artists"][0].get("popularity"))
        artist_genre.append(track_data["artists"][0].get("genres"))
        acousticness.append(features_data["acousticness"])
        danceability.append(features_data["danceability"])
        energy.append(features_data["energy"])
        instrumentalness.append(features_data["instrumentalness"])
        liveness.append(features_data["liveness"])
        loudness.append(features_data["loudness"])
        speechiness.append(features_data["speechiness"])
        tempo.append(features_data["tempo"])
        time_signature.append(features_data["time_signature"])
        valence.append(features_data["valence"])   

        print("Song name: {}".format(track_data["name"]))

    time.sleep(5+ random.randint(0, 10))
    

    infodict = {"song_name": song_name, "spotify_song_id": spotify_song_ids, "artist_name": artist_name, "release_date": release_date, 
                "popularity": popularity, "duration_ms": duration_ms, "explicit": explicit, "track_number": track_number, "album_name": album_name, 
                "total_tracks": total_tracks, "album_type": album_type, "album_genre": album_genre, "artist_followers": artist_followers, "artist_popularity": artist_popularity, 
                "artist_genre": artist_genre, "acousticness": acousticness, "danceability": danceability, "energy": energy, "instrumentalness": instrumentalness, "liveness": liveness, "loudness": loudness, 
                "speechiness": speechiness, "tempo": tempo, "time_signature": time_signature, "valence": valence} 
    
    infodf = pd.DataFrame(infodict, columns=["song_name", "spotify_song_id", "artist_name", "release_date", "popularity", "duration_ms", "explicit", "track_number", "album_name", 
                                             "total_tracks", "album_type", "album_genre", "artist_followers", "artist_popularity", "artist_genre", "acousticness", "danceability", "energy", "instrumentalness", 
                                             "liveness", "loudness", "speechiness", "tempo", "time_signature", "valence"])
    print(infodf)
    
    return infodf

def load_data(infodf, spotify_song_id):
    # Connect to the database
    conn = sqlite3.connect(r"C:\Users\Andrea bb\Downloads\Spotify\trackssentiment.sqlite")
    cursor = conn.cursor()

    # Create a table called "songs_info" if it doesn't already exist
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS songs_info (
            song_name VARCHAR(200),
            spotify_song_id VARCHAR(200),
            artist_name VARCHAR(200),
            release_date DATE,
            popularity INT,
            duration_ms INT,
            explicit BOOLEAN,
            track_number INT,
            album_name VARCHAR(200),
            total_tracks INT,
            album_type VARCHAR(200),
            album_genre VARCHAR(200),
            artist_followers INT,
            artist_popularity INT,
            artist_genre VARCHAR(200),
            acousticness FLOAT,
            danceability FLOAT,
            energy FLOAT,
            instrumentalness FLOAT,
            liveness FLOAT,
            loudness FLOAT,
            speechiness FLOAT,
            tempo FLOAT,
            time_signature INT,
            full_song_name TEXT AS (song_name || ' - ' || artist_name),
            valence FLOAT
        )
    '''
    cursor.execute(create_table_query)
    print("Opened database successfully")

    for index, row in infodf.iterrows():
        spotify_song_id = row['spotify_song_id']
        #print(row)
        if cursor.execute(f"SELECT COUNT(*) FROM songs_info WHERE spotify_song_id=?", (spotify_song_id,)).fetchone()[0] == 0:
            sql_insert = """
            INSERT INTO songs_info (
                song_name, spotify_song_id, artist_name, release_date, popularity, duration_ms, explicit, track_number, album_name, total_tracks, album_type, album_genre, artist_followers, artist_popularity, 
                artist_genre, acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, tempo, time_signature, valence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            values = (
                row['song_name'], row['spotify_song_id'], row['artist_name'], row['release_date'], row['popularity'], row['duration_ms'], row['explicit'], row['track_number'], row['album_name'], row['total_tracks'], 
                row['album_type'], row['album_genre'], row['artist_followers'], row['artist_popularity'], row['artist_genre'], row['acousticness'], row['danceability'], row['energy'], row['instrumentalness'], row['liveness'],
                row['loudness'], row['speechiness'], row['tempo'], row['time_signature'], row['valence']         
            )
            cursor.execute(sql_insert, values)
            conn.commit()

            print(f"New row added for spotify_song_id: {spotify_song_id}")
        else:
            print(f"Data already exists for spotify_song_id: {spotify_song_id}")

    conn.close()
    print("Close database successfully")    




def main():
    database = r"C:\Users\Andrea bb\Downloads\Spotify\trackssentiment.sqlite"

    # create a database connection
    conn = create_connection(database)
    access_token =  API_call()
    with conn:
        select_counts(conn)
        df = pd.DataFrame(select_counts(conn), columns = ["spotify_song_id", "song_name", "artist_name"])
        ids = extract_ids(df)
        infodf = extract_each_song(ids, access_token)
        load_data(infodf, infodf["spotify_song_id"])


if __name__ == '__main__':
    main()