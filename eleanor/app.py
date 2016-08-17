"""Web app module for eleanor service"""
from flask import Flask, json, request, abort, Response

from utils import get_logger

from eleanor.clients.postgres import utils as pg_utils


logger = get_logger(__name__)


web_app = Flask(__name__)


@web_app.route('/')
def hello():
    """Temp test endpoint to verify service is running"""
    logger.debug('Hitting the test endpoint')
    return 'Ello there'


@web_app.route(
    '/twitter-tl-users', methods=['POST', 'GET'], strict_slashes=False
)
def tracked_twitter_tl_user():
    """Get or add new twitter users to be polled"""
    if request.method == 'GET':
        logger.debug('Returning tracked twitter timeline users')
        tracked_users = pg_utils.get_tracked_twitter_tl_users()
        return_data = {
            'twitter_usernames': []
        }
        return_data['twitter_usernames'] = tracked_users

        resp = Response(
            status=200,
            mimetype='application/json',
            response=json.dumps(return_data)
        )
        return resp
    elif request.method == 'POST':
        logger.debug('twitter-tl-users POST headers are: %s', request.headers)
        logger.debug(
            'twitter-tl-users POST request data: %s', request
        )
        logger.debug(
            'twitter-tl-users POST json: %s', request.json
        )
        for k, v in request.headers.items():
            if k.lower() == 'content-type':
                if v.lower() == 'application/json':
                    request_data = json.loads(request.json)
                    request_users = request_data['twitter_usernames']
                    logger.info(
                        'Adding users: %s to tracked twitter timline users',
                        request_users
                    )
                    for username in request_users:
                        if not pg_utils.is_twitter_user_in_interns(username):
                            pg_utils.begin_tracking_twitter_user(username)


@web_app.route('/add-tweet-data', methods=['POST'], strict_slashes=False)
def add_tweet_data():
    """Add data pulled from a tweet"""
    tweet_data = request.get_json()
    pg_utils.insert_tweet_data(tweet_data)
    return 200


@web_app.route('/tweet/<tweet_id>', strict_slashes=False)
def get_tweet_from_id(tweet_id):
    """When given a tweet_id returns tweet data in the same format provided
    initially or returns a 204 if no tweet is found
    """
    tweet_data = pg_utils.get_tweet_data_by_id(tweet_id)
    if tweet_data:
        resp = Response(
            status=200,
            mimetype='application/json',
            response=json.dumps(tweet_data)
        )
        return resp
    else:
        abort(204)


@web_app.route('/last-tweet-id/<username>', strict_slashes=False)
def get_last_tweet_id(username):
    """Returns the last tweet_id from username or a 204 if username is not
    tracked
    """
    last_tweet_id = pg_utils.last_twitter_user_entry_id(username)
    if last_tweet_id:
        return_data = {'last_tweet_id': last_tweet_id}
        resp = Response(
            status=200,
            mimetype='application/json',
            response=json.dumps(return_data)
        )
        return resp
    else:
        abort(204)


if __name__ == '__main__':
    web_app.run()
