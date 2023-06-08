from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.student_query import StudentQuery
import hashlib
import uuid
from utility.logger import get_logger
from utility.auth import token_require, get_identity


class Student(Resource):
    logger = get_logger('student')

    @token_require
    def get(self):
        rtn = RtnMessage()
        student_name, student_id, is_admin, is_teacher = get_identity()
        try:
            dao = StudentQuery(config)
            df = dao.get_student_status(student_id=student_id)
            df.astype({"paper_index": 'int', 'answered_right': 'int', 'total_question': 'int',
                       'score': 'int', 'total_score': 'int', 'limit_time': 'int'})
            df['answered_on'] = df['answered_on'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df['created_on'] = df['created_on'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df = df.to_dict(orient='records')
            rtn.result = {
                student_name: df
            }
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: NONE")
            self.logger.error(f"REQUEST IDENTITY: name:{student_name}, _id{student_id}, is_admin:{is_admin}, "
                              f"is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
