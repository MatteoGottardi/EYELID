import sys
from Utils import load_csv, cleanData, byteFile
from index import so_byte_index
from wigleGet import search_area_query, get_auth, set_auth, push_request, write_csv


# get wifi data from WIGLE.net

if len(sys.argv) < 6 or len(sys.argv) > 8:
    print('\nParameters: dir_path lat_up long_up lat_down long_down [from_date is optional] [search_after is optional]\n')
    exit(-1)

dir_path = sys.argv[1]
lat_up = float(sys.argv[2])
long_up = float(sys.argv[3])
lat_down = float(sys.argv[4])
long_down = float(sys.argv[5])

if len(sys.argv) < 7:
    from_date = '20010101000001'
else:
    from_date = int(sys.argv[6])

if len(sys.argv) < 8:
    search_after = 0
else:
    search_after = int(sys.argv[7])

api_name = "yourusetoken"
api_token = "yourapitoken"
file_path = dir_path + 'WIGLE_data.csv'

auth = get_auth(api_name, api_token)
query = search_area_query(lat_up, long_up, lat_down, long_down, from_date, search_after)

n = 1  # counter
res = None

accepted, response = set_auth(auth)
if accepted:
    while (search_after is not None) and (n == 1 or res['success']):
        query = search_area_query(lat_up, long_up, lat_down, long_down, from_date, search_after)
        r = push_request(query, auth)
        res = r.json()
        search_after = res['search_after']
        if res['success']:
            print('%d.\tRequest succeded\tsearch_after: %s' % (n, res['search_after']))
            n += 1
            write_csv(res, file_path)
        else:
            print('\nSomething gone wrong')
            print(r.json())

    # clean data and create index

    df = load_csv(file_path)
    cleanData(df, dir_path + 'WIGLE_filtered.csv', ['BSSID', 'LAT', 'LONG'])
    byteFile(dir_path + 'WIGLE_filtered.csv', dir_path + 'wifiData.bin')

    so_byte_index(dir_path + 'wifiData.bin', dir_path + 'index.bin', 14, 256)

else:
    print('Not authorized.')
    print(response.text)


