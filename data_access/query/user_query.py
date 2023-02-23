from data_access.db_connect.MySQL import mysqlDB


class UserQuery:
    def __init__(self, config):
        self._config = config
        self._db_handler = mysqlDB(config)

    def create_user(self, acc='', salt='', name='', pws=''):
        try:
            sql = \
                f"""
                INSERT INTO user (ACCOUNT, PASSWORD, NAME, SALT)
                VALUES("{acc}", "{pws}", "{name}", "{salt}")
                """
            self._db_handler.insert(sql)
        except Exception as e:
            raise e
