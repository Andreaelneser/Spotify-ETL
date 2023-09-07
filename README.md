# Spotify-project
This repository contains a project I did using the Spotify API to extract data from my recently played songs into a database. Then I extract the data from the database and using the API get the information for each song so I can make a more indeep analysis and recommendations. And also create a monthly playlist with the most played songs.

The project is in progress.

* main.py has the ETL. It first requests the access token with the function API(). Then the API is consumed and the data from the last 50 played songs its retrieved with https://api.spotify.com/v1/me/player/recently-played?after{time}&limit=50. From there, a list is set for each column or variable. Then each song is itered and the info for all the columns is extracted, including the lyrics from genius (which needs another API). Then the duration is transformed from ms to min and finally the data is loaded to a SQLite database
