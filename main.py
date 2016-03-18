import time

import sys
from betfair_functions import get_markets_ids, get_competition, convert_to_market_objs, get_books, convert_to_market_book_objs
from db_functions import write_markets_to_database, get_live_games_market_ids, clean_out_db, write_books_to_database



def clean_db():
    """
    clears the shit out of the database!
    """
    clean_out_db()

def addCompetitions(comp_string):
    """
    Searches for competitions and saves any upcoming games into markets collection
    (does not find lives games)
    @param: comp_string *string*: name of competition being searched for
    @return: None
    """
    market_codes = ["MATCH_ODDS"]

    # Find competition
    competition = get_competition(comp_string)


    # Find all markets for competition and place into mongodb

    markets = get_markets_ids(
        competition=competition,
        market_type_codes=market_codes
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
    # Forever keep searching for games that are live.
    while True:
        # Find list of markets inplay
        market_ids = get_live_games_market_ids()
        if len(market_ids) == 0:
            print("no markets to fetch")
        else:
            write_books_to_database(convert_to_market_book_objs(get_books(market_ids)))
            print("written down {} books to database".format(len(market_ids)))
        time.sleep(time_interval)   # now wait a second


if __name__ == "__main__":
    choice = {
            "competition": addCompetitions,
            "capture": capture_games
        }
    try:
        method = sys.argv[1]
        argument = sys.argv[2]
    except:
        # Incase no argument provided, capture games with 1 second increment
        capture_games(1)
        sys.exit() # stop

    choice[method](argument)

