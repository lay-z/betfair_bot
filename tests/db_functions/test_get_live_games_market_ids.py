from unittest import TestCase
from config import MARKETS_COLLECTION, STATUS, MARKET_BOOK_COLLECTION
from pymongo import MongoClient
from datetime import datetime, timedelta
from marketsdb import MarketsDB


class TestGet_live_games_market_ids(TestCase):
    #  Run once
    def setup_class(self):
        self.marketdb = MarketsDB()

    # Run before every test method
    def setUp(self):
        # Set up database
        self.marketdb.clean_out_db()

    def test_get_live_games_market_ids(self):
        # Check that it only get games that are before a certain date
        # AND that the Status is NOT closed

        # Given
        marketId = ['1.234', '1.111', '3.553']

        self.marketdb.db[MARKETS_COLLECTION].insert_many([
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

        print("In database currently:")
        print([c for c in self.marketdb.db[MARKETS_COLLECTION].find()])

        # When
        correct_live_ids = [marketId[0]]
        live_ids = self.marketdb.get_live_games_market_ids()

        # Then
        self.assertEqual(live_ids, correct_live_ids)

    def test_write_books_to_db_also_changes_market_col_status_if_inserted_book_status_has_been_set_to_closed(self):
        # Check that written to database
        # Also check that relevent market in market_col is also set to "CLOSED"
        # Given
        marketId = ['1.234', '1.111', '3.553']

        # Set up games that already exist
        self.marketdb.db[MARKETS_COLLECTION].insert_many([
            {
                # Literally event just started
                "marketId": marketId[0],
                "openDate": datetime.today(),
                "status": STATUS["OPEN"]
            }
        ])

        book = {
            "marketId": marketId[0],
            "status": STATUS["CLOSED"]
        }

        # When
        self.marketdb.write_books_to_database([book])

        # Then
        # will raise execption if no data available
        markets = self.marketdb.db[MARKETS_COLLECTION].find().next()
        self.assertEqual(markets["status"], STATUS["CLOSED"])

    def test_write_books_to_db_only_changes_status_not_anything_else(self):
        # Check that written to database
        # Also check that relevent market in market_col is also set to "CLOSED"
        # Given
        market_id = ['1.234', '1.111', '3.553']

        document = {
            # Literally event just started
            "marketId": market_id[0],
            "openDate": datetime.today().replace(microsecond=0),
            "status": STATUS["OPEN"]
        }
        # Set up games that already exist
        self.marketdb.db[MARKETS_COLLECTION].insert_many([
            document
        ])

        book = {
            "marketId": market_id[0],
            "status": STATUS["CLOSED"]
        }

        # When
        self.marketdb.write_books_to_database([book])
        document["status"] = STATUS["CLOSED"]

        # Then
        # will raise execption if no data available
        markets = self.marketdb.db[MARKETS_COLLECTION].find().next()
        self.assertEqual(document, markets)
