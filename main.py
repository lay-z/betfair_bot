from betfair import Betfair
from betfair.models import MarketFilter
from betfair.constants import MarketProjection
from constants import DEVELOPER_APP_KEY, CERT_FILE, USERNAME, PASSWORD

client = Betfair(DEVELOPER_APP_KEY, CERT_FILE)
client.login(USERNAME, PASSWORD)

event_types = client.list_event_types(
    MarketFilter(text_query='Football')
)
premier_league = client.list_competitions(
    MarketFilter(text_query='Barclays Premier League')
)[0].competition
print(len(event_types))                 # Get All the amounts of different events
print(event_types[0].event_type.name)   # 'Tennis'
football_event_type = event_types[0]


markets = client.list_market_catalogue(
    MarketFilter(
        event_type_ids=[football_event_type.event_type.id],
        market_type_codes="MATCH_ODDS",  # Betfair has a set of the types of codes
        competition_ids=[premier_league.id]
    ),
    market_projection=[MarketProjection.EVENT]  # also return details about market event
)
print(dir(markets[4]))
print(len(markets))

event = markets[5]



# print("Getting information for {} with market_id: {}".format(event.market_name, event.market_id))
#
# market_book = client.list_market_book(
#     market_ids=event.market_id,
# )

# print("for the market:{}, Total available: {}".format(markets[5].market_name, market_book.total_available))

for market in markets:
    print("Game: {}, total matched:{}, market id:{}".format(market.event.name, market.total_matched, market.market_id))
