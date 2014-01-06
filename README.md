social_scrapers
===============

Various Python scripts to scrape sites that store data about you.

## Setup

Most of the scraper scripts in this repo use OAuth2 to access an API of some sort that gives access to data you generate in some way. You'll need to gather some information to make that OAuth2 process work and create the Postgres database schema to store the data in.

After you clone this repo, start by creating a virtual environment in which you'll load all your dependencies:

    git clone git@github.com:iandees/social_scrapers.git
    mkvirtualenv --no-site-packages social_scrapers

### Twitter

At this point the Twitter scraper will save your tweets, your favorites, and tweets that mention you.

    # Activate the virtual environment you created above
    workon social_scrapers
    # Install the dependencies
    pip install -r requirements.twitter.txt
    
Make a copy of the `settings.json.example` file ane name it `settings.json`. Go to [this website](https://dev.twitter.com/apps/new) to create a new Twitter "application". This will give you a Consumer Key and a Consumer Secret. At the bottom of your new app's page, click the button to generate an Access Token. This will give you an Access Token and Access Token Secret. Put these four values in the `settings.json` file's `twitter` section.

Next you need to create the Postgres database tables to store the data. Once you create the Postgres database, create a Schema named "source" and run the `source_twitter.sql` file to create the three tables.

Finally, you should be able to run the scraper script to fetch as much information as you can.

    python fetch_twitter.py
    
Note that Twitter only returns the most recent [3200 tweets](https://dev.twitter.com/docs/api/1/get/statuses/user_timeline) from its API, so if you have more tweets than that you won't get them all with this method (you can [request an archive](https://twitter.com/settings/account) of all your tweets, but working with that archive is not supported here yet). If you run the `fetch_twitter.py` script again it will only fetch new tweets/mentions/favorites.

### Foursquare

The Foursquare scraper will save all your checkins.

    # Activate the virtual environment you created above
    workon social_scrapers
    # Install the dependencies
    pip install -r requirements.foursquare.txt
    
...

### Moves App

The Moves App scraper will save the details of your timeline.

    # Activate the virtual environment you created above
    workon social_scrapers
    # Install the dependencies
    pip install -r requirements.movesapp.txt
    
...

### Picasa / Google+ Auto-Backup

The Picasa scraper will save links to your auto-upload pictures and videos along with the associated metadata.

    # Activate the virtual environment you created above
    workon social_scrapers
    # Install the dependencies
    pip install -r requirements.picasaweb.txt
    
...

## TODO

I'd like to support these pieces of the puzzle at some point:

- OpenStreetMap edits
- Ventra bus/train trips
- Fitbit steps/sleep
