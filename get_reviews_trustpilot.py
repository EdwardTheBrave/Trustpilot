import requests
import json
from time import gmtime, strftime

def get_reviews(headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    return response.text

def writeToJSONFile(path, fileName, data):
    filePathNameWExt = '/' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'a') as fp:
        json.dump(data, fp)
        fp.write('\n')

"""Con los siguientes comandos conseguimos el access token para poder contectarnos con la API"""

url = "https://api.trustpilot.com/v1/oauth/oauth-business-users-for-applications/accesstoken"

payload = "grant_type=password&username=<email de un usuario de la empresa con acceso a Trustpilot Business>&password=<contraseña de ese usuario>"
headers = {
    'Authorization': "Basic <API Key + Secret Key de la empresa cifradas en Base64>",
    'Content-Type': "application/x-www-form-urlencoded"
    }

response = requests.request("POST", url, data=payload, headers=headers)

token_json = json.loads(response.text)
token = token_json["access_token"]



"""Ahora procedemos a solicitar todas las valoraciones"""

pre_total = []

url = "https://api.trustpilot.com/v1/private/business-units/<Id de tu empresa o business unit ID>/reviews"
querystring = {token,"perPage":"1", "page":"1", "orderBy":"createdat.desc"}
header = {
    'authorization': "Basic <API Key + Secret Key de la empresa cifradas en Base64>",
    'cache-control': "no-cache",
    }

doNotGetOut = True
i = 1
while doNotGetOut:
    querystring['page'] = i
    query_1 = get_reviews(header, querystring)
    response_json = json.loads(query_1)    
    
    if not response_json['reviews']:
        doNotGetOut = False
    else:        
        pre_total.append(response_json)
        i = i + 1

filename = 'trustpilot_reviews_' + strftime("%a", gmtime())
for i in pre_total:
    writeToJSONFile('home/cloudera/trustpilot', filename, i)