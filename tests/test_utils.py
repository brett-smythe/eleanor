"""Test file for eleanor utilities"""
# pylint: disable=import-error
import unittest

import mock

from eleanor import utils as eleanor_utils


class EleanorUtilsCases(unittest.TestCase):
    """Test cases for eleanor utilities"""
    # pylint: disable=too-many-public-methods

    @mock.patch('eleanor.utils.logging')
    def test_get_eleanor_logger(self, mock_logging):
        """Test getting eleanor logger"""
        # pylint: disable=no-self-use
        eleanor_utils.get_logger()
        mock_logging.getLogger.assert_called()
