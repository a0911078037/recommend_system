from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
from utility.logger import get_logger
from utility.auth import token_require, get_identity
import plotly.express as px


# TODO teacher account, add_testPaper
class Teacher(Resource):
    logger = get_logger('Teacher')

    @token_require
    def get(self):
        rtn = RtnMessage()
        data = None
        name, _id, is_admin, is_teacher = get_identity()
        try:
            if not is_teacher or not is_admin:
                raise Exception('require teacher to access this api')
            dao = QuestionQuery(config)
            question_name_list = dao.get_question_type()['type_name'].to_list()
            df = dao.get_all_question(table_list=question_name_list)
            df = df[['uuid', 'question', 'options1', 'options2', 'options3', 'options4', 'options5', 'answer',
                     'answer_nums', 'correct_nums', 'category']]
            rtn.result = df.to_dict(orient='records')

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            self.logger.error(f"REQUEST IDENTITY: name:{name}, _id:{_id}, is_admin:{is_admin}, "
                              f"is_teacher:{is_teacher}")
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
