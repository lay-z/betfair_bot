import time

from betfair_functions import get_markets_ids, get_competition, convert_to_market_objs, get_books
from db_functions import write_markets_to_database, get_live_games_market_ids, clean_out_db, write_books_to_database

# Lets clean out our database first!
# clean_out_db()

market_codes = ["MATCH_ODDS"]
# Find competition
competition = get_competition("Armenian First League")


# Find all markets for competition and place into mongodb

markets = get_markets_ids(
    competition=competition,
    market_type_codes=market_codes
)

print("found {} marketIds".format(len(markets)))
markets = convert_to_market_objs(markets)
resp = write_markets_to_database(markets)

# Make sure data written
if not resp.acknowledged:
    print("Euston we have a problem!")


# Forever keep searching for games that are live.
while True:
    # Find list of markets inplay
    market_ids = get_live_games_market_ids()
    if len(market_ids) > 0:
        write_books_to_database([book.to_primitive() for book in get_books(market_ids)])
        print("written down {} books to database".format(len(market_ids)))
    time.sleep(1)   # now wait a second


# # Combine all runners in to nice array
# runners = []
# for market in markets:
#     runners += market.runners
#
#
# # Get information for Markets
# books = get_books(market_ids=marketIds)
#
# for book in books:
#     print