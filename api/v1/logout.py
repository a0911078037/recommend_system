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
        name, _id, is_admin, is_teacher = get_identity()
        try:
            dao = UserQuery(config)
            dao.delete_token(user_id=_id)
            rtn.msg = '登出成功'
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST IDENTITY: name:{name}, _id{_id}, is_admin:{is_admin}, is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
