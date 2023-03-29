from flask_restx import Resource
from utility.RtnMessage import RtnMessage
from data_access.db_connect.MySQL import mysqlDB
from app import config


class test(Resource):
    def get(self):
        rtn = RtnMessage()
        try:
            db = mysqlDB(config)
            sql = 'SELECT VERSION()'
            d = db.execute(sql)
            rtn.msg = 'db connect successfully'
        except Exception as e:
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
