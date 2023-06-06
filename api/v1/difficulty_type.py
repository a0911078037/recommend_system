from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
from utility.logger import get_logger


class DifficultyType(Resource):
    logger = get_logger('DifficultyType')

    def get(self):
        rtn = RtnMessage()
        data = None
        try:
            data = {
                "type_id": request.args.get('type_id', None)
            }
            dao = QuestionQuery(config)
            df = dao.get_difficulty_type(type_id=data['type_id'])
            rtn.result.append(
                df.to_dict(orient='records')
            )

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
