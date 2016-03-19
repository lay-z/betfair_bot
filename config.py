from os import path, environ

USERNAME = "priyav391"
PASSWORD = "Hustle101"

DEVELOPER_APP_KEY = "uxep2d9hyzIPslUA"
APP_KEY = "MpEYOYr9YIooK1XM"

CERT_FILE = path.normpath(path.join(path.dirname(__file__), "certs", "client-2048.pem"))

DB_NAME = environ.get("BORED_DB", "infobored-test")

MARKETS_COLLECTION = "markets"
MARKET_BOOK_COLLECTION = "market-books"

STATUS = {
    'INACTIVE': -1,
    'CLOSED': 0,
    'OPEN': 1,
    'SUSPENDED': 2
}
