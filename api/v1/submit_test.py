from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.test_query import TestQuery
from utility.logger import get_logger
import os
import json
import datetime
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

            created_on = paper['created_on']
            created_on = datetime.datetime.strptime(created_on, '%Y-%m-%d %H:%M:%S.%f')
            limit_time = paper['limit_time']
            current_time = datetime.datetime.now()
            tolerance_time = datetime.timedelta(minutes=int(config['API']['DEFAULT_TOLERANCE_TEST_TIME']))
            if created_on + datetime.timedelta(minutes=int(limit_time)) + tolerance_time < current_time:
                raise Exception('examination time is over!')

            if paper['paper_type'] == 'first_test':
                first_test(student_answer_list=student_answer_list,
                           paper=paper,
                           student_id=student_id,
                           paper_id=paper_id)
            else:
                raise Exception('paper_type invalid')

            file.close()

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()


def first_test(student_answer_list=None, paper=None, student_id=None, paper_id=None):
    dao = TestQuery(config)

    if paper['student_id'] != student_id:
        raise Exception('student_id not match with paper')

    if paper['paper_id'] != paper_id:
        raise Exception('paper id not match!')

    df = dao.get_paper_by_paper_index(student_id=student_id,
                                      paper_index=int(paper['paper_index']))
    if not df.empty:
        Exception('this paper already finish')

    correct_list = [1 if x == y else 0 for x, y in zip(student_answer_list, paper['answer_list'])]
    question_score_list = paper['question_score_list']

    question_name_list = dao.get_question_type()['type_name'].to_list()
    df = dao.get_question_type_id(question_name_list=question_name_list)
    score = 0
    cnt = Counter()
    for type_id, correct, question_score in zip(paper['type_id_list'], correct_list, question_score_list):
        question_name = df.loc[df['uuid'] == type_id]['type1'].values[0]
        cnt[question_name] += 1
        if correct:
            score += question_score
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
        created_on=paper['created_on'],
        total_score=paper['total_score'],
        score=score,
        paper_type=paper['paper_type']
    )

    dao.update_student_status(student_id=student_id,
                              question_name_list=question_name_list,
                              counter_list=cnt)
