"""Retrieve TWeets, embeddings, and persist in the database."""
import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User


TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(config('BASILICA_KEY'))


def add_twitter_user(name):
    try:
        twitter_user = TWITTER.get_user(name)
    except TweepError:
        return (f"user '{name}' not found", None)
    db_user = User.query.get(twitter_user.id) 
    if db_user: 
        return (f"user name '{name}' id {u[0]} is already in the database", None)
    tweets = twitter_user.timeline(
        count=200, exclude_replies=True, include_rts=False, tweet_mode='extended')
    db_user = User(id=twitter_user.id,
                   name=twitter_user.screen_name, 
                   newest_tweet_id= (tweets[0].id if len(tweets) > 0 else None))
    for tweet in tweets:
        embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
        db_tweet = Tweet(
            id=tweet.id, text=tweet.full_text[:500], embedding=embedding)
        DB.session.add(db_tweet)
        db_user.tweets.append(db_tweet)

    DB.session.add(db_user)
    DB.session.commit()
    return (f"user and their original tweets added to database", db_user)


def get_tweets(name):
    query = DB.select([User]).where(User.name == name)
    rp = DB.session.execute(query)
    u = rp.fetchone()
    if str(type(u)) == "<class 'NoneType'>":
        return (f"User {user} not found", None)
    db_user = User.query.get(u[0]) 
    return (f"user name {name} id {u[0]} tweets", db_user)


def add_or_update_user(username):
    """Add or update a user *and* their Tweets, error if no/private user."""
    try:
        twitter_user = TWITTER.get_user(username)
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, name=username))
        DB.session.add(db_user)
        # We want as many recent non-retweet/reply statuses as we can get
        tweets = twitter_user.timeline(
            count=200, exclude_replies=True, include_rts=False,
            tweet_mode='extended', since_id=db_user.newest_tweet_id)
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        for tweet in tweets:
            # Get embedding for tweet, and store in db
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:500],
                             embedding=embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e
    else:
        DB.session.commit()    

