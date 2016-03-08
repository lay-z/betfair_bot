from os import path



USERNAME = "priyav391"
PASSWORD = "Hustle101"

DEVELOPER_APP_KEY = "uxep2d9hyzIPslUA"
APP_KEY = "MpEYOYr9YIooK1XM"

CERT_FILE = path.normpath(path.join(path.dirname(__file__), "certs", "client-2048.pem"))


DB_NAME = "infoboard_test"
MARKET_COLLECTION = "markets"
MARKET_BOOK_COLLECTION = "market_books"

STATUS = {
    'INACTIVE': -1,
    'CLOSED': 0,
    'OPEN': 1,
    'SUSPENDED': 2
}
