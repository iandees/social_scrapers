from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from oauth2client.file import Storage
import argparse
import httplib2
from urllib import urlencode
import json
import psycopg2
import pprint
import sys
import datetime

settings = json.load(open('settings.json', 'r'))
moves_settings = settings['movesapp']

def setup_movesapp_credentials(flags):
    storage = Storage('moves_credentials.storage')

    credentials = storage.get()

    if not credentials:
        flow = OAuth2WebServerFlow(client_id=moves_settings['client_id'],
                                   client_secret=moves_settings['client_secret'],
                                   scope='activity location',
                                   auth_uri='https://api.moves-app.com/oauth/v1/authorize',
                                   token_uri='https://api.moves-app.com/oauth/v1/access_token',
                                   revoke_uri=None,
                                   response_type='code')
        credentials = tools.run_flow(flow, storage, flags)

    if credentials.access_token_expired:
        print "Access token is expired. Refreshing."
        credentials.refresh(httplib2.Http())
        storage.put(credentials)

    return credentials

def movesapp_profile(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    (response, content) = http.request('https://api.moves-app.com/api/v1/user/profile')
    if response.status == 200:
        json_obj = json.loads(content)
        return json_obj
    else:
        # Most likely a problem with authentication
        print content
        return None

def storyline_for(credentials, date, etag=None):
    http = httplib2.Http()
    http = credentials.authorize(http)

    qwargs = {
        'trackPoints': 'true'
    }
    url = 'https://api.moves-app.com/api/v1/user/storyline/daily/%s?%s' % (date.strftime('%Y%m%d'), urlencode(qwargs))

    headers = {}
    if etag:
        headers['If-None-Match'] = etag

    (response, content) = http.request(url, headers=headers)

    if response.status == 200:
        # Since we're asking for trackPoints=true, this will always return one day in the array
        return (json.loads(content)[0], response.get('etag'))
    elif response.status == 304:
        # Etag was specified and nothing changed, so content will be empty
        return (None, etag)
    else:
        print content
        return (None, None)

def days_since(start_date):
    the_date = start_date
    while True:
        yield the_date
        the_date += datetime.timedelta(days=1)
        if the_date > datetime.date.today():
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    flags = parser.parse_args()
    credentials = setup_movesapp_credentials(flags)

    profile = movesapp_profile(credentials)
    first_date = datetime.datetime.strptime(profile['profile']['firstDate'], '%Y%m%d').date()
    print "Hello user %s, your first date of data was %s." % (profile['userId'], first_date.strftime('%x'))

    conn = psycopg2.connect(settings['database'])
    cur = conn.cursor()

    updates = 0
    inserts = 0
    # Go back a week to catch when the timeline data gets modified
    for date in days_since(datetime.date.today() - datetime.timedelta(days=7)):
        cur.execute("SELECT day,etag FROM source.movesapp WHERE day=%s", [date.strftime('%Y%m%d')])
        row = cur.fetchone()
        etag = None
        if row:
            print "Already know about date %s, so checking for updates." % row[0]
            etag = row[1]

        (storyline, response_etag) = storyline_for(credentials, date, etag)

        if (storyline is None) and (response_etag is not None):
            print "Date %s has not changed. Skipping insert." % (row[0])
            continue
        elif row and (response_etag != etag):
            print "Date %s has changed. Updating existing data." % (row[0])
            cur.execute("UPDATE source.movesapp SET data=%s, etag=%s WHERE day=%s", [
                json.dumps(storyline),
                response_etag,
                storyline['date']
            ])
            print "Updated %s" % storyline['date']
            updates += 1
        else:
            cur.execute("INSERT INTO source.movesapp (data, day, etag) VALUES (%s, %s, %s)", [
                json.dumps(storyline),
                storyline['date'],
                response_etag
            ])
            print "Inserted %s" % storyline['date']
            inserts += 1

    conn.commit()

    print "Inserted %s new storyline days and updated %s existing ones." % (inserts, updates)