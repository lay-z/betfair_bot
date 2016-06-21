from os import path, environ

USERNAME = "priyav391"
PASSWORD = "Hustle101"

DEVELOPER_APP_KEY = "uxep2d9hyzIPslUA"
APP_KEY = "MpEYOYr9YIooK1XM"

CERT_FILE = path.normpath(
    path.join(path.dirname(__file__), "certs", "client-2048.pem"))

# Check if CERT_FILE exists
if not path.isfile(CERT_FILE):
    raise Exception("COULD NOT FIND CERTIFICATE FILE!" +
                    "Read README.md for more info")


TEST_DB = "infobored-test"
LIVE_DB = "infobored"

MARKETS_COLLECTION = "markets"
MARKET_BOOK_COLLECTION = "market-books"

STATUS = {
    'INACTIVE': -1,
    'CLOSED': 0,
    'OPEN': 1,
    'SUSPENDED': 2
}

DEBUG = True
