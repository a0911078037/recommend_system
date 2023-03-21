from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.user_query import UserQuery
import hashlib
import uuid
from utility.logger import get_logger
from flask_jwt_extended import jwt_required, get_jwt_identity


class User(Resource):
    logger = get_logger('user')

    @jwt_required()
    def get(self):
        rtn = RtnMessage()
        try:
            acc = get_jwt_identity()
            dao = UserQuery(config)
            df = dao.get_users(acc=acc)
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
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
            if 'Duplicate' in rtn.msg:
                rtn.msg = '帳號已經申請過了'
        return rtn.to_dict()

    @jwt_required()
    def put(self):
        rtn = RtnMessage()
        try:
            acc = request.json['acc']
            name = request.json['name']
            pws = request.json['pws']
            old_acc = get_jwt_identity()
            if not acc or not name or not pws:
                raise Exception('input cannot be null')
            salt = uuid.uuid4().hex[0:10]
            pws = hashlib.sha256((salt + pws).encode('utf-8')).hexdigest()
            dao = UserQuery(config)
            dao.update_users(acc=acc,
                             name=name,
                             pws=pws,
                             salt=salt,
                             old_acc=old_acc)

            rtn.msg = '更新完成，請重新登入'

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
            if 'Duplicate' in rtn.msg:
                rtn.msg = '帳號重複'
        return rtn.to_dict()

    @jwt_required()
    def delete(self):
        rtn = RtnMessage()
        try:
            acc = get_jwt_identity()
            dao = UserQuery(config)
            dao.delete_users(acc=acc)

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
