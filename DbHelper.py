import pymysql.cursors
import config


class DbHelper:

    connection: pymysql.Connection = None

    def __init__(self):
        self.connect()

    @classmethod
    def connect(cls):
        try:
            cls.connection = pymysql.connect(
                host=config.mysql_host,
                port=config.mysql_port,
                user=config.mysql_user,
                password=config.mysql_password,
                database=config.mysql_db,
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            print(f'Connection refused:\n{e}')

    @classmethod
    def query(cls, query: str, params: list = None):
        result = None
        try:
            cursor = cls.connection.cursor()
            cursor.execute(query, params)
            result = cursor
        except Exception as e:
            print(f'Query exception:\n{e}\nQuery: query')
        return result

    @staticmethod
    def get_format(expr):
        if isinstance(expr, str):
            return '%s'
        elif isinstance(expr, float):
            return '%d'
        elif isinstance(expr, int):
            return '%i'
        else:
            return '%s'

    @staticmethod
    def get_value(expr):
        if isinstance(expr, float) or  isinstance(expr, int):
            return f'{expr}'
        else:
            expr.replace("'", "\'")
            return f'\'{expr}\''

    @classmethod
    def insert(cls, table: str, fields_list: list, values_list: list):
        fields_list = list(f'`{field}`' for field in fields_list)
        fields = ', '.join(fields_list)
        values_format = [cls.get_format(value) for value in values_list]
        values_format = ', '.join(values_format)
        # values_list = [cls.get_value(value) for value in values_list]
        tuple_values = tuple(values_list)
        values = ','.join(values_list)
        query: str = f'insert into {table}({fields}) VALUES ({values_format})'
        print(f'Query: {query}')
        print(f'Values: {values}')

        cursor = cls.connection.cursor()
        cursor.execute(query, tuple_values)
        cls.connection.commit()

