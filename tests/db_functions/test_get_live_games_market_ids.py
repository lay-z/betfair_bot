from unittest import TestCase
from config import DB_NAME, MARKETS_COLLECTION, STATUS
from pymongo import MongoClient
from datetime import datetime, timedelta
from db_functions import get_live_games_market_ids


class TestGet_live_games_market_ids(TestCase):
    def setUp(self):
        # Set up database
        self.market_col = MongoClient()[DB_NAME][MARKETS_COLLECTION]
        self.market_col.drop()

    def test_get_live_games_market_ids(self):
        # Check that it only get games that are before a certain date
        # AND that the Status is NOT closed

        # Given
        marketId = ['1.234', '1.111', '3.553']

        self.market_col.insert_many([
            {
                # Literally event just started
                "marketId": marketId[0],
                "openDate": datetime.today(),
                "status": STATUS["OPEN"]
            }, {
                # Event starts 6 seconds from now
                "marketId": marketId[1],
                "openDate": datetime.today() + timedelta(seconds=10),
                "status": STATUS["OPEN"]
            }, {
                # Event is 90 minutes in and status is set to shut
                "marketId": marketId[2],
                "openDate": datetime.today() + timedelta(minutes=90),
                "status": STATUS["CLOSED"]
            }
        ])

        # When
        correct_live_ids = [marketId[0]]
        live_ids = get_live_games_market_ids()

        # Then
        self.assertEqual(live_ids, correct_live_ids)
