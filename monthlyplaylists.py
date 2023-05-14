import sqlite3
from sqlite3 import Error
import pandas as pd
import requests
import json
import datetime


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
    

def select_counts(conn, month):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param month: the month to filter on
    :return: rows from the query result
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(full_song_name), song_name, artist_name, spotify_song_id  FROM trackssentiment t WHERE played_at LIKE '%-{}-%' GROUP BY full_song_name ".format(month))

    rows = cur.fetchall()

    return rows

def extract_ids(dataframe, number_of_times_played):
    """
    Extracts id of the songs that were played more times that the given number
    :param dataframe: the dataframe to filter on
    :param number of times played: number of times played to filter on
    :return: list of song ids
    """
    song_ids = []
    for _, row in dataframe.iterrows():
        if row["count"] > number_of_times_played:
            song_ids.append(row["spotify_song_id"])
            print(row["spotify_song_id"])
    return song_ids

def API_request():
    refresh_token = "***********"
    base_64 = "**********="

    query = "https://accounts.spotify.com/api/token"

    response = requests.post(query,
                            data={"grant_type": "refresh_token",
                                "refresh_token": refresh_token},
                            headers={"Authorization": "Basic " + base_64})

    response_json = response.json()
    print(response_json)
    return response_json["access_token"]

def check_playlist(token):
    USER_ID = "223e6vdbktpzkrwn6y6yqp3ay"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    SPOTIFY_API_PLAYLISTS_ENDPOINT = "https://api.spotify.com/v1/users/{user_id}/playlists"
    
    #Define the names of the months in spanish with the first letter in uppercase
    MONTH_NAMES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
    }

    # Get the current month and year
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year
    playlist_name = f"{MONTH_NAMES[current_month]} {current_year}"
    headers = {
    "Authorization": f"Bearer {token}",
    }
    params = {
        "limit": 50,  # Maximum number of playlists to retrieve
    }
    response = requests.get(SPOTIFY_API_PLAYLISTS_ENDPOINT.format(user_id=USER_ID), headers=headers, params=params)

    playlist_id = None
    for playlist in response.json()["items"]:
        if playlist["name"] == playlist_name:
            playlist_id = playlist["id"]
            break
    
    # If the playlist doesn't exist, create it
    if not playlist_id:
        data = {
            "name": playlist_name,
            "description": f"Playlist created on {now.strftime('%d %B %Y')} by a Python script",
            "public": False,  # Change to True if you want the playlist to be public
        }
        response = requests.post(SPOTIFY_API_PLAYLISTS_ENDPOINT.format(user_id=USER_ID), headers=headers, json=data)
        playlist_id = response.json()["id"]
        print(f"Created playlist '{playlist_name}' with ID {playlist_id}")
    else:
        print(f"Found playlist '{playlist_name}' with ID {playlist_id}")

    return playlist_id


def add_to_playlist(token, playlist_id, song_ids):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    # Get the list of tracks already in the playlist
    response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
    existing_track_ids = [item['track']['id'] for item in response.json()['items']]
    # Filter out the song IDs that are already in the playlist
    song_ids_to_add = [id for id in song_ids if id not in existing_track_ids]
    # Make the API call to add the remaining songs to the playlist
    if len(song_ids_to_add) > 0:
        data = {
            "uris": [f"spotify:track:{id}" for id in song_ids_to_add]
        }        
        response = requests.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", data=json.dumps(data), headers=headers)
        print(response.json())
    else:
        print("All songs are already in the playlist.")


def main():
    database = r"C:\Users\Andrea\Downloads\Spotify\trackssentiment.sqlite"

    # create a database connection
    conn = create_connection(database)
    with conn:
        print("Query count of songs played in the month")
        #Extract the current month
        month = datetime.datetime.now().strftime("%m")
        print(month)
        select_counts(conn, month)
        df = pd.DataFrame(select_counts(conn, month), columns = ["count", "song_name", "artist_name", "spotify_song_id"])
        print(df)
        #times_played = int(input("Enter number of times played: "))
        times_played = 8
        song_ids = extract_ids(df, times_played)
        print(song_ids)
        token = API_request()
        playlist_id = check_playlist(token) 
        add_to_playlist(token, playlist_id, song_ids)

if __name__ == '__main__':
    main()
