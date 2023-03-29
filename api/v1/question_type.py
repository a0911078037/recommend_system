from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
from utility.logger import get_logger


class QuestionType(Resource):
    logger = get_logger('QuestionType')

    def get(self):
        rtn = RtnMessage()
        try:
            data = {
                "major_type_id": request.args.get('major_type_id', None),
                "type_id": request.args.get('type_id', None)
            }
            dao = QuestionQuery(config)
            df = dao.get_question_type()
            df['type'] = df['type'].astype(str)
            type_name_list = df['type_name'].to_list()
            df_2 = dao.get_question_type_by_type_id(type_name_list=type_name_list,
                                                    type_id=data['type_id'])

            if data['major_type_id']:
                type_name = df[df['type'] == data['major_type_id']]['type_name'].to_list()
                if not type_name:
                    return rtn.to_dict()
                type_name = type_name[0]
                rtn.result.append(
                    {
                        "major_type": df[df['type'] == data['major_type_id']]['type_name'].to_list()[0],
                        "question_type":
                            df_2[df_2['type1'] == type_name].to_dict(orient='records')
                    }
                )
                return rtn.to_dict()
            if data['type_id']:
                rtn.result.append(
                    df_2.to_dict(orient='records')
                )
                return rtn.to_dict()
            rtn.result.append(
                {
                    "question_type": df_2.to_dict(orient='records'),
                    "major_question_type": df.to_dict(orient='records')
                }
            )

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
