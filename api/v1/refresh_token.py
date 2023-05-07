from flask_restx import Resource
from utility.RtnMessage import RtnMessage
from utility.logger import get_logger
from flask import request
from utility.auth import create_token_by_refresh


class RefreshToken(Resource):
    logger = get_logger('refresh_token')

    def post(self):
        rtn = RtnMessage()
        try:
            refresh_token = request.json['refresh_token']
            new_token = create_token_by_refresh(refresh_token=refresh_token)
            rtn.result.append(
                {
                    "token": new_token
                }
            )
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
