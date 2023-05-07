from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.test_query import TestQuery
from utility.auth import token_require, get_identity
from utility.logger import get_logger
import uuid
import json
import os
import datetime


class Test(Resource):
    logger = get_logger('Test')

    @token_require
    def get(self):
        rtn = RtnMessage()
        try:
            pass
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()

    @token_require
    def post(self):
        rtn = RtnMessage()
        try:
            student_name, student_id, is_admin, is_teacher = get_identity()

            dao = TestQuery(config)
            question_name_list = dao.get_question_type()['type_name'].to_list()
            # random pick question
            pick_num = int(config['API']['QUESTION_NUM']) // len(question_name_list)
            question = dao.get_question(question_name_list=question_name_list,
                                        student_id=student_id,
                                        pick_num=pick_num)
            paper_index = dao.get_new_paperIndex(student_id=student_id)
            paper_id = str(uuid.uuid4())
            time_now = str(datetime.datetime.now())
            pass_num = int(len(question['answer']) * 0.6)
            file = {
                "student_id": student_id,
                "paper_id": paper_id,
                "paper_index": paper_index,
                "created_on": time_now,
                "answer_list": question['answer'].to_list(),
                "question_id_list": question['uuid'].to_list(),
                "type_id_list": question['type_id'].to_list(),
                "pass_num": pass_num
            }
            file_json = json.dumps(file)
            if os.path.exists(f'./test_tmp/{paper_id}.json'):
                raise Exception('file duplicated error')
            with open(f"./test_tmp/{paper_id}.json", 'w') as outfile:
                outfile.write(file_json)
            question.drop(['answer'], axis=1, inplace=True)
            rtn.result = {
                "paper_id": paper_id,
                "paper_index": paper_index,
                "created_on": time_now,
                "pass_num": pass_num,
                "question_list":
                    question.to_dict(orient='records')
            }

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
