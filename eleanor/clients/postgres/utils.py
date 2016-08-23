"""Utilities for the eleanor service"""

import json
from datetime import datetime, timedelta

from dateutil.parser import parse as date_parse

from sqlalchemy import distinct, desc, and_
from sqlalchemy.exc import IntegrityError

from eleanor.utils import get_logger
from eleanor.models import models, twitter_models
from eleanor.clients.postgres.client import GetDBSession


logger = get_logger(__name__)


def get_string_from_datetime(dt):
    """When given a datetime object return a ISO 8601 string representation of
    the datetime
    """
    dt_format = "%Y-%m-%dT%H:%M:%S+%z"
    return dt.strftime(dt_format)


def get_tweet_data_by_id(tweet_id):
    """When given a tweet_id returns the tweet data if in the database else
    returns None
    """
    with GetDBSession() as db_session:
        twitterSource = db_session.query(
            twitter_models.TwitterSource
        ).filter(
            twitter_models.TwitterSource.tweet_id == tweet_id
        ).first()
        if not twitterSource:
            return None

        retweet_data = {}
        if twitterSource.is_retweet:
            retweetSource = db_session.query(
                twitter_models
            ).get(twitterSource.retweet_source_id)
            retweet_data = {
                'user_name': retweetSource.tweeter_user_name,
                'tweet_id': retweetSource.tweet_id,
                'url': retweetSource.text_source.source_url,
                'tweet_text': retweetSource.text_source.written_text,
                'tweet_created': get_string_from_datetime(
                    retweetSource.text_source.time_posted
                ),
                'is_retweet': retweetSource.is_retweet,
                'user_mentions': [
                    mention.user_name for mention in retweetSource.mentions
                ],
                'hashtags': [
                    hashtag.hashtag for hashtag in retweetSource.hashtags
                ],
                'tweet_urls': [
                    url.url for url in retweetSource.urls
                ]
            }

        ret_data = {
            'user_name': twitterSource.tweeter_user_name,
            'tweet_id': twitterSource.tweet_id,
            'url': twitterSource.text_source.source_url,
            'tweet_text': twitterSource.text_source.written_text,
            'tweet_created': get_string_from_datetime(
                twitterSource.text_source.time_posted
            ),
            'is_retweet': twitterSource.is_retweet,
            'user_mentions': [
                mention.user_name for mention in twitterSource.mentions
            ],
            'hashtags': [
                hashtag.hashtag for hashtag in twitterSource.hashtags
            ],
            'tweet_urls': [
                url.url for url in twitterSource.urls
            ],
            'retweet_data': retweet_data
        }
    return ret_data


def insert_text_data(data_source, source_url, text, time_posted, session):
    """Adds the base entry for a text data source to the database and returns
    the newly created model


    Keyword arguments:
    data_source -- An enum indicating source. The enum is located in
    interns.models.models.AllowedSources
    source_url -- A string indicating the url the text was pulled from
    text -- the raw text data pulled from the url
    time_posted -- either a datetime object or a datetime string
    session -- active db session
    """
    if not isinstance(time_posted, datetime):
        time_posted = date_parse(time_posted)

    logger.debug('Inserting text data into postgres')

    TextModel = models.TextSource(
        source_key=data_source,
        source_url=source_url,
        written_text=text,
        time_posted=time_posted
    )

    session.add(TextModel)
    return TextModel


def get_tracked_twitter_tl_users():
    """
    Pull the list of twitter users that is being polled by the interns
    """
    logger.debug('Getting listing of tracked twitter users')
    tracked_users = []
    with GetDBSession() as db_session:
        tracked_users_query = db_session.query(
            twitter_models.PolledTimelineUsers
        )
        for user in tracked_users_query:
            tracked_users.append(user.user_name)
    return tracked_users


def begin_tracking_twitter_user(username):
    """
    Add a twitter user to be tracked to the databse

    Arguments:
    username -- Twitter username/screen_name to be added. For example to add
    username '@NASA' to be polled: add_tracked_twitter_tl_user('NASA')
    """
    new_user = twitter_models.PolledTimelineUsers(user_name=username)
    with GetDBSession() as db_session:
        db_session.add(new_user)
        db_session.commit()
    logger.debug('Adding twitter user %s to be tracked', username)


def is_twitter_user_in_interns(screen_name):
    """
    Checks to see if a twitter user exists within the database. Returns True
    if the screen_name is present in the database else returns False.

    For example checking to see if the user '@NASA' exists within the database
    the method would be called like so: is_twitter_user_in_interns('NASA')

    Arguments:
    screen_name -- Twitter user_name/screen_name to check for.
    """
    screen_names = []
    with GetDBSession() as db_session:
        distinct_screen_names = db_session.query(
            distinct(twitter_models.TwitterSource.tweeter_user_name)
        )
    for sn in distinct_screen_names:
        screen_names.append(sn[0])
    is_user_tracked = screen_name in screen_names
    logger.debug(
        'Twitter username %s is currently being tracked by interns is: %s',
        screen_name,
        is_user_tracked
    )
    return screen_name in screen_names


def last_twitter_user_entry_id(screen_name):
    """
    Returns the latest tweet id assocaited with screen_name otherwise returns
    None.

    Arguments:
    screen_name -- Twitter user_name/screen_name to check for.
    """
    with GetDBSession() as db_session:
        if is_twitter_user_in_interns(screen_name):
            # Check to make sure it's not a retweet
            # change this to filter against if retweet
            query = db_session.query(
                twitter_models.TwitterSource.tweet_id
            ).filter_by(
                tweeter_user_name=screen_name
            ).order_by(
                desc(twitter_models.TwitterSource.tweet_id)
            ).first().tweet_id

            logger.debug(
                'Last tweet id from twitter user %s is %s',
                screen_name,
                query
            )
            return query
        else:
            return None


def add_urls(tweet_data, tweetModel):
    """Add urls to tweetModel"""
    urls = tweet_data['tweet_urls']
    if urls:
        for url in urls:
            tweetURL = twitter_models.TweetURLs(
                url=url
            )
            tweetModel.urls.append(tweetURL)


def add_hashtags(tweet_data, tweetModel):
    """Insert hashtags"""
    hashtags = tweet_data['hashtags']
    if hashtags:
        for hashtag in hashtags:
            tweetHashtag = twitter_models.TweetHashtags(
                hashtag=hashtag
            )
            tweetModel.hashtags.append(tweetHashtag)


def add_user_mentions(tweet_data, tweetModel):
    """Insert user mentions"""
    user_mentions = tweet_data['user_mentions']
    if user_mentions:
        for mention in user_mentions:
            userMention = twitter_models.TweetUserMentions(
                user_name=mention
            )
            tweetModel.mentions.append(userMention)


def insert_retweet_data(retweet_data):
    """Inserts retweet data"""
    insert_tweet_data(retweet_data['retweet_data'])
    with GetDBSession() as db_session:
        retweet_id = int(retweet_data['retweet_data']['tweet_id'])
        retweetSource = db_session.query(
            twitter_models.TwitterSource
        ).filter(
            twitter_models.TwitterSource.tweet_id == retweet_id
        ).first()

        tweetTextModel = insert_text_data(
            models.AllowedSources.twitter.name,
            retweet_data['url'],
            '',
            retweet_data['tweet_created'],
            db_session
        )

        tweetModel = twitter_models.TwitterSource(
            retweet_source_id=retweetSource.id,
            tweeter_user_name=retweet_data['user_name'],
            tweet_id=retweet_data['tweet_id'],
            is_retweet=True
        )
        tweetTextModel.twitter_source = tweetModel
        try:
            db_session.commit()
        except IntegrityError as e:
            if 'duplicate key value' in e.message:
                # We've already captured this so, moving on
                logger.info(
                    'Duplicate tweet is already in the database, skipping'
                )
            else:
                logger.critical(
                    (
                        'A database error occurred while attempting to '
                        'insert tweet %s'
                    ),
                    e
                )
        except Exception as e:
            # Something real bad happened
            logger.critical(
                (
                    'An error has occurred while inserting a tweet into '
                    'the database %s'
                ),
                e
            )


def insert_non_retweet_data(tweet_data):
    """Takes the passed in JSON tweet_data and inserts into the database"""
    logger.debug('Inserting tweet data')
    with GetDBSession() as db_session:
        tweetTextModel = insert_text_data(
            models.AllowedSources.twitter.name,
            tweet_data['url'],
            tweet_data['tweet_text'],
            date_parse(tweet_data['tweet_created']),
            db_session
        )

        tweetModel = twitter_models.TwitterSource(
            tweeter_user_name=tweet_data['user_name'],
            tweet_id=tweet_data['tweet_id'],
            is_retweet=False
        )
        tweetTextModel.twitter_source = tweetModel

        add_user_mentions(tweet_data, tweetModel)
        add_hashtags(tweet_data, tweetModel)
        add_urls(tweet_data, tweetModel)

        try:
            db_session.commit()
        except IntegrityError as e:
            if 'duplicate key value' in e.message:
                # We've already captured this so, moving on
                logger.info(
                    'Duplicate tweet is already in the database, skipping'
                )
            else:
                logger.critical(
                    (
                        'A database error occurred while attempting '
                        'to insert tweet %s'
                    ),
                    e
                )
        except Exception as e:
            # Something real bad happened
            logger.critical(
                (
                    'An error has occurred while inserting a tweet into '
                    'the database %s'
                ),
                e
            )


def insert_tweet_data(tweet_data):
    """Takes a given JSON payload and depending on if a retweet inserts
    appropriately
    """
    if not isinstance(tweet_data, dict):
        tweet_data = json.loads(tweet_data)
    if tweet_data['is_retweet']:
        insert_retweet_data(tweet_data)
    else:
        insert_non_retweet_data(tweet_data)


def search_count_of_user_tweets_on_day(username, date, search_term):
    """When given a username, datetime, and search_term return the number of
    times search term was tweeted by username on the day of datetime"""
    return_data = {}
    date = date_parse(date)
    start = datetime(year=date.year, month=date.month, day=date.day)
    end = start + timedelta(days=1)
    with GetDBSession() as db_session:
        user_query = db_session.query(
            twitter_models.TwitterSource
            ).filter(
                twitter_models.TwitterSource.tweeter_user_name == username
            ).join(
                twitter_models.TwitterSource.text_source, aliased=True
            ).filter(
                and_(
                    and_(
                        models.TextSource.time_posted > start,
                        models.TextSource.time_posted < end
                    ),
                    models.TextSource.written_text.contains(search_term)
                )
            )

        return_data[username] = {search_term: user_query.count()}
    return return_data
