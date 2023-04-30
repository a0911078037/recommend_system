from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.test_query import TestQuery
from utility.logger import get_logger
import uuid
import json
import os
import datetime


class test(Resource):
    logger = get_logger('test')

    def get(self):
        rtn = RtnMessage()
        try:
            pass
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()

    def post(self):
        rtn = RtnMessage()
        try:
            student_id = request.json['student_id']
            if not student_id:
                raise Exception('input missing')

            dao = TestQuery(config)
            question_name_list = dao.get_question_type()['type_name'].to_list()
            # random pick question
            df = dao.get_question(question_name_list=question_name_list,
                                  student_id=student_id)
            question = df.sample(n=int(config['API']['QUESTION_NUM']))
            paper_index = dao.get_new_paperIndex(student_id=student_id)
            paper_id = str(uuid.uuid4())
            time_now = str(datetime.datetime.now())
            file = {
                "student_id": student_id,
                "paper_id": paper_id,
                "paper_index": paper_index,
                "created_on": time_now,
                "answer": question['answer'].to_list(),
                "question_id": question['uuid'].to_list(),
                "type_id": question['type_id'].to_list(),
                "category": question['category'].to_list()
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
                "question_list":
                    question.to_dict(orient='records')
            }

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
