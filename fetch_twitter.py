from twitter import *
import json
import psycopg2

settings = json.load(open('settings.json', 'r'))
twitter_settings = settings['twitter']

def paged_query(endpoint, beginning_max_id, since_id):
    max_id = beginning_max_id
    while True:
        kwargs = dict(screen_name="", count=200, include_rts=1)
        if max_id:
            kwargs['max_id'] = max_id
        if since_id:
            kwargs['since_id'] = since_id
        tweets = endpoint(**kwargs)
        if len(tweets) == 0:
            break
        for tweet in tweets:
            yield tweet
            if not max_id:
                max_id = tweet['id']
            max_id = min(tweet['id'], max_id) - 1

def do_update(endpoint, table_name):
    max_id = None
    since_id = None
    count = 0

    cur.execute("SELECT MAX(tweet_id) FROM %s;" % table_name)
    row = cur.fetchone()
    if row and row[0]:
        since_id = int(row[0])
        print "Most recent %s was %s" % (table_name, since_id)

    for tweet in paged_query(endpoint, max_id, since_id):
        cur.execute("SELECT tweet_id FROM %s WHERE tweet_id=%%s" % table_name, [tweet['id_str']])
        row = cur.fetchone()
        if row:
            print "Skipping %s %s because I already know about it" % (table_name, row[0])
            continue
        else:
            cur.execute("INSERT INTO %s (data, created_at, tweet_id) VALUES (%%s, %%s, %%s)" % table_name, [
                json.dumps(tweet),
                tweet['created_at'],
                tweet['id_str']
            ])
            print "Inserted %s %s" % (table_name, tweet['id_str'])
            count += 1
    return count

if __name__ == '__main__':
    t = Twitter(
        auth=OAuth(twitter_settings['access_token'], twitter_settings['access_token_secret'],
                   twitter_settings['client_id'], twitter_settings['client_secret'])
    )

    conn = psycopg2.connect(settings['database'])
    cur = conn.cursor()

    tweets = do_update(t.statuses.user_timeline, 'source.twitter_tweets')
    mentions = do_update(t.statuses.mentions_timeline, 'source.twitter_mentions')
    favorites = do_update(t.favorites.list, 'source.twitter_favorites')

    conn.commit()

    print "Inserted %s tweets, %s mentions, and %s favorites." % (tweets, mentions, favorites)