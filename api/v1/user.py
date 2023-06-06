from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.user_query import UserQuery
from data_access.query.student_query import StudentQuery
import hashlib
import uuid
from utility.logger import get_logger
from utility.auth import token_require, get_identity
import datetime


class User(Resource):
    logger = get_logger('user')

    @token_require
    def get(self):
        rtn = RtnMessage()
        name, _id, is_admin, is_teacher = get_identity()
        try:
            dao = UserQuery(config)
            df = dao.get_user_by_id(user_id=_id)
            if not len(df):
                raise Exception('account not found in db')
            rtn.result = {
                'acc': df['ACCOUNT'][0],
                'name': df['NAME'][0]
            }
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: NONE")
            self.logger.error(f"REQUEST IDENTITY: name:{name}, _id{_id}, is_admin:{is_admin}, is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()

    def post(self):
        rtn = RtnMessage()
        data = None
        try:
            data = {
                "acc": request.json.get('acc', None),
                "name": request.json.get('name', None),
                "pws": request.json.get('pws', None)
            }
            if not data['acc'] or not data['name'] or not data['pws']:
                raise Exception('input cannot be null')
            salt = uuid.uuid4().hex[0:10]
            pws = hashlib.sha256((salt + data['pws']).encode('utf-8')).hexdigest()
            dao = UserQuery(config)

            df = dao.get_users(acc=data['acc'])
            if not df.empty:
                raise Exception('account already exist')
            dao.create_users(acc=data['acc'],
                             name=data['name'],
                             pws=pws,
                             salt=salt)
            df = dao.get_user_id(acc=data['acc'])

            dao2 = StudentQuery(config)
            dao2.create_students(df['USER_ID'][0])

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()

    @token_require
    def put(self):
        rtn = RtnMessage()
        name, _id, is_admin, is_teacher = get_identity()
        data = None
        try:
            data = {
                "new_acc": request.json.get('acc', None),
                "new_name": request.json.get('name', None),
                "new_pws": request.json.get('pws', None)
            }

            if not data['new_acc'] or not data['new_name'] or not data['new_pws']:
                raise Exception('input cannot be null')
            dao = UserQuery(config)
            df = dao.get_users(acc=data['new_acc'])

            if not df.empty:
                raise Exception('account already exist, please re consider new account')
            salt = uuid.uuid4().hex[0:10]
            new_pws = hashlib.sha256((salt + data['new_pws']).encode('utf-8')).hexdigest()
            updated_on = datetime.datetime.now()
            dao.update_users(acc=data['new_acc'],
                             name=data['new_name'],
                             pws=new_pws,
                             salt=salt,
                             _id=_id,
                             updated_on=updated_on)
            dao.delete_token(user_id=_id)

            rtn.msg = '更新完成，請重新登入'

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            self.logger.error(f"REQUEST IDENTITY: name:{name}, _id{_id}, is_admin:{is_admin}, is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()

    @token_require
    def delete(self):
        rtn = RtnMessage()
        name, _id, is_admin, is_teacher = get_identity()
        try:
            dao = UserQuery(config)
            dao.delete_users(_id=_id)
            dao2 = StudentQuery(config)
            dao2.delete_student(_id)
            rtn.msg = '使用者成功刪除'

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: NONE")
            self.logger.error(f"REQUEST IDENTITY: name:{name}, _id{_id}, is_admin:{is_admin}, is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
