import pymysql.cursors
import config


class DbHelper:

    connection: pymysql.Connection = None

    def __init__(self):
        self.connect()

    @classmethod
    def connect(cls):
        """Connects to database."""
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
        """Executes query and returns result"""
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
        """Returns format %s, %d, %i of expression"""
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
        """Adds quotes if expression is text"""
        if isinstance(expr, float) or isinstance(expr, int):
            return f'{expr}'
        else:
            expr.replace("'", "\'")
            return f'\'{expr}\''

    @classmethod
    def insert(cls, table: str, fields_list: list, values_list: tuple) -> int:
        """Inserts record to table"""
        fields_list = list(f'`{field}`' for field in fields_list)
        fields = ', '.join(fields_list)
        # values_format = [cls.get_format(value) for value in values_list]
        values_format = ['%s'] * len(values_list)
        values_format = ', '.join(values_format)
        #values_list = [cls.get_value(value) for value in values_list]
        #tuple_values = tuple(values_list)
        #values = ','.join(values_list)
        query: str = f'insert into {table}({fields}) VALUES ({values_format})'
        print(f'Query: {query}')
        print(f'Values: {values_list}')

        cursor = cls.connection.cursor()
        cursor.execute(query, values_list)
        cls.connection.commit()
        return cursor.lastrowid

    @classmethod
    def update_or_insert_one(cls, table: str, fields: list, values: list, where: str) -> int:
        """Updates or inserts record to table"""
        rows = cls.select(table, where, fields + ['id'])
        if rows is None:
            return cls.insert(table, fields, values)
        row_id: int = rows[0]['id']
        # Меняем where, т.к. меняем ТОЛЬКО ОДНУ запись!
        where = f"id={row_id}"
        field_list = ', '.join([f'{field} = {cls.get_value(value)}' for field, value in zip(fields, values)])
        query: str = f'UPDATE `{table}` set {field_list} WHERE {where}'
        print(f'Query: {query}')
        cursor = cls.connection.cursor()
        cursor.execute(query)
        cls.connection.commit()
        return row_id

    @classmethod
    def select(cls, table: str, where: str, fields: list = None, order: list = None, limit: str = '') -> pymysql.cursors:
        """Construct the SELECT, executes, and returns rows"""

        if fields is None:
            fields_list = '*'
        else:
            fields_list = list(f'`{field}`' for field in fields)
            fields_list = ', '.join(fields_list)

        if order is not None:
            order_by = 'ORDER BY ' + ','.join(order)
        else:
            order_by = ''

        query: str = f'SELECT {fields_list} from `{table}` where {where} {order_by} {limit}'
        print(f'Query: {query}')
        cursor = cls.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall() if cursor.rowcount > 0 else None

    @classmethod
    def select_one(cls, table: str, where: str, fields: list = None, order: list = None, limit: str = ''):
        """Selects on record with condition WHERE"""
        rows = cls.select(table=table, where=where, fields=fields, order=order, limit=limit)
        return rows[0] if rows is not None else None
