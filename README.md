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

Make a copy of the `settings.json.example` file (or use the one you created above) ane name it `settings.json`. Go to [this website](https://foursquare.com/developers/register) to create a new Foursquare "application". This will give you a Consumer Key and a Consumer Secret. Put these two values in the `settings.json` file's `foursquare` section.

Next you need to create the Postgres database tables to store the data. Once you create the Postgres database, create a Schema named "source" and run the `source_foursquare.sql` file to create the required table.

With your app and database created, we'll run the fetch script once to do the OAuth work required to let the script do work on behalf of your account.

    python fetch_foursquare.py

It will ask you to click on a URL, which will open a Foursquare authorization page in your browser. When you approve the application's access to your account, you will be redirected to a page that fails to load, but the important part is in your browser's address bar. Look for `code=` and copy the stuff following it. Paste that code into console at the script's prompt and hit enter. It will proceed to grab all of your foursquare checkins and put them in the database.

### Moves App

The Moves App scraper will save the details of your timeline.

    # Activate the virtual environment you created above
    workon social_scrapers
    # Install the dependencies
    pip install -r requirements.movesapp.txt

Make a copy of the `settings.json.example` file (or use the one you created above) ane name it `settings.json`. Go to [this website](https://dev.moves-app.com/apps/new) to create a new Moves "application". This will give you a Consumer Key and a Consumer Secret. Put these two values in the `settings.json` file's `movesapp` section.

Next you need to create the Postgres database tables to store the data. Once you create the Postgres database, create a Schema named "source" and run the `source_movesapp.sql` file to create the required table.

With your app and database created, we'll run the fetch script once to do the OAuth work required to let the script do work on behalf of your account.

    python fetch_movesapp.py

It will ask you to click on a URL, which will open a Move authorization page in your browser. You will be asked to enter a code into your mobile phone to approve the app. When you approve the application's access to your account, you will be redirected to a page that says the authentication is complete. It will proceed to grab all of your timeline and put it in the database.

### Picasa / Google+ Auto-Backup

The Picasa scraper will save links to your auto-upload pictures and videos along with the associated metadata (it won't actually download the photos, though).

    # Activate the virtual environment you created above
    workon social_scrapers
    # Install the dependencies
    pip install -r requirements.picasaweb.txt

Make a copy of the `settings.json.example` file (or use the one you created above) ane name it `settings.json`. Go to [this website](https://cloud.google.com/console#/project) to create a new Google Developer "application". Click "Create Project", give it a name, and click "Create". After you create the application, click its entry in the list and browse to the "APIs & Auth" > "Credentials" section. Click "Create New Client ID". This will give you a Client ID and a Client Secret. Put these two values in the `settings.json` file's `picasaweb` section.

Next you need to create the Postgres database tables to store the data. Once you create the Postgres database, create a Schema named "source" and run the `source_picasaweb.sql` file to create the required table.

With your app and database created, we'll run the fetch script once to do the OAuth work required to let the script do work on behalf of your account.

    python fetch_picasa.py

It will ask you to click on a URL, which will open a Move authorization page in your browser. You will be asked to approve access to your Picasa photos. When you approve the application's access to your account, you will be redirected to a page that says the authentication is complete. It will proceed to grab all of your photos and put their information in the database.

## TODO

I'd like to support these pieces of the puzzle at some point:

- OpenStreetMap edits
- Ventra bus/train trips
- Fitbit steps/sleep
