import time
import sys
from queue import Queue

from pymongo import MongoClient

from betfair_functions import get_markets_ids, get_competition
from betfair_functions import convert_to_market_objs, get_market_types
from betfair_functions import CaptureMatch
from marketsdb import MarketsDB
import config


def addMarketCatalogues(comp_string, db):
    """
    Searches for competitions and saves any upcoming games into
    markets collection (does not find lives games)
    @param: comp_string *string*: name of competition being searched for
    @return: None
    """
    # Find competition
    competitions = get_competition(comp_string)

    if competitions is None:
        print("Can't find any competitions with that name")
        return

    print("found {} competitions:".format(len(competitions)))
    for i, c in enumerate(competitions):
        print("\t{}) name: {}, marketCount: {}".format(
            i, c.competition.name, c.market_count))

    resp = int(input("Select competition to retrieve markets from: "))
    competition = competitions[resp].competition

    market_codes = get_market_types(competition)
    for i, c in enumerate(market_codes):
        print("\t{}) name: {}".format(i, c.market_type))

    res = int(input("select market: "))
    print(market_codes[res].market_type)
    # Find all markets for competition and place into mongodb
    markets = get_markets_ids(
        competition=competition,
        market_type_codes=market_codes[res].market_type
    )

    print("found {} marketIds".format(len(markets)))
    for m in markets:
        print("\t {}".format(m.event.name))

    if len(markets) > 0:
        print("Saving markets to db")
        markets = convert_to_market_objs(markets)
        resp = db.write_markets_to_database(markets)

        # Make sure data written
        if not resp.acknowledged:
            print("Euston we have a problem!")


def capture_games(time_interval, db):
    """
    Keeps checking the db for games that are currently live, games
    that are are then fetched and written to the db
    @param: time_interval - time to sleep between fetches (seconds)
    @return: None
    """
    # Set up threads to fetch and process data
    q = Queue()
    for thread in range(4):
        CaptureMatch(queue=q, thread_no=thread).start()

    # Forever keep searching for games that are live.
    while True:
        # Find list of markets inplay
        market_ids = db.get_live_games_market_ids()
        if config.DEBUG:
            print("Found {} market Ids".format(len(market_ids)))

        if len(market_ids) > 0:
            for i in range(0, len(market_ids), 3):
                q.put(market_ids[i: i + 3])

        time.sleep(time_interval)   # now wait time_interval seconds


if __name__ == "__main__":
    # TODO include argparse to make sense of commandline arguments
    # https://docs.python.org/3.4/library/argparse.html

    db = MarketsDB(MongoClient()[config.LIVE_DB])

    if len(sys.argv) < 3:
        print("Running DEFAULT")
        # Incase no argument provided, capture games with 1 second increment
        capture_games(1, db)
    if sys.argv[1] == "competition":
        print("Added games to DB")
        addMarketCatalogues(sys.argv[2], db)
    if sys.argv[1] == "capture":
        if sys.argv[2] is not None:
            capture_games(int(sys.argv[2]), db)
        else:
            print("Must provide second argument for capture")
