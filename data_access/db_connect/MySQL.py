import pyodbc
import pandas as pd


class mysqlDB:
    def __init__(self, config, db_con='1'):
        self._config = config
        if config['STORGE']['USING'] != 'mysql':
            raise Exception('db type error')
        host = config['STORGE']['DATABASE']['IP']
        pwd = config['STORGE']['DATABASE']['PASSWORD']
        port = config['STORGE']['DATABASE']['PORT']
        db = config['STORGE']['DATABASE'][f'DB_{db_con}']
        user = config['STORGE']['DATABASE']['USER']
        self._db_handler = pyodbc.connect(
            f'DRIVER={"MySQL ODBC 8.0 Unicode Driver"};SERVER={host};DATABASE={db};UID={user};PWD={pwd};PORT={port}')

    def connect(self):
        return self._db_handler.cursor()

    def execute(self, sql_statement):
        success = True
        msg = ''
        con = self._db_handler.cursor()
        try:
            cursor = con.execute(sql_statement)
            cursor.commit()
            result = cursor.fetchall()
            return result
        except Exception as e:
            msg = e
            success = False
        finally:
            con.close()
            if not success:
                raise Exception(msg)

    def insert(self, sql_statement):
        success = True
        msg = ''
        con = self._db_handler.cursor()
        try:
            cursor = con.execute(sql_statement)
            cursor.commit()
        except Exception as e:
            msg = e
            success = False
        finally:
            con.close()
            if not success:
                raise Exception(msg)

    def delete(self, sql_statement):
        success = True
        msg = ''
        con = self._db_handler.cursor()
        try:
            cursor = con.execute(sql_statement)
            cursor.commit()
        except Exception as e:
            msg = e
            success = False
        finally:
            con.close()
            if not success:
                raise Exception(msg)

    def update(self, sql_statement):
        success = True
        msg = ''
        con = self._db_handler.cursor()
        try:
            cursor = con.execute(sql_statement)
            cursor.commit()
        except Exception as e:
            msg = e
            success = False
        finally:
            con.close()
            if not success:
                raise Exception(msg)

    def execute_many(self, sql_statement):
        success = True
        msg = ''
        con = self._db_handler.cursor()
        con.fast_executemany = True
        try:
            con.execute_many(sql_statement)
            con.commit()
        except Exception as e:
            msg = e
            success = False
        finally:
            con.close()
            if not success:
                raise Exception(msg)

    def execute_dataframe(self, sql_statement):
        success = True
        msg = ''
        con = self._db_handler
        try:
            result = pd.read_sql(sql_statement, con)
            return result
        except Exception as e:
            msg = e
            success = False
        finally:
            con.close()
            if not success:
                raise Exception(msg)
