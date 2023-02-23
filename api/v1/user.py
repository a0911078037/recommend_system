from flask_restx import Resource
from flask import request
from utility.ErrorHandler import ErrorHandler
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.user_query import UserQuery
import hashlib
import uuid


class User(Resource):
    def get(self):
        rtn = RtnMessage()
        try:
           pass
        except Exception as e:
            rtn = ErrorHandler(e, rtn).return_error()
        return rtn.to_dict()

    def post(self):
        rtn = RtnMessage()
        try:
            acc = request.json['acc']
            name = request.json['name']
            pws = request.json['pws']
            if not acc or not name or not pws:
                raise Exception('input cannot be null')
            salt = uuid.uuid4().hex[0:10]
            pws = hashlib.sha256((salt + pws).encode('utf-8')).hexdigest()
            dao = UserQuery(config)
            dao.create_user(acc=acc,
                            name=name,
                            pws=pws,
                            salt=salt)
        except Exception as e:
            rtn = ErrorHandler(e, rtn).return_error()
        return rtn.to_dict()

    def update(self):
        rtn = RtnMessage()
        try:
            pass
        except Exception as e:
            rtn = ErrorHandler(e, rtn).return_error()
        return rtn.to_dict()

    def delete(self):
        rtn = RtnMessage()
        try:
            pass
        except Exception as e:
            rtn = ErrorHandler(e, rtn).return_error()
        return rtn.to_dict()
