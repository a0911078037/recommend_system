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
    data = None

    def post(self):
        rtn = RtnMessage()
        data = None
        try:
            data = {
                "acc": request.json.get('acc', None),
                "pws": request.json.get('pws', None)
            }
            if not data['acc'] or not data['pws']:
                raise Exception('input cannot be null')
            if len(data['acc']) >= 64 or len(data['pws']) >= 64:
                raise Exception('length is too long')
            dao = UserQuery(config)
            df = dao.get_users(acc=data['acc'])
            if not len(df):
                raise Exception('帳號或密碼錯誤')
            pws = hashlib.sha256((df['SALT'][0] + data['pws']).encode('utf-8')).hexdigest()
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
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
