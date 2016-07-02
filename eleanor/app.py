import json

from flask import Flask, json, request

from utils import get_logger

from interns.clients.twitter import utils as twitter_utils


logger = get_logger(__name__)


web_app = Flask(__name__)


@web_app.route('/')
def hello():
    logger.debug('Hitting the test endpoint')
    return 'Ello there'


@web_app.route(
    '/twitter-tl-user', methods = ['POST', 'GET'], strict_slashes=False
)
def tracked_twitter_tl_user():
    if request.method == 'GET':
        logger.debug('Returning tracked twitter timeline users')
        tracked_users = twitter_utils.get_tracked_twitter_tl_users()
        return_data = {
            'tracked_twitter_usernames': []
        }
        return_data['tracked_twitter_usernames'] = tracked_users
        return json.dumps(return_data)
    elif request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            req_data = json.loads(request.json)
            logger.info(
                'Adding user: {0} to tracked twitter timline users'.format(
                    req_data['username']
                )
            )
            twitter_utils.add_tracked_twitter_tl_user(req_data['username'])


if __name__ == '__main__':
    web_app.run()

