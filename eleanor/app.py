"""Web app module for eleanor service"""
from flask import Flask, json, request, jsonify, abort

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
    '/twitter-tl-user', methods=['POST', 'GET'], strict_slashes=False
)
def tracked_twitter_tl_user():
    """Get or add new twitter users to be polled"""
    if request.method == 'GET':
        logger.debug('Returning tracked twitter timeline users')
        tracked_users = pg_utils.get_tracked_twitter_tl_users()
        return_data = {
            'tracked_twitter_usernames': []
        }
        return_data['tracked_twitter_usernames'] = tracked_users
        return json.dumps(return_data)
    elif request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            req_data = json.loads(request.get_json())
            request_user = req_data['username']
            logger.info(
                'Adding user: %s to tracked twitter timline users',
                request_user
            )
            if not pg_utils.is_twitter_user_in_interns(request_user):
                pg_utils.begin_tracking_twitter_user(req_data['username'])


@web_app.route('/add-tweet-data', methods=['POST'], strict_slashes=False)
def add_tweet_data():
    """Add data pulled from a tweet"""
    tweet_data = request.get_json()
    pg_utils.insert_tweet_data(tweet_data)


@web_app.route('/tweet/<tweet_id>', strict_slashes=False)
def get_tweet_from_id(tweet_id):
    """When given a tweet_id returns tweet data in the same format provided
    initially or returns a 204 if no tweet is found
    """
    tweet_data = pg_utils.get_tweet_data_by_id(tweet_id)
    if tweet_data:
        return jsonify(tweet_data)
    else:
        abort(204)


@web_app.route('/last-tweet-id/<username>', strict_slashes=False)
def get_last_tweet_id(username):
    """Returns the last tweet_id from username or a 204 if username is not
    tracked
    """
    last_tweet_id = pg_utils.last_twitter_user_entry_id(username)
    if last_tweet_id:
        last_return_key = '{0}_last_tweet_id'.format(username)
        return_data = {last_return_key: last_tweet_id}
        return jsonify(return_data)
    else:
        abort(204)


if __name__ == '__main__':
    web_app.run()
