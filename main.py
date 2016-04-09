import time
import sys
from queue import Queue

from betfair_functions import get_markets_ids, get_competition, convert_to_market_objs, get_market_types, CaptureMatch
from db_functions import write_markets_to_database, get_live_games_market_ids, clean_out_db
from config import DEBUG


def clean_db():
    """
    clears the shit out of the database!
    """
    clean_out_db()

def addMarketCatalogues(comp_string):
    """
    Searches for competitions and saves any upcoming games into markets collection
    (does not find lives games)
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
        print("\t{}) name: {}, marketCount: {}".format(i, c.competition.name, c.market_count))

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
        resp = write_markets_to_database(markets)

        # Make sure data written
        if not resp.acknowledged:
            print("Euston we have a problem!")


def capture_games(time_interval):
    """
    Keeps checking the db for games that are currently live, games that are are then fetched
    and written to the db
    @param: time_interval - number of time to sleep between fetches (in seconds)
    @return: None
    """
    # Set up threads to fetch and process data
    q = Queue()
    for thread in range(4):
        CaptureMatch(queue=q, thread_no=thread).start()

    # Forever keep searching for games that are live.
    while True:
        # Find list of markets inplay
        market_ids = get_live_games_market_ids()
        if DEBUG:
            print("Found {} market Ids".format(len(market_ids)))

        if len(market_ids) > 0:
            for i in range(0, len(market_ids), 3):
                q.put(market_ids[i: i+3])

        time.sleep(time_interval)   # now wait time_interval seconds


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Running DEFAULT")
        # Incase no argument provided, capture games with 1 second increment
        capture_games(1)
    if sys.argv[1] == "competition":
        print("Added games to DB")
        addMarketCatalogues(sys.argv[2])
    if sys.argv[1] == "capture":
        if sys.argv[2] is not None:
            capture_games(int(sys.argv[2]))
        else:
            print("Must provide second argument for capture")


