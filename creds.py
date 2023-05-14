'''
https://accounts.spotify.com/authorize?response_type=code&client_id=baf8a75cefa545da844710e4b198b03f&redirect_uri=http://localhost/8888/callback&scope=user-read-recently-played
50b5d7d27ccf4be9b5692e82e90e7237:0b057df10ebc4d59b8400ad3b4c6d85b

curl -H "Authorization: NTBiNWQ3ZDI3Y2NmNGJlOWI1NjkyZTgyZTkwZTcyMzc6MGIwNTdkZjEwZWJjNGQ1OWI4NDAwYWQzYjRjNmQ4NWI=" -d grant_type=authorization_code -d code=AQB-sEfA0wFAAVc5HT2FISRzf8eBEvG0ES73iBq8jcU5Lss_1EvVpd9wKXFHpAMOUWGRbogV0iMr43hRy4zLNOQTe2UPnsViQsyQvSFtP3UyGFoqLbI1ssBMjItBhBCM9iLPZn7xVOUZ8HRU2rt8pqZgCkUlv5KGRdgDGkPmveNPsK1bL6ylvTlvSQZal_Gg94X3KUxE69cVVdqq930NjdT_IPBWndi-cciLPHk-JgALFH9icKYUn422PKCTTlDpHsMrfLFxEQY7TIlk2gsB0A -d redirect_uri=http://localhost:7777/callback https://accounts.spotify.com/api/token


curl -d client_id=baf8a75cefa545da844710e4b198b03f -d client_secret=b21af1278d3543fa9cf5d475bcfa2ee4 -d grant_type=authorization_code -d code=AQCY9yl1yue4pvc6wYDCAKumID6OFrNXZyQRKCQsUdI9Hq8SlRpHFjrF57CwoomBj4WnFADfPFkXjLFmS72P_M29hk0Lo_duOWHFCWHKA7s-w8oXEMT-h99gT_r9cszD3A2s5UOnnEQ2Y2VFXHDOup1XxqCpYisP2WJemettCi_2UT-qRN_LxnrDUXbjytJjY2EZc3XNQ2gW43jxYA -d redirect_uri=http://localhost/8888/callback https://accounts.spotify.com/api/token 
'''


import requests
import json

refresh_token = "AQCNJha_wRu2of5j_IPFSBf7UdrNhPWneFt7Kaa78vOort7J6euFT0CtgG3rH8AhgCcL6cFSMBrnj-nfolkO1ImOhDMWFP_74TxXKxDoYwiP_sGPUedWYeQdCC8mmKsJRxQ" 
base_64 = "YmFmOGE3NWNlZmE1NDVkYTg0NDcxMGU0YjE5OGIwM2Y6YjIxYWYxMjc4ZDM1NDNmYTljZjVkNDc1YmNmYTJlZTQ=" 

query = "https://accounts.spotify.com/api/token"

response = requests.post(query,
                        data={"grant_type": "refresh_token",
                            "refresh_token": refresh_token},
                        headers={"Authorization": "Basic " + base_64})

response_json = response.json()
print(response_json)