from flask_restx import Resource
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
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
