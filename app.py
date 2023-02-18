from flask import Flask
from flask_restx import Api
from utility.EnvLoader import load_env_file
import os
import api

app = Flask(__name__)
app.register_blueprint(api.bp, url_prefix='/api')
Api = Api(app)


if __name__ == '__main__':
    load_env_file('./env/.env')

    if os.environ['API_VERSION'] != 'v1':
        raise Exception('version required v1')

    app.run(
        host=os.environ['API_HOST'],
        port=int(os.environ['API_PORT']),
        debug=True
    )
