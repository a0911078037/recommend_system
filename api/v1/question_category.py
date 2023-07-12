from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
from utility.logger import get_logger
from utility.auth import token_require


class QuestionCategory(Resource):
    logger = get_logger('question_category')
    data = None

    @token_require
    def get(self):
        rtn = RtnMessage()
        data = None
        try:
            dao = QuestionQuery(config)
            df = dao.get_question_category()
            rtn.result = df.to_dict(orient='records')
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
