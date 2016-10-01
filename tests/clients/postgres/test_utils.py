"""Test for eleanor sqlalchemy postgres utils"""
import unittest

from datetime import datetime

import mock

from eleanor.clients.postgres import utils


class EleanorPostgresUtilsCases(unittest.TestCase):
    """Tests for eleanor sqlalchemy postgres utils"""

    def test_get_string_from_datetime(self):
        """Test datetime conversion used by eleanor"""
        test_dt = datetime(year=1997, month=8, day=29, hour=02, minute=14)
        test_dt_string = utils.get_string_from_datetime(test_dt)
        self.assertEqual(
            test_dt_string,
            '1997-08-29T02:14:00+'
        )
