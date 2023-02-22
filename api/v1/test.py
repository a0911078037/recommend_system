from flask_restx import Resource
from utility.ErrorHandler import ErrorHandler
from utility.RtnMessage import RtnMessage
from data_access.db_connect.MySQL import mysqlDB
from app import config


class test(Resource):
    def get(self):
        rtn = RtnMessage()
        try:
            db = mysqlDB(config)
            sql = 'SELECT * FROM users'
            d = db.execute(sql)
            print(d)
            rtn.msg = d.to_dict()
        except Exception as e:
            rtn = ErrorHandler(e, rtn).return_error()
        return rtn.to_dict()
