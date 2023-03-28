from data_access.db_connect.MySQL import mysqlDB


class UserQuery:
    def __init__(self, config):
        self._config = config
        self._db_handler = mysqlDB(config, 1)

    def create_users(self, acc='', salt='', name='', pws=''):
        try:
            sql = \
                f"""
                INSERT INTO users (ACCOUNT, PASSWORD, NAME, SALT)
                VALUES("{acc}", "{pws}", "{name}", "{salt}")
                """
            self._db_handler.insert(sql)
        except Exception as e:
            raise e

    def get_users(self, acc=''):
        try:
            sql = \
                f"""
                SELECT PASSWORD, SALT, NAME, ACCOUNT FROM users
                WHERE ACCOUNT="{acc}"
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            raise e

    def update_users(self, acc='', salt='', name='', pws='', old_acc=''):
        try:
            sql = \
                f"""
                UPDATE users 
                SET ACCOUNT="{acc}", PASSWORD="{pws}", NAME="{name}", SALT="{salt}"
                WHERE ACCOUNT="{old_acc}"
                """
            self._db_handler.update(sql)
        except Exception as e:
            raise e

    def delete_users(self, acc=''):
        try:
            sql = \
                f"""
                DELETE FROM users
                WHERE ACCOUNT="{acc}"
                """
            self._db_handler.delete(sql)
        except Exception as e:
            raise e

    def get_user_id(self, acc=''):
        try:
            sql = \
                f"""
                SELECT USER_ID FROM users
                WHERE ACCOUNT="{acc}" 
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            raise e
