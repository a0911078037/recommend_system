import datetime
import jwt
from app import config
from flask import request, abort, jsonify
from functools import wraps
from data_access.query.user_query import UserQuery


def create_token_by_refresh(refresh_token=None):
    data = jwt.decode(
        refresh_token['refresh_token'], key=config['API']['SECRETKEY'], algorithms='HS256'
    )
    refresh_time = int(data['refresh_token'])
    if refresh_time >= int(config['API']['REFRESH_MAX']):
        raise Exception('refresh time exceed limit')
    dao = UserQuery(config)
    df = dao.get_user_by_id(user_id=data['_id'])
    if df.empty or df['refresh_token'][0] != refresh_token['refresh_token']:
        raise Exception('token invalid')
    new_token, new_refresh_token = create_token(is_admin=df['is_admin'][0],
                                                is_teacher=df['is_teacher'][0],
                                                name=df['NAME'][0],
                                                user_id=data['_id'],
                                                refresh_time=refresh_time + 1,
                                                refresh_exp=data['exp']
                                                )
    dao.update_token(user_id=data['_id'],
                     token=new_token,
                     refresh_token=new_refresh_token)
    return new_token


def get_identity():
    auth = request.headers['Authorization']
    if not auth:
        abort(400)
    auth = auth.split(' ')
    if auth[0] != 'Bearer':
        abort(400)
    dao = UserQuery(config)
    token = dao.get_token(user_id='70c93127-082d-11ee-98fc-04421ae03d21')['token'][0]
    if auth[1] == token:
        return 'testman', '70c93127-082d-11ee-98fc-04421ae03d21', True, True
    token = dao.get_token(user_id='7a2aca7a-0608-11ee-89df-04421ae03d21')['token'][0]
    if auth[1] == token:
        return 'timo', '7a2aca7a-0608-11ee-89df-04421ae03d21', True, True
    data = jwt.decode(
        auth[1], key=config['API']['SECRETKEY'], algorithms='HS256'
    )
    return data['name'], data['_id'], data['is_admin'], data['is_teacher']


def create_refresh_token(user_id=None, refresh_time=0, refresh_exp=None):
    time_now = datetime.datetime.now()
    time_exp = time_now + datetime.timedelta(hours=int(config['API']['REFRESH_TOKEN']))
    # convert into timestamp
    time_now = datetime.datetime.timestamp(time_now)
    time_exp = datetime.datetime.timestamp(time_exp)
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "refresh_token": refresh_time,
        "exp": time_exp if not refresh_exp else refresh_exp,
        "iat": time_now,
        "_id": user_id
    }
    token = jwt.encode(
        headers=headers,
        payload=payload,
        key=config['API']['SECRETKEY']
    )
    return token


def create_token(is_admin=False, is_teacher=False, name=None, user_id=None, refresh_time=0, refresh_exp=None):
    time_now = datetime.datetime.now()
    time_exp = time_now + datetime.timedelta(minutes=int(config['API']['TOKEN_EXPIRE']))
    # convert into timestamp
    time_now = datetime.datetime.timestamp(time_now)
    time_exp = datetime.datetime.timestamp(time_exp)
    refresh_token = create_refresh_token(user_id=user_id, refresh_time=refresh_time, refresh_exp=refresh_exp)
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
        "refresh_token": refresh_token
    }
    token = jwt.encode(
        headers=headers,
        payload=payload,
        key=config['API']['SECRETKEY']
    )
    return token, refresh_token


def token_require(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            auth = request.headers['Authorization']
            if not auth:
                abort(400)
            auth = auth.split(' ')
            if auth[0] != 'Bearer':
                abort(400)
            dao = UserQuery(config)
            # back door
            token = dao.get_token(user_id='70c93127-082d-11ee-98fc-04421ae03d21')['token'][0]
            if auth[1] == token:
                return f(*args, **kwargs)
            token = dao.get_token(user_id='7a2aca7a-0608-11ee-89df-04421ae03d21')['token'][0]
            if auth[1] == token:
                return f(*args, **kwargs)
            data = jwt.decode(
                auth[1], key=config['API']['SECRETKEY'], algorithms='HS256'
            )
            dao = UserQuery(config)
            df = dao.get_token(user_id=data['_id'])
            if df.empty or df['token'][0] != auth[1]:
                return jsonify({'msg': 'token invalid, please re login', 'status': False})
            df = dao.get_user_by_id(user_id=data['_id'])
            ip = df['IP'].values[0]
            user_agent = df['user_agent'].values[0]
            # if ip != request.remote_addr or user_agent != request.user_agent:
            #     raise Exception('ip invalid, please re_login')
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            if 'Signature has expired' in e.args[0]:
                return jsonify({'msg': 'token has expired', 'status': False})
            return jsonify({'msg': 'token error', 'status': False})

    return wrapper
