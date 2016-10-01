"""Tests for the eleanor web app"""
# pylint: disable=import-error
import unittest
import json

from functools import wraps
from logging import RootLogger

import mock

from flask import Response

import eleanor
import eleanor.app


class EleanorAppCases(unittest.TestCase):
    """Tests for the eleanor web app"""
    # pylint: disable=too-many-public-methods

    def create_test_context(endpoint, http_method):
        """Decorator for creating contexts for eleanor tests"""
        # pylint: disable=no-self-argument
        def decorator(func):
            # pylint:disable=missing-docstring, unused-variable

            @wraps(func)
            def func_wrapper(self, *args, **kwargs):
                # pylint: disable=missing-docstring, unused-argument
                with eleanor.app.web_app.test_request_context(
                    endpoint, http_method
                ):
                    func(self, *args, **kwargs)
            return func_wrapper
        return decorator

    @mock.patch('eleanor.app.get_logger')
    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/twitter-tl-users', 'GET')
    def test_tracked_twitter_tl_users_get(self, mock_pg_utils, mock_get_log):
        """Test getting the list of tracked twitter users"""
        fake_users = ['NASA', 'JossWhedon']
        response_data = {'twitter_usernames': fake_users}
        test_response = Response(
            status=200,
            mimetype='application/json',
            response=json.dumps(response_data)
        )
        mock_get_log.return_value = mock.Mock(spec=RootLogger)
        mock_pg_utils.get_tracked_twitter_tl_users.return_value = fake_users
        return_resp = eleanor.app.tracked_twitter_tl_user()
        self.assertEqual(
            return_resp.status, test_response.status
        )
        self.assertEqual(
            return_resp.mimetype, test_response.mimetype
        )
        self.assertEqual(
            return_resp.response, test_response.response
        )

    @mock.patch('eleanor.app.request')
    @mock.patch('eleanor.app.get_logger')
    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/twitter-tl-users', 'POST')
    def test_tracked_twitter_tl_users_post(self, mock_pg_utils,
                                           mock_get_logger, mock_request):
        """Test adding a list of twitter users to track"""
        fake_users = ['SteveRogers', 'JossWhedon']
        mock_get_logger.return_value = mock.Mock(spec=RootLogger)
        mock_request.method = 'POST'
        mock_request.headers = {'content-type': 'application/json'}
        mock_request.json = {'twitter_usernames': fake_users}
        mock_pg_utils.is_twitter_user_in_interns.return_value = False
        return_resp = eleanor.app.tracked_twitter_tl_user()
        mock_pg_utils.begin_tracking_twitter_user.assert_any_call(
            fake_users[0]
        )
        mock_pg_utils.begin_tracking_twitter_user.assert_any_call(
            fake_users[1]
        )
        self.assertEqual(
            return_resp.status, '200 OK'
        )

    @mock.patch('eleanor.app.pg_utils')
    @mock.patch('eleanor.app.request')
    @create_test_context('/add-tweet-data', 'POST')
    def test_add_tweet_data(self, mock_request, mock_pg_utils):
        """Test inserting new tweet data"""
        # pylint: disable=no-self-use
        fake_data = '{"test": "json"}'
        mock_request.get_json.return_value = fake_data
        eleanor.app.add_tweet_data()
        mock_pg_utils.insert_tweet_data.assert_called_with(fake_data)

    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/tweet/10', 'GET')
    def test_get_tweet_from_id_200(self, mock_pg_utils):
        """Test getting a tweet by tweet id when a tweet exists"""
        fake_tweet_data = {'fake': 'tweet data'}
        test_response = Response(
            status=200,
            mimetype='application/json',
            response=json.dumps(fake_tweet_data)
        )
        mock_pg_utils.get_tweet_data_by_id.return_value = fake_tweet_data
        return_resp = eleanor.app.get_tweet_from_id(10)
        self.assertEqual(
            return_resp.status, test_response.status
        )
        self.assertEqual(
            return_resp.mimetype, test_response.mimetype
        )
        self.assertEqual(
            return_resp.response, test_response.response
        )

    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/tweet/10', 'GET')
    def test_get_tweet_from_id_204(self, mock_pg_utils):
        """Test getting a tweet by tweet id when no tweet exists with that
        id"""
        no_tweet = None
        mock_pg_utils.get_tweet_data_by_id.return_value = no_tweet
        self.assertEqual(
            eleanor.app.get_tweet_from_id(10).status,
            '204 NO CONTENT'
        )

    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/last-tweet-id/NASA', 'GET')
    def test_get_last_tweet_id_200(self, mock_pg_utils):
        """Test getting the last tweet id from a user that is tracked and has
        tweets in the database"""
        test_tweet_id = 10
        fake_data = {'last_tweet_id': test_tweet_id}
        test_response = Response(
            status=200,
            mimetype='application/json',
            response=json.dumps(fake_data)
        )
        mock_pg_utils.last_twitter_user_entry_id.return_value = test_tweet_id
        return_resp = eleanor.app.get_last_tweet_id(10)
        self.assertEqual(
            return_resp.status, test_response.status
        )
        self.assertEqual(
            return_resp.mimetype, test_response.mimetype
        )
        self.assertEqual(
            return_resp.response, test_response.response
        )

    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/last-tweet-id/NASA', 'GET')
    def test_get_last_tweet_id_204(self, mock_pg_utils):
        """Test getting last tweet id by username when either the user is not
        tracked or has no tweets in the database yet"""
        no_tweet_id = None
        mock_pg_utils.last_twitter_user_entry_id.return_value = no_tweet_id
        self.assertEqual(
            eleanor.app.get_last_tweet_id(10).status,
            '204 NO CONTENT'
        )

    @mock.patch('eleanor.app.request')
    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/stats/tweets-on-date', 'POST')
    def test_search_twitter_data_200(self, mock_pg_utils, mock_request):
        """Test searching for a number of tweets for a username on a date with a
        search term when they exist in the database"""
        fake_data = {'fake_counts': 20}
        test_response = Response(
            status=200,
            mimetype='application/json',
            response=json.dumps(fake_data)
        )
        mock_request.method = 'POST'
        mock_request.headers = {'content-type': 'application/json'}
        mock_request.json = {
            'twitter_username': 'Bucky',
            'search_date': '01/01/1945',
            'search_term': 'hydra'
        }
        mock_pg_utils.search_count_of_user_tweets_on_day.return_value = \
            fake_data
        return_resp = eleanor.app.search_twitter_data()
        self.assertEqual(
            return_resp.status, test_response.status
        )
        self.assertEqual(
            return_resp.mimetype, test_response.mimetype
        )
        self.assertEqual(
            return_resp.response, test_response.response
        )

    @mock.patch('eleanor.app.request')
    @mock.patch('eleanor.app.pg_utils')
    @create_test_context('/stats/tweets-on-date', 'POST')
    def test_search_twitter_data_204(self, mock_pg_utils, mock_request):
        """Test searching for a number of tweets for a username on a date with
        a search term when nothing is found"""
        no_results = None
        mock_request.method = 'POST'
        mock_request.headers = {'content-type': 'application/json'}
        mock_request.json = {
            'twitter_username': 'Bucky',
            'search_date': '01/01/1945',
            'search_term': 'hydra'
        }
        mock_pg_utils.search_count_of_user_tweets_on_day.return_value = \
            no_results
        self.assertEqual(
            eleanor.app.search_twitter_data().status,
            '204 NO CONTENT'
        )
