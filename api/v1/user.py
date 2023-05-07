from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.user_query import UserQuery
from data_access.query.student_query import StudentQuery
import hashlib
import uuid
from utility.logger import get_logger
from utility.auth import create_token, token_require, get_identity
import datetime


class User(Resource):
    logger = get_logger('user')

    @token_require
    def get(self):
        rtn = RtnMessage()
        try:
            acc = get_identity()
            dao = UserQuery(config)
            df = dao.get_users(acc=acc)
            if not len(df):
                raise Exception('account not found in db')
            rtn.result = {
                'acc': df['ACCOUNT'][0],
                'name': df['NAME'][0]
            }
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

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
            dao.create_users(acc=acc,
                             name=name,
                             pws=pws,
                             salt=salt)
            df = dao.get_user_id(acc=acc)

            dao2 = StudentQuery(config)
            dao2.create_students(df['USER_ID'][0])

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
            if 'Duplicate' in rtn.msg:
                rtn.msg = '帳號已經申請過了'
        return rtn.to_dict()

    @token_require
    def put(self):
        rtn = RtnMessage()
        try:
            acc = request.json['acc']
            name = request.json['name']
            pws = request.json['pws']
            old_acc = get_identity()
            if not acc or not name or not pws:
                raise Exception('input cannot be null')
            salt = uuid.uuid4().hex[0:10]
            pws = hashlib.sha256((salt + pws).encode('utf-8')).hexdigest()
            updated_on = datetime.datetime.now()
            dao = UserQuery(config)
            dao.update_users(acc=acc,
                             name=name,
                             pws=pws,
                             salt=salt,
                             old_acc=old_acc,
                             updated_on=updated_on)

            rtn.msg = '更新完成，請重新登入'

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
            if 'Duplicate' in rtn.msg:
                rtn.msg = '帳號重複'
        return rtn.to_dict()

    @token_require
    def delete(self):
        rtn = RtnMessage()
        try:
            acc = get_identity()
            dao = UserQuery(config)
            df = dao.get_user_id(acc=acc)
            dao.delete_users(acc=acc)
            dao2 = StudentQuery(config)
            dao2.delete_student(df['USER_ID'][0])

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
