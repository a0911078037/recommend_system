from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.user_query import UserQuery
from utility.logger import get_logger
import hashlib
from utility.auth import create_token


class Login(Resource):
    logger = get_logger('login')

    def post(self):
        rtn = RtnMessage()
        try:
            acc = request.json['acc']
            pws = request.json['pws']
            if not acc or not pws:
                raise Exception('input cannot be null')
            if len(acc) >= 64 or len(pws) >= 64:
                raise Exception('length is too long')
            dao = UserQuery(config)
            df = dao.get_users(acc=acc)
            if not len(df):
                raise Exception('帳號或密碼錯誤')
            pws = hashlib.sha256((df['SALT'][0] + pws).encode('utf-8')).hexdigest()
            if df['PASSWORD'][0] == pws:
                token = create_token(is_admin=df['is_admin'][0],
                                     is_teacher=df['is_teacher'][0],
                                     name=df['NAME'][0],
                                     user_id=df['USER_ID'][0])
                dao.update_token(user_id=df['USER_ID'][0],
                                 token=token)
                rtn.result = {
                    'name': df['NAME'][0],
                    'token': token
                }
                rtn.msg = '登入成功'
            else:
                raise Exception('帳號或密碼錯誤')
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
