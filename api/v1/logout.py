from flask_restx import Resource
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.user_query import UserQuery
from utility.logger import get_logger
from utility.auth import token_require, get_identity


class Logout(Resource):
    logger = get_logger('logout')

    @token_require
    def post(self):
        rtn = RtnMessage()
        try:
            user_name, user_id, is_admin, is_teacher = get_identity()

            dao = UserQuery(config)
            dao.delete_token(user_id=user_id)
            rtn.msg = '登出成功'
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
