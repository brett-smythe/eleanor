from flask import Flask, json, request

from eleanor.lib.interns.interns.clients.twitter import utils as twitter_utils


web_app = Flask(__name__)


@web_app.route('/')
def hello():
    return 'Ello there'


@web_app.route('/twitter-tl-user', methods = ['POST', 'GET'])
def add_tracked_twitter_tl_user():
    if request.method == 'GET':
        print twitter_utils.get_tracked_twitter_tl_users()
    elif request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            req_data = json.loads(request.json)
            twitter_utils.add_tracked_twitter_tl_user(req_data['username'])


if __name__ == '__main__':
    web_app.run()

