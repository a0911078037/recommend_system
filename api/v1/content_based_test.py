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


class ContentBasedTest(Resource):
    logger = get_logger('ContentBasedTest')

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
        student_name, student_id, is_admin, is_teacher = get_identity()
        try:
            dao = TestQuery(config)
            question_name_list = dao.get_question_type()['type_name'].to_list()
            # random pick question
            pick_num_list = [int(config['API']['QUESTION_NUM']) // len(question_name_list)] * len(question_name_list)
            for i in range(0, int(config['API']['QUESTION_NUM']) % len(question_name_list)):
                pick_num_list[i] += 1
            question = dao.get_random_question_with_limit_list_each_table(question_name_list=question_name_list,
                                                                          student_id=student_id,
                                                                          pick_num_list=pick_num_list)

            df = dao.get_paper_by_paper_index(student_id=student_id,
                                              paper_index=0)
            if not df.empty:
                raise Exception('first_test already done')
            paper_index = dao.get_new_paperIndex(student_id=student_id)
            paper_id = str(uuid.uuid4())
            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            question_score_list = [100 // len(question['answer'])] * len(question['answer'])
            total_score = 100
            file = {
                "student_id": student_id,
                "paper_id": paper_id,
                "paper_index": paper_index,
                "paper_type": "first_test",
                "created_on": time_now,
                "limit_time": config['API']['DEFAULT_TEST_TIME'],
                "answer_list": question['answer'].to_list(),
                "question_id_list": question['uuid'].to_list(),
                "type_id_list": question['type_id'].to_list(),
                "question_score_list": question_score_list,
                "total_score": total_score
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
                "question_score_list": question_score_list,
                "limit_time": config['API']['DEFAULT_TEST_TIME'],
                "total_score": total_score,
                "question_list":
                    question.to_dict(orient='records')
            }

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: NONE")
            self.logger.error(f"REQUEST IDENTITY: name:{student_name}, _id{student_id}, is_admin:{is_admin}, "
                              f"is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
