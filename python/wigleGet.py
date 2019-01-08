import requests
from requests.auth import HTTPBasicAuth
import csv
import os


def set_auth(auth):
    header = {'accept': 'application/json'}
    response = requests.get('https://api.wigle.net/api/v2/profile/user', headers=header, auth=auth)
    if response.status_code == 200:
        return True, response
    else:
        return False, response


def get_auth(api_name, api_token):
    return HTTPBasicAuth(api_name, api_token)


def push_request(request, auth):
    return requests.get(request, auth=auth)


def search_area_query(lat_up, long_up, lat_down, long_down, last_updt='20010101000001', search_after=None):
    u = ('https://api.wigle.net/api/v2/network/search?onlymine=false&first=0&'+
         'latrange1=%0.3f&latrange2=%0.3f&longrange1=%0.3f&longrange2=%0.3f&freenet=false&paynet=false&lastupdt=%s'
         % (lat_up, lat_down, long_up, long_down, last_updt))
    if search_after is not None:
        u += '&searchAfter=%s' % search_after
    return u


def write_csv(body, file_path):
    #BSSID, lat, long, lastupdt
    file = csv.writer(open(file_path, "a+", newline=''))

    if os.stat(file_path).st_size == 0:
        file.writerow(['BSSID', 'LAT', 'LONG'])

    for e in body['results']:
        bssid = e['netid'].replace(':', '')
        file.writerow([bssid.lower(), e['trilat'], e['trilong']])
    pass
