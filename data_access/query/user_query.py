from data_access.db_connect.MySQL import mysqlDB
from utility.logger import get_logger


class UserQuery:
    def __init__(self, config):
        self._config = config
        self._db_handler = mysqlDB(config, 1)
        self.logger = get_logger('UserQuery')

    def create_users(self, acc='', salt='', name='', pws=''):
        try:
            sql = \
                f"""
                INSERT INTO users (ACCOUNT, PASSWORD, NAME, SALT)
                VALUES(?, ?, ?, ?)
                """
            data = (acc, pws, name, salt)
            self._db_handler.insert(sql, data)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: acc:{acc}, salt:{salt}, name:{name}, pws:{pws}")
            raise Exception('error in query')

    def get_users(self, acc=''):
        try:
            sql = \
                f"""
                SELECT * FROM users
                WHERE ACCOUNT="{acc}"
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: acc:{acc}")
            raise Exception('error in query')

    def get_user_by_id(self, user_id=''):
        try:
            sql = \
                f"""
                SELECT * FROM users
                WHERE USER_ID="{user_id}"
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: user_id:{user_id}")
            raise Exception('error in query')

    def update_users(self, acc='', salt='', name='', pws='', _id='', updated_on=None):
        try:
            sql = \
                f"""
                UPDATE users 
                SET ACCOUNT="{acc}", PASSWORD="{pws}", NAME="{name}", SALT="{salt}", UPDATED_ON="{updated_on}"
                WHERE USER_ID="{_id}"
                """
            self._db_handler.update(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: acc:{acc}, salt:{salt}, name:{name}, pws:{pws}, _id:{_id}, "
                              f"updated_on:{updated_on}")
            raise Exception('error in query')

    def delete_users(self, _id=''):
        try:
            sql = \
                f"""
                DELETE FROM users
                WHERE USER_ID="{_id}"
                """
            self._db_handler.delete(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: _id:{_id}")
            raise Exception('error in query')

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
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: acc:{acc}")
            raise Exception('error in query')

    def update_token(self, user_id=None, token=None, refresh_token=None):
        try:
            sql = \
                f"""
                UPDATE users
                SET token="{token}", refresh_token="{refresh_token}"
                WHERE user_id="{user_id}"
                """
            self._db_handler.update(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: token:{token}, user_id:{user_id}")
            raise Exception('error in query')

    def delete_token(self, user_id=''):
        try:
            sql = \
                f"""
                UPDATE users
                SET token=NULL, refresh_token=NULL
                WHERE user_id="{user_id}"
                """
            self._db_handler.update(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: user_id:{user_id}")
            raise Exception('error in query')

    def get_token(self, user_id=''):
        try:
            sql = \
                f"""
                SELECT token FROM users
                WHERE USER_ID="{user_id}"
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: user_id:{user_id}")
            raise Exception('error in query')

    def get_all_userid(self):
        try:
            sql = \
                f"""
                SELECT USER_ID FROM `users`
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: NONE")
            raise Exception('error in query')

    def get_class_type(self):
        try:
            sql = \
                f"""
                SELECT * FROM `class_type`
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: NONE")
            raise Exception('error in query')

    def update_user_status(self, user_id='', user_agent='', ip=''):
        try:
            sql = \
                f"""
                UPDATE users
                SET user_agent='{user_agent}', ip='{ip}'
                WHERE user_id="{user_id}"
                """
            self._db_handler.update(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: user_id:{user_id}, user_agent:{user_agent}")
            raise Exception('error in query')
