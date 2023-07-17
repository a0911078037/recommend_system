from flask_restx import Resource
from utility.RtnMessage import RtnMessage
from utility.logger import get_logger
from flask import request
from utility.auth import create_token_by_refresh
import jwt
from app import config


class RefreshToken(Resource):
    logger = get_logger('refresh_token')

    def post(self):
        rtn = RtnMessage()
        data = None
        try:
            data = {
                "refresh_token": request.json.get('refresh_token', None)
            }
            if not data['refresh_token']:
                raise Exception('input data missing')
            refresh_token = jwt.decode(
                data['refresh_token'], key=config['API']['SECRETKEY'], algorithms='HS256'
            )
            new_token = create_token_by_refresh(refresh_token=refresh_token)
            rtn.result.append(
                {
                    "token": new_token
                }
            )
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
