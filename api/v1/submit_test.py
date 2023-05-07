from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.test_query import TestQuery
from utility.logger import get_logger
import os
import json
from collections import Counter
from utility.auth import token_require, get_identity


class SubmitTest(Resource):
    logger = get_logger('SubmitTest')

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

            paper_id = request.json['paper_id']
            student_answer_list = request.json['answer_list']

            if not paper_id:
                raise Exception('input data missing')
            paper_file_path = f'./test_tmp/{paper_id}.json'

            if not os.path.exists(paper_file_path):
                raise Exception('paper not found! please get a new test and try again')

            file = open(paper_file_path)
            paper = json.load(file)

            if paper['student_id'] != student_id:
                raise Exception('student_id not match with paper')

            if paper['paper_id'] != paper_id:
                raise Exception('paper id not match!')

            dao = TestQuery(config)

            correct_list = [1 if x == y else 0 for x, y in zip(student_answer_list, paper['answer_list'])]

            question_name_list = dao.get_question_type()['type_name'].to_list()
            df = dao.get_question_type_id(question_name_list=question_name_list)
            cnt = Counter()
            for type_id, correct in zip(paper['type_id'], correct_list):
                question_name = df.loc[df['uuid'] == type_id]['type1'].values[0]
                cnt[question_name] += 1
                if correct:
                    cnt[f"correct_{question_name}"] += 1

            dao.insert_student_paper(student_id=student_id,
                                     student_answer_list=student_answer_list,
                                     answer_list=paper['answer_list'],
                                     correct_list=correct_list,
                                     paper_index=paper['paper_index'],
                                     question_id_list=paper['question_id_list'])

            dao.insert_student_answer(student_id=student_id,
                                      correct_list=correct_list,
                                      question_id_list=paper['question_id_list'])

            dao.insert_student_paper_status(
                student_id=student_id,
                paper_index=paper['paper_index'],
                paper_id=paper_id,
                answered_right=correct_list.count(1),
                total_question=len(paper['answer_list']),
                created_on=paper['created_on']
            )

            dao.update_student_status(student_id=student_id,
                                      question_name_list=question_name_list,
                                      counter_list=cnt)
            file.close()
            os.remove(paper_file_path)

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
