from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from datetime import datetime
import config
# from threading import Thread

# Connect to mongo database


#
# class db_writer(Thread):
#     def __init__(self, q):
#         """
#
#         :param db: mongodb to be written to
#         :param q: Queue to write data from
#         :return:
#         """
#         Thread.__init__(self)
#         self.q = q
#
#     def run(self):
#         # receive item from queue
#         data = self.q.get()
#
#         # Process data to get it into format to save to mongodb
#
#         # Check if market is no longer active
#         if data.status == "CLOSED":
#             # Write to events collection event status is now closed
#             pass
#         # Save to mongodb
#
#
#         # Let queue know that task is complete
#         self.q.task_done()

class MarketsDB():
    def __init__(self, db=MongoClient()[config.TEST_DB]):
        self.db = db
        self.markets_col = db[config.MARKETS_COLLECTION]
        self.book_col = db[config.MARKET_BOOK_COLLECTION]

    def clean_out_db(self):
        """
        Drops all tables and cleans the shit out of our database
        :return: None
        """
        self.db.client.drop_database(self.db.name)

    def write_markets_to_database(self, markets):
        """
        :param markets: Formated Markets from betfair
                        (see models.txt for formating)
        :return: Instance of Mongodb InsertManyResult.
        """
        # write all changes into db
        return self.markets_col.insert_many(markets, ordered=False)

    def write_books_to_database(self, books):
        """
        Writes books to database
        :param books: Books returned from betfair
        :return: Instance of mongodb InsertManyResult
        """
        market_updates = []  # Any markets that need to be closed

        # iterate through books and check if any markets are closed
        for book in books:
            if book["status"] == config.STATUS["CLOSED"]:
                market_updates.append(
                    UpdateOne(
                        {"marketId": book["marketId"]},
                        {"$set": {"status": config.STATUS["CLOSED"]}}
                    )
                )

        # TODO error correction if bulk writes don't work?
        try:
            if len(market_updates) > 0:
                self.markets_col.bulk_write(market_updates)
        except BulkWriteError as e:
            print(e.details)

        return self.book_col.insert_many(books, ordered=False)

    def get_live_games_market_ids(self):
        """
        Returns markets who's games have started (i.e. inplay)
        and markets which are not closed
        :return: List of market Ids (floats)
        """

        # Find games where openDates are
        # earlier than current time, but status is also open
        cur = self.markets_col.find(
            {"openDate":
             {"$lt": datetime.now()},
             "status":
                 {"$gt": config.STATUS["CLOSED"]}
             })

        return [market["marketId"] for market in cur]
