import threading
from datetime import datetime, timedelta
from time import sleep
from betfair import Betfair
from betfair.models import MarketFilter, PriceProjection
from betfair.constants import MarketProjection, PriceData, OrderProjection, MatchProjection, MarketStatus
from config import DEVELOPER_APP_KEY, CERT_FILE, USERNAME, PASSWORD, APP_KEY, STATUS

client = Betfair(APP_KEY, CERT_FILE)
client.login(USERNAME, PASSWORD)


class CaptureMatch(threading.Thread):
    def __init__(self, queue):
        """

        :param time_stop: *datetime* time to stop exectuion of code
        :param delta: *int* number of seconds to wait
        :param game_name: *string* String representation of game
        :return:
        """
        threading.Thread.__init__(self)
        # self.time_start = time_start
        self.time_stop = time_stop
        print(self.time_stop)
        self.delta = delta
        self.game_name = game_name
        self.queue = queue

    def run(self):
        current_datetime = datetime.now()
        while current_datetime < self.time_stop:
            print("Currently at time: {} with thread {}".format(current_datetime, self.game_name))
            sleep(self.delta)
            current_datetime = datetime.now()


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
            market_type_codes=market_type_codes,
            competition_ids=[competition.id],
            in_play_only=True  # Only get games that are currently running/in play
        ),
        market_projection=[MarketProjection.EVENT, MarketProjection.RUNNER_DESCRIPTION]
        # also return details about market event
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
    return client.list_competitions(
        MarketFilter(text_query=name)
    )[0].competition


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
