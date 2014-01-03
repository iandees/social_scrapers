from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from oauth2client.file import Storage
import argparse
import httplib2
from urllib import urlencode
import json
import psycopg2

settings = json.load(open('settings.json', 'r'))
goog_settings = settings['google']

def setup_picasa_credentials(flags):
    storage = Storage('goog_credentials.storage')

    credentials = storage.get()

    if not credentials:
        flow = OAuth2WebServerFlow(client_id=goog_settings['client_id'],
                                   client_secret=goog_settings['client_secret'],
                                   scope='https://picasaweb.google.com/data/',
                                   redirect_uri='http://localhost/auth_return')
        credentials = tools.run_flow(flow, storage, flags)

    if credentials.access_token_expired:
        print "Access token is expired. Refreshing."
        credentials.refresh(httplib2.Http())
        storage.put(credentials)

    return credentials

def setup_picasa_instant_upload_album_id(credentials):
    if 'album_id' in goog_settings:
        return goog_settings['album_id']
    else:
        http = httplib2.Http()
        http = credentials.authorize(http)
        (response, content) = http.request('https://picasaweb.google.com/data/feed/api/user/default?alt=json', headers={'GData-Version': '2'})
        if response.status == 200:
            json_obj = json.loads(content)
            for entry in json_obj['feed']['entry']:
                album_type = entry.get('gphoto$albumType', {}).get('$t')
                if album_type == 'InstantUpload':
                    print "Found album '%s' with InstantUpload type. Set the 'album_id' key to this value in your settings." % entry['gphoto$id']['$t']
                    return entry['gphoto$id']['$t']
                    break
            print "Couldn't find the InstantUpload album."
            return None
        else:
            # Most likely a problem with authentication
            print content
            return None

def photos_since(credentials, album_id, since_time=None):
    http = httplib2.Http()
    http = credentials.authorize(http)

    offset = 1
    while True:
        # The fields= stuff comes from https://code.google.com/p/gdata-issues/issues/detail?id=138#c14
        # (The only way to query by time)
        # The imgmax stuff comes from https://developers.google.com/picasa-web/docs/2.0/reference?csw=1#Parameters
        # (Without imgmax=d they don't include a reference to the original image)
        qwargs = {
            'alt': 'json',
            'imgmax': 'd',
            'max-results': 250,
            'start-index': offset
        }
        if since_time:
            qwargs['fields'] = 'entry[xs:dateTime(updated)>=xs:dateTime(\'%s\')]' % since_time
        url = 'https://picasaweb.google.com/data/feed/api/user/default/albumid/%s?%s' % (album_id, urlencode(qwargs))
        (response, content) = http.request(url, headers={'GData-Version': '2'})

        if response.status == 200:
            json_obj = json.loads(content)

            feed_entries = json_obj['feed'].get('entry', [])
            for entry in feed_entries:
                yield entry
            offset += len(feed_entries)
            if len(feed_entries) == 0:
                break
        else:
            print content
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    flags = parser.parse_args()
    credentials = setup_picasa_credentials(flags)

    instant_upload_album_id = setup_picasa_instant_upload_album_id(credentials)

    conn = psycopg2.connect(settings['database'])
    cur = conn.cursor()

    # Find most recent photo
    cur.execute("SELECT to_char(created_at at time zone 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"') FROM source.picasaweb ORDER BY created_at DESC LIMIT 1")
    most_recent_timestamp = cur.fetchone()
    most_recent_timestamp = most_recent_timestamp[0] if most_recent_timestamp else most_recent_timestamp

    print "Most recent photo was at %s" % most_recent_timestamp

    rows = 0
    for photo in photos_since(credentials, instant_upload_album_id, most_recent_timestamp):
        cur.execute("SELECT photo_id FROM source.picasaweb WHERE photo_id=%s", [photo['gphoto$id']['$t']])
        if cur.fetchone():
            print "Skipping %s because I already know it" % photo['gphoto$id']['$t']
            continue
        cur.execute("INSERT INTO source.picasaweb (data, photo_id, created_at, thumbnail_url) VALUES (%s, %s, %s, %s)", [
            json.dumps(photo),
            photo['gphoto$id']['$t'],
            photo['published']['$t'],
            photo['media$group']['media$thumbnail'][-1]['url']
        ])
        print "Inserted %s" % photo['gphoto$id']['$t']
        rows += 1

    conn.commit()

    print "Inserted %s new photos." % rows