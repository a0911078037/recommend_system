import datetime
import jwt
from app import config
from flask import request, abort, jsonify
from functools import wraps
from data_access.query.user_query import UserQuery


def create_token_by_refresh(refresh_token=None):
    data = jwt.decode(
        refresh_token, key=config['API']['SECRETKEY'], algorithms='HS256'
    )
    refresh_time = data['refresh_token']
    if refresh_time >= config['API']['REFRESH_MAX']:
        raise Exception('refresh time exceed limit')
    dao = UserQuery(config)
    df = dao.get_user_by_id(user_id=data['_id'])
    new_token = create_token(is_admin=df['is_admin'][0],
                             is_teacher=df['is_teacher'][0],
                             name=df['NAME'][0],
                             user_id=data['_id'],
                             refresh_time=refresh_time + 1
                             )
    dao.update_token(user_id=data['_id'],
                     token=new_token)
    return new_token


def get_identity():
    auth = request.headers['Authorization'].split(' ')
    if auth[0] != 'Bearer':
        abort(400)
    data = jwt.decode(
        auth[1], key=config['API']['SECRETKEY'], algorithms='HS256'
    )
    return data['name'], data['_id'], data['is_admin'], data['is_teacher']


def create_refresh_token(user_id=None, refresh_time=0):
    time_now = datetime.datetime.now()
    time_exp = time_now + datetime.timedelta(hours=int(config['API']['TOKEN_EXPIRE']))
    # convert into timestamp
    time_now = datetime.datetime.timestamp(time_now)
    time_exp = datetime.datetime.timestamp(time_exp)
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "refresh_token": refresh_time,
        "exp": time_exp,
        "iat": time_now,
        "_id": user_id
    }
    token = jwt.encode(
        headers=headers,
        payload=payload,
        key=config['API']['SECRETKEY']
    )
    return token


def create_token(is_admin=False, is_teacher=False, name=None, user_id=None, refresh_time=0):
    time_now = datetime.datetime.now()
    time_exp = time_now + datetime.timedelta(minutes=int(config['API']['TOKEN_EXPIRE']))
    # convert into timestamp
    time_now = datetime.datetime.timestamp(time_now)
    time_exp = datetime.datetime.timestamp(time_exp)
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "name": name,
        "_id": user_id,
        "exp": time_exp,
        "iat": time_now,
        "is_admin": bool(is_admin),
        "is_teacher": bool(is_teacher),
        "refresh_token": create_refresh_token(user_id=user_id, refresh_time=refresh_time)
    }
    token = jwt.encode(
        headers=headers,
        payload=payload,
        key=config['API']['SECRETKEY']
    )
    return token


def token_require(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers['Authorization'].split(' ')
        if auth[0] != 'Bearer':
            abort(400)
        data = jwt.decode(
            auth[1], key=config['API']['SECRETKEY'], algorithms='HS256'
        )
        dao = UserQuery(config)
        df = dao.get_token(user_id=data['_id'])
        if df['token'][0] != auth[1]:
            return jsonify({'msg': 'token invalid, please re login'})
        return f(*args, **kwargs)

    return wrapper
