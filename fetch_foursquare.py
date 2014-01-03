import foursquare
import json
import psycopg2

settings = json.load(open('settings.json', 'r'))
fs_settings = settings['foursquare']

def setup_foursquare_client():
    # Construct the client object
    client = foursquare.Foursquare(client_id=fs_settings['client_id'], client_secret=fs_settings['client_secret'], redirect_uri='http://localhost:8000')

    if 'user_access_token' not in fs_settings:
        # Build the authorization url for your app
        auth_uri = client.oauth.auth_url()

        print "Go to %s" % auth_uri
        code = raw_input("Enter the code here: ")
        print "You entered \'%s\'" % code

        # Interrogate foursquare's servers to get the user's access_token
        user_access_token = client.oauth.get_token(code)
        print "User access token was %s" % user_access_token

        # Apply the returned access token to the client
        client.set_access_token(user_access_token)
    else:
        client.set_access_token(fs_settings['user_access_token'])

    return client

def checkins_since(client, epoch_time=None):
    offset = 0
    while(True):
        params = {'limit': 250, 'offset': offset}
        if epoch_time:
            params['afterTimestamp'] = epoch_time
        checkins = client.users.checkins(params=params)
        # Yield out each checkin
        for checkin in checkins['checkins']['items']:
            yield checkin
        # Determine if we should stop here or query again
        offset += len(checkins['checkins']['items'])
        if (offset >= checkins['checkins']['count']) or (len(checkins['checkins']['items']) == 0):
            # Break once we've processed everything
            break

if __name__ == '__main__':
    fs_client = setup_foursquare_client()

    conn = psycopg2.connect(settings['database'])
    cur = conn.cursor()

    # Find most recent checkin
    cur.execute("SELECT EXTRACT(EPOCH FROM created_at) FROM source.foursquare ORDER BY created_at DESC LIMIT 1")
    most_recent_timestamp = cur.fetchone()
    most_recent_timestamp = int(most_recent_timestamp[0]) if most_recent_timestamp else most_recent_timestamp

    print "Most recent checkin is at %s" % most_recent_timestamp

    rows = 0
    for checkin in checkins_since(fs_client, most_recent_timestamp):
        cur.execute("SELECT checkin_id FROM source.foursquare WHERE checkin_id=%s", [checkin['id']])
        if cur.fetchone():
            print "Skipping %s because I already know it" % checkin['id']
            continue
        cur.execute("INSERT INTO source.foursquare (data, checkin_id, created_at) VALUES (%s, %s, (SELECT timestamptz 'epoch' + %s * interval '1 second'))", [json.dumps(checkin), checkin['id'], checkin['createdAt']])
        rows += 1

    conn.commit()

    print "Inserted %s new checkins." % rows