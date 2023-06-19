from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.test_query import TestQuery
from data_access.query.question_query import QuestionQuery
from utility.logger import get_logger
from utility.auth import token_require, get_identity


class SubmitSurvey(Resource):
    logger = get_logger('SubmitSurvey')

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
                "survey_answer_list": request.json.get("survey_answer_list", None),
                "paper_satisfaction": request.json.get('paper_satisfaction', None)
            }

            if not data["paper_id"] or not data["survey_answer_list"] or not data['paper_satisfaction']:
                raise Exception('input data missing')

            dao = TestQuery(config)
            df = dao.get_paper_status_by_paper_id(paper_id=data['paper_id'],
                                                  student_id=student_id)
            if df.empty:
                raise Exception('paper not found in db')
            if int(df['paper_satisfaction'][0]) != -1:
                raise Exception('survey already done')
            paper_index = df['paper_index'][0]

            dao2 = QuestionQuery(config)
            df = dao2.get_satisfy_type()
            satisfy_type_list = df['satisfy_type'].values.tolist()

            survey_answer_list = data['survey_answer_list']
            if data['paper_satisfaction'] not in satisfy_type_list:
                raise Exception('invalid paper_satisfaction')
            for survey_answer in survey_answer_list:
                if survey_answer not in satisfy_type_list:
                    raise Exception('invalid survey_answer')

            df = dao.get_paper_by_paper_index(student_id=student_id,
                                              paper_index=paper_index)
            question_id_list = df['question_id'].values.tolist()
            if len(question_id_list) != len(survey_answer_list):
                raise Exception("didn't answer all the question survey")
            dao.update_paper_satisfaction(paper_index=paper_index,
                                          student_id=student_id,
                                          question_id_list=question_id_list,
                                          survey_answer_list=survey_answer_list)
            dao.update_paper_status_satisfaction(paper_index=paper_index,
                                                 student_id=student_id,
                                                 paper_satisfaction=data['paper_satisfaction'])

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            self.logger.error(f"REQUEST IDENTITY: name:{student_name}, _id{student_id}, is_admin:{is_admin}, "
                              f"is_teacher:{is_teacher}")
            rtn.state = False
            rtn.msg = str(e)
        return rtn.to_dict()
