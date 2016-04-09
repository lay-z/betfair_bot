import threading
from datetime import datetime, timedelta
from betfair import Betfair
from betfair.models import MarketFilter, PriceProjection
from betfair.constants import MarketProjection, PriceData, OrderProjection, MatchProjection, MarketStatus
from config import DEVELOPER_APP_KEY, CERT_FILE, USERNAME, PASSWORD, APP_KEY, STATUS, DEBUG
from db_functions import write_books_to_database
from datetime import datetime

client = Betfair(APP_KEY, CERT_FILE)
client.login(USERNAME, PASSWORD)


class CaptureMatch(threading.Thread):
    def __init__(self, queue, thread_no):
        """

        :param time_stop: *datetime* time to stop exectuion of code
        :param delta: *int* number of seconds to wait
        :param game_name: *string* String representation of game
        :return:
        """
        threading.Thread.__init__(self)
        self.queue = queue 
        self.thread_no = thread_no
        if DEBUG:
            print("Thread no: {} initialised".format(self.thread_no))

    def run(self):
        if DEBUG:
            print("Thread no: {}  Running".format(self.thread_no))

        while True:
            market_ids = self.queue.get(block=True, timeout=None)
            if DEBUG:
                print("Thread no: {} getting data".format(self.thread_no))
            try:
                r = write_books_to_database(convert_to_market_book_objs(get_books(market_ids)))
                if DEBUG:
                    print("Thread no: {} written down {} books to database".format(self.thread_no,len(r.inserted_ids)))

            except TimeoutError as e:
                print("TIMEOUT ERROR !!\n{}".format(e.argv))
                print("Reinitalising client login")
                # Re initiate connection with betfair
                client.login(USERNAME, PASSWORD)
            except Exception as e:
                print("EXCEPTION OCCURED!!\n{}".format(e.argv))
                with open("Exceptions/{}".format(datetime.now())) as e_file:
                    e_file.write("Exception Type: {}\n Args: {}".format(type(e), e.args))


def get_markets_ids(competition, market_type_codes):
    """
    Gets all the competition IDS in betfair for a given competiion and a given market_type

    :param competition: Betfair competition model
    :param market_type_codes: *String* Betfair market codes, to receive market_ids for games
    :return: List of betfair MarketCatalogues for inplay markets in the specified leage
            MarketCatalogues will also contain information about the event and description about the runners
    """

    return client.list_market_catalogue(
        MarketFilter(
            market_type_codes=[market_type_codes],
            competition_ids=[competition.id],
            in_play_only=False  # Only get games that are currently running/in play
        ),
        market_projection=[MarketProjection.EVENT, MarketProjection.RUNNER_DESCRIPTION]
        # also return details about market event
    )

def get_market_types(competition):
    """
    Retrieves list of market_types
    :param competition:
    :return:
    """

    return client.list_market_types(
        MarketFilter(
            competition_ids=[competition.id],
        ),
    )


def get_books(market_ids):
    # Get information for Markets
    return client.list_market_book(
        market_ids=market_ids,
        price_projection=PriceProjection(
            price_data=[PriceData.EX_ALL_OFFERS]
        ),
        order_projection=OrderProjection.EXECUTABLE,
        match_projection=MatchProjection.ROLLED_UP_BY_AVG_PRICE
    )


def get_competition(name):
    c = client.list_competitions(
        MarketFilter(text_query=name)
    )
    if len(c) > 0:
        return c

def convert_to_market_objs(market_catalogues):
    """
    Converts/formats market_catalogue into eventObj to be stored into mongodb
    :param market_catalogues: betfair market_catalogue model (must have event and runner data)
    :return: list of dictionaries to write to
    """
    catalogues = []
    for market in market_catalogues:
        catalogue = market.to_primitive()  # Get raw event data
        catalogue["openDate"] = market.event.open_date  # Save as date format
        del catalogue["event"]["openDate"]
        catalogue["status"] = STATUS["OPEN"]

        catalogues.append(catalogue)
    return catalogues

def convert_to_market_book_objs(market_books):
    """
    Converts betfair market_book models into objects to store into mongo
    :param market_books:
    :return: list of dictionaires to write to market-book database
    """
    formated_books = []
    for book in market_books:
        tmp_book = book.to_primitive()
        tmp_book["lastMatchTime"] = book.last_match_time
        tmp_book["status"] = STATUS[book["status"]]
        tmp_book["timeReceived"] = datetime.now()
        formated_books.append(tmp_book)

    return formated_books

if __name__ == "__main__":
    timeStop = datetime.now() + timedelta(minutes=3)
    match1 = CaptureMatch(timeStop, 3, "thread1")
    match2 = CaptureMatch(timeStop, 3, "thread2")
    print("in main")
    try:
        match1.start()
        match2.start()
    except Exception as e:
        print("Errors caught!")
        print(e)
