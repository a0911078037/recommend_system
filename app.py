from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from utility.EnvLoader import load_env_file
import api
import platform

config = load_env_file('./env/api_config.yml')


if __name__ == '__main__':
    if platform.system() == 'Linux':
        import bjoern
    app = Flask(__name__)
    app.register_blueprint(api.bp, url_prefix='/api')
    CORS(app)
    Api = Api(app)

    if config['API']['VERSION'] != 'v1':
        raise Exception('version required v1')

    if platform.system() == 'Linux':
        bjoern.run(app, "0.0.0.0", 8000)
    elif platform.system() == 'Windows':
        app.run(
            host=config['API']['IP'],
            port=int(config['API']['PORT']),
            debug=True,
            use_reloader=False
        )
    else:
        raise Exception('os not supported')
