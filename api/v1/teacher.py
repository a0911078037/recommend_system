from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.test_query import TestQuery
from utility.logger import get_logger
import uuid
import json
import os
import datetime


# TODO teacher account, add_testPaper
class Teacher(Resource):
    logger = get_logger('Teacher')

    def get(self):
        rtn = RtnMessage()
        data = None
        try:
            pass
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()

    def post(self):
        rtn = RtnMessage()
        data = None
        try:
            pass
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
