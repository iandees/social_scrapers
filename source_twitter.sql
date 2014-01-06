CREATE TABLE source.twitter_favorites
(
  data json,
  created_at timestamp with time zone,
  tweet_id bigint
);

CREATE TABLE source.twitter_mentions
(
  data json,
  created_at timestamp with time zone,
  tweet_id bigint
);

CREATE TABLE source.twitter_tweets
(
  data json,
  created_at timestamp with time zone,
  tweet_id bigint
);