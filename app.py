from flask import Flask
from flask_restx import Api
from utility.EnvLoader import load_env_file
from flask_jwt_extended import JWTManager
import api
from datetime import timedelta

config = load_env_file('./env/api_config.yml')


if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(api.bp, url_prefix='/api')
    app.config["JWT_SECRET_KEY"] = config['API']['SECRETKEY']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)
    JWTManager(app)
    Api = Api(app)

    if config['API']['VERSION'] != 'v1':
        raise Exception('version required v1')

    app.run(
        host=config['API']['IP'],
        port=int(config['API']['PORT']),
        debug=True
    )
