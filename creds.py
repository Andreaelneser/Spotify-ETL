''' THIS IS HOW WE GET THE CREDENTIALS. REMEMBER TO GET YOUR OWN CLIENT ID AND CLIENT SECRET
https://accounts.spotify.com/authorize?response_type=code&client_id=****************&redirect_uri=http://localhost/8888/callback&scope=user-read-recently-played
50b5d7d27ccf4be9b5692e82e90e7237:0b057df10ebc4d59b8400ad3b4c6d85b

curl -H "Authorization: ************************=" -d grant_type=authorization_code -d code=************* -d redirect_uri=http://localhost:7777/callback https://accounts.spotify.com/api/token


curl -d client_id=******************** -d client_secret=**************** -d grant_type=authorization_code -d code=*********** -d redirect_uri=http://localhost/8888/callback https://accounts.spotify.com/api/token 
'''


import requests
import json

refresh_token = "**************************" 
base_64 = "****************=" 

query = "https://accounts.spotify.com/api/token"

response = requests.post(query,
                        data={"grant_type": "refresh_token",
                            "refresh_token": refresh_token},
                        headers={"Authorization": "Basic " + base_64})

response_json = response.json()
print(response_json)
