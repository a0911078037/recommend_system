from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
from data_access.query.student_query import StudentQuery
from data_access.query.user_query import UserQuery
from data_access.query.test_query import TestQuery
from utility.logger import get_logger
from utility.auth import token_require, get_identity
import pandas as pd
import numpy as np
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
            data = {
                'get_type': request.args.get('get_type', None)
            }
            if not data['get_type']:
                raise Exception('input date invalid')
            if not is_teacher or not is_admin:
                raise Exception('require teacher to access this api')
            if data['get_type'] == 'question_db':
                dao = QuestionQuery(config)
                question_name_list = dao.get_question_type()['type_name'].to_list()
                type_id_df = pd.DataFrame()
                for question_name in question_name_list:
                    df = dao.get_question_type_by_table_name(table_name=question_name)
                    type_id_df = pd.concat([type_id_df, df])
                type_id_df = type_id_df[['type_id', 'type1']]
                major_type_df = dao.get_question_type()
                major_type_dict = {}
                for key, value in zip(major_type_df['type_name'].tolist(), major_type_df['type'].tolist()):
                    major_type_dict[key] = value
                df = dao.get_all_question(table_list=question_name_list)
                df = df[['uuid', 'question', 'options1', 'options2', 'options3', 'options4', 'options5', 'answer',
                         'answer_nums', 'correct_nums', 'category', 'type_id', 'difficulty', 'create_on',
                         'options1_count', 'options2_count', 'options3_count', 'options4_count', 'options5_count']]
                type_id_df['type1'] = type_id_df['type1'].map(major_type_dict)
                type_id_dict = {}
                for key, value in zip(type_id_df['type_id'].tolist(), type_id_df['type1'].tolist()):
                    type_id_dict[key] = value
                major_type = pd.DataFrame(df['type_id'].map(type_id_dict))
                major_type.columns = ['major_type_id']
                df = pd.concat([df, major_type], axis=1)
                df = df.replace(np.nan, -1)
                df['create_on'] = df['create_on'].astype(str)
                rtn.result = df.to_dict(orient='records')
            elif data['get_type'] == 'all_paper_type':
                dao = StudentQuery(config)
                student_id_list = None
                if is_admin:
                    student_id_list = dao.get_all_student_id()['student_id'].to_list()
                elif is_teacher:
                    student_id_list = dao.get_all_student_id(teacher_id=_id)['student_id'].to_list()
                if not student_id_list:
                    raise Exception('no student in this teacher')
                df = dao.get_max_paper_index(student_id_list=student_id_list)[['paper_index', 'paper_type']]
                rtn.result = df.to_dict(orient='records')
            elif data['get_type'] == 'all_student':
                paper_index = request.args.get('paper_index', None)
                if not paper_index:
                    raise Exception('input date invalid')
                dao = StudentQuery(config)
                df = dao.get_student_status_by_teacher(is_admin=is_admin, teacher_id=_id)
                student_df = df[['student_id', 'ACCOUNT', 'NAME', 'class_type']]

                dao2 = UserQuery(config)
                df = dao2.get_class_type()
                class_dict = {}
                for index, row in df.iterrows():
                    class_dict[row['class_type']] = row['class_name']
                student_df['class_type'] = student_df['class_type'].map(class_dict)
                index_list = ['paper_index', 'answered_right', 'total_question', 'score', 'total_score', 'answered_on']

                dao3 = TestQuery(config)
                data = pd.DataFrame()
                for index, row in student_df.iterrows():
                    df = dao3.get_paper_status_by_paper_index(
                        student_id=row['student_id'], paper_index=int(paper_index))[index_list]
                    data = pd.concat([data,  pd.concat([student_df.iloc[index], df.T]).T])
                data.reset_index(drop=True, inplace=True)
                data['answered_on'].reset_index(drop=True, inplace=True)
                data = data.replace(np.nan, -1)
                data['answered_on'] = data['answered_on'].astype(str)
                rtn.result = data.to_dict(orient='records')

            elif data['get_type'] == 'student_status':
                student_id = request.args.get('student_id', None)
                if not student_id:
                    raise Exception('input date invalid')

                dao = StudentQuery(config)
                df = dao.get_student_status_details(student_id=student_id)

                dao2 = TestQuery(config)
                question_name_list = dao2.get_question_type()['type_name'].to_list()
                question_name_df = []
                for question_name in question_name_list:
                    question_name_df.append(f"correct_{question_name}")
                    question_name_df.append(f"answer_{question_name}")
                data = df[question_name_df]
                rtn.result = [{"student_detail": data.to_dict(orient='records')}]
                df = dao.get_student_status(student_id=student_id)
                if not df.empty:
                    df = df.replace(np.nan, -1)
                    df['answered_on'] = df['answered_on'].astype(str)
                    df['created_on'] = df['created_on'].astype(str)

                rtn.result.append({"student_paper": df.to_dict(orient='records')})
            else:
                raise Exception('input date invalid')

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
