from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.test_query import TestQuery
from data_access.query.question_query import QuestionQuery
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
        student_name, student_id, is_admin, is_teacher = get_identity()
        data = None
        try:
            data = {
                "paper_id": request.json.get('paper_id', None),
                "answer_list": request.json.get("answer_list", None),
                "paper_type": request.json.get("paper_type", None)
            }

            if not data["paper_id"] or not data["answer_list"] or not data['paper_type']:
                raise Exception('input data missing')
            paper_file_path = None
            if data['paper_type'] == 'first_test':
                paper_file_path = f'./test_tmp/first_test/{data["paper_id"]}.json'
            elif data['paper_type'] == 'content_based':
                paper_file_path = f'./test_tmp/content_based/{data["paper_id"]}.json'
            else:
                raise Exception('invalid paper_type')

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

            if paper['paper_type'] != data['paper_type']:
                raise Exception('paper_type not match with db')

            submit_test(student_answer_list=data["answer_list"],
                        paper=paper,
                        student_id=student_id,
                        paper_id=data["paper_id"],
                        current_time=str(current_time))

            file.close()

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            self.logger.error(f"REQUEST IDENTITY: name:{student_name}, _id{student_id}, is_admin:{is_admin}, "
                              f"is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()


def submit_test(student_answer_list=None, paper=None, student_id=None, paper_id=None, current_time=None):
    dao = TestQuery(config)

    if paper['student_id'] != student_id:
        raise Exception('student_id not match with paper')

    if paper['paper_id'] != paper_id:
        raise Exception('paper id not match!')

    df = dao.get_paper_status_by_paper_index(student_id=student_id,
                                             paper_index=int(paper['paper_index']))
    if not df.empty:
        Exception('this paper already finish')

    correct_list = [1 if x == y else 0 for x, y in zip(student_answer_list, paper['answer_list'])]
    question_score_list = paper['question_score_list']

    question_name_list = dao.get_question_type()['type_name'].to_list()
    df = dao.get_question_type_id(question_name_list=question_name_list)
    score = 0
    cnt = Counter()
    type_cnt = Counter()
    type_dict = {}
    update_question_dict = {}
    for question_name in question_name_list:
        update_question_dict[question_name] = {}

    for type_id, correct, question_score, question_id in zip(paper['type_id_list'], correct_list, question_score_list,
                                                             paper['question_id_list']):
        # 計算大方向的類別
        question = df.loc[df['type_id'] == type_id].values[0].tolist()[0:-1]
        question = [i for i in question if i is not None]
        cnt[f"{question[1]}"] += 1

        # 計算小方向的類別
        type_name = ','.join(question[1:])
        type_cnt[f"{type_name}"] += 1
        type_dict[type_name] = question[0]
        update_question_dict[question[1]][question_id] = 0
        if correct:
            score += question_score
            cnt[f"correct_{question[1]}"] += 1
            type_cnt[f"correct_{type_name}"] += 1
            update_question_dict[question[1]][question_id] = 1

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
        paper_type=paper['paper_type'],
        answered_on=current_time,
        limit_time=paper['limit_time']
    )

    dao.update_student_status(student_id=student_id,
                              question_name_list=question_name_list,
                              counter_list=cnt)

    dao.update_student_type(type_cnt=type_cnt,
                            type_dict=type_dict,
                            student_id=student_id)

    dao = QuestionQuery(config)
    dao.update_question_answer_status(update_question_dict=update_question_dict)
