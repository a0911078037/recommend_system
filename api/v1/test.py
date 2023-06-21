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
import pandas as pd
import datetime


class Test(Resource):
    logger = get_logger('Test')

    @token_require
    def get(self):
        rtn = RtnMessage()
        student_name, student_id, is_admin, is_teacher = get_identity()
        try:
            data = {
                "paper_index": request.args.get('paper_index', None)
            }
            if not data['paper_index']:
                raise Exception('input data missing')
            dao = TestQuery(config)
            df = dao.get_paper_status_by_paper_index(student_id=student_id,
                                                     paper_index=data['paper_index'])
            if df.empty:
                raise Exception('test not found in db')

            question_name_list = dao.get_question_type()['type_name'].to_list()
            question_df = dao.get_full_test_by_paper_index(student_id=student_id,
                                                           paper_index=data['paper_index'],
                                                           question_name_list=question_name_list)
            paper_df = dao.get_paper_by_paper_index(student_id=student_id,
                                                    paper_index=data['paper_index'])
            # question reorder
            question_df = question_df.set_index('uuid')
            question_df = question_df.reindex(index=paper_df['question_id'])
            question_df = question_df.reset_index()
            question_df['student_answer'] = paper_df['student_answer']
            rtn.result.append({
                "limit_time": int(df['limit_time'][0]),
                "score": int(df['score'][0]),
                "total_score": int(df['total_score'][0]),
                "paper_type": df['paper_type'][0],
                "created_on": str(df['created_on'][0]),
                "answered_on": str(df['answered_on'][0]),
                "question_list":
                    question_df.to_dict(orient='records')
            })


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
            data = {
                "paper_type": request.json.get('paper_type', None)
            }
            if not data['paper_type']:
                raise Exception('input data missing')
            paper_type = data['paper_type'].lower()
            paper_id = None
            paper_index = None
            time_now = None
            question_score_list = None
            total_score = None
            question = None
            if paper_type == 'first_test':
                paper_id, paper_index, time_now, question_score_list, total_score, question = first_test(student_id)
            elif paper_type == 'content_based_test':
                paper_id, paper_index, time_now, question_score_list, total_score, question = \
                    content_based_test(student_id)
            else:
                raise Exception('paper_type invalid')
            rtn.result = {
                "paper_id": paper_id,
                "paper_index": paper_index,
                "created_on": time_now,
                "paper_type": data['paper_type'],
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


def first_test(student_id=None):
    dao = TestQuery(config)
    df = dao.get_paper_status_by_paper_index(student_id=student_id,
                                             paper_index=0)
    if not df.empty:
        raise Exception('first_test already done')
    paper_index = dao.get_new_paperIndex(student_id=student_id)
    question_name_list = dao.get_question_type()['type_name'].to_list()
    # random pick question
    pick_num_list = [int(config['API']['QUESTION_NUM']) // len(question_name_list)] * len(question_name_list)
    for i in range(0, int(config['API']['QUESTION_NUM']) % len(question_name_list)):
        pick_num_list[i] += 1

    df = dao.get_question_type_id_order_by_major_type(question_name_list=question_name_list)
    question_pick_dict = {}
    for question_name, pick_num in zip(question_name_list, pick_num_list):
        question_pick_dict[question_name] = {}
        if pick_num <= len(df[question_name]):
            for i in range(pick_num):
                question_pick_dict[question_name][df[question_name][i][0]] = 1
        else:
            for i, type_list in enumerate(df[question_name]):
                if i < pick_num % len(df[question_name]):
                    question_pick_dict[question_name][type_list[0]] = pick_num // len(df[question_name]) + 1
                else:
                    question_pick_dict[question_name][type_list[0]] = pick_num // len(df[question_name])
    question = dao.get_random_question_with_limit_by_type_id(question_name_list=question_name_list,
                                                             student_id=student_id,
                                                             question_pick_dict=question_pick_dict)
    # shuffle
    question = question.sample(frac=1).reset_index(drop=True)

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
    if os.path.exists(f'./test_tmp/first_test/{paper_id}.json'):
        raise Exception('file duplicated error')
    with open(f"./test_tmp/first_test/{paper_id}.json", 'w') as outfile:
        outfile.write(file_json)
    question.drop(['answer'], axis=1, inplace=True)

    return paper_id, paper_index, time_now, question_score_list, total_score, question


def content_based_test(student_id=None):
    dao = TestQuery(config)
    df = dao.get_paper_status_by_paper_index(student_id=student_id,
                                             paper_index=0)
    if df.empty:
        raise Exception('first_test must done first')

    df = dao.get_student_type(student_id=student_id)
    df = df[df['type_answer'] > df['type_correct']]
    df['need'] = df['type_answer'].sub(df['type_correct'])
    df.sort_values('need', ascending=True, inplace=True)
    df = df[df['need'] != 0]
    total_question_need = int(config['API']['QUESTION_NUM'])
    total_question = 0
    question_df = pd.DataFrame()
    for index, row in df.iterrows():
        question_need = row['need'] if row['need'] + total_question < total_question_need \
            else total_question_need - total_question
        df = dao.get_random_question_with_limit_by_type_id_2(
            question_name=row['type_name'].split(',')[0],
            type_id=row['type_id'],
            pick_num=question_need,
            student_id=student_id
        )
        question_df = question_df.append(df, ignore_index=True)
        total_question += question_need
        if total_question == total_question_need:
            break

    # insert question reason
    question_df['reason'] = '根據上次作答錯誤同類別的問題'

    # 補足尚未達到預設題數
    # question_name_list = dao.get_question_type()['type_name'].to_list()
    # # random pick question
    # pick_num_list = [(total_question_need - total_question) // len(question_name_list)] * len(
    #     question_name_list)
    # for i in range(0, (total_question_need - total_question) % len(question_name_list)):
    #     pick_num_list[i] += 1
    #
    # df = dao.get_question_type_id_order_by_major_type(question_name_list=question_name_list)
    # question_pick_dict = {}
    # for question_name, pick_num in zip(question_name_list, pick_num_list):
    #     question_pick_dict[question_name] = {}
    #     if pick_num <= len(df[question_name]):
    #         for i in range(pick_num):
    #             question_pick_dict[question_name][df[question_name][i][0]] = 1
    #     else:
    #         for i, type_list in enumerate(df[question_name]):
    #             if i < pick_num % len(df[question_name]):
    #                 question_pick_dict[question_name][type_list[0]] = pick_num // len(df[question_name]) + 1
    #             else:
    #                 question_pick_dict[question_name][type_list[0]] = pick_num // len(df[question_name])
    # question = dao.get_random_question_with_limit_by_type_id(question_name_list=question_name_list,
    #                                                          student_id=student_id,
    #                                                          question_pick_dict=question_pick_dict)
    # question['reason'] = '尚未作答過的題目'
    # question_df = question_df.append(question, ignore_index=True)
    # shuffle
    question_df = question_df.sample(frac=1).reset_index(drop=True)

    paper_id = str(uuid.uuid4())
    paper_index = dao.get_new_paperIndex(student_id=student_id)
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    question_score_list = [100 // len(question_df['answer'])] * len(question_df['answer'])
    total_score = 100
    file = {
        "student_id": student_id,
        "paper_id": paper_id,
        "paper_index": paper_index,
        "paper_type": "content_based",
        "created_on": time_now,
        "limit_time": config['API']['DEFAULT_TEST_TIME'],
        "answer_list": question_df['answer'].to_list(),
        "question_id_list": question_df['uuid'].to_list(),
        "type_id_list": question_df['type_id'].to_list(),
        "question_score_list": question_score_list,
        "total_score": total_score
    }
    file_json = json.dumps(file)
    if os.path.exists(f'./test_tmp/content_based/{paper_id}.json'):
        raise Exception('file duplicated error')
    with open(f"./test_tmp/content_based/{paper_id}.json", 'w') as outfile:
        outfile.write(file_json)
    question_df.drop(['answer'], axis=1, inplace=True)
    return paper_id, paper_index, time_now, question_score_list, total_score, question_df

