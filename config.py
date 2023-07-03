import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TINKOFF_TOKEN = os.environ.get('TINKOFF_TOKEN')

DB_ENGINE = os.environ.get('DB_ENGINE')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DBNAME = os.environ.get('DB_DBNAME')

class_codes = ['TQBR', 'SPBFUT'] # поиск только по акциям РФ и фьючерсам

url_menu = 'url_по_кнопке'

save_path = 'files/'

mysql_host = 'localhost'
mysql_port = 3306
mysql_user = 'mysql_user_name'
mysql_password = 'mysql_password'
mysql_db = 'mysql_database_name'

instruction = """/a - анекдот
            /s - история
            Цены на акции/фьючерсы МосБиржи, например:
            /SBER Сбербанк
            /GAZP - Газпром
            и т.д."""
