from flask_restx import Resource
from utility.ErrorHandler import ErrorHandler
from utility.RtnMessage import RtnMessage


class test(Resource):
    def get(self):
        rtn = RtnMessage()
        try:
            raise Exception('e')
        except Exception as e:
            rtn = ErrorHandler(e, rtn).return_error()
        return rtn.to_dict()
