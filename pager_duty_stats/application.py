import os

from functools import lru_cache
from dotenv import load_dotenv
from flask import Flask
from flask import redirect
from flask import request

from pager_duty_stats.api import api

application = Flask(__name__, static_folder='../ui/dist/', static_url_path='')
application.register_blueprint(api)


@lru_cache(maxsize=1)
def is_prod():
   return not application.config['ENV'] == 'development' 


# ----- Configuration ----- #
print(application.config['ENV'])
if not is_prod():
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '.env'))


@application.before_request
def reroute_http_to_https():
    if not request.is_secure and is_prod():
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


# ----- Static Pages ----- #
@application.route('/')
def get_index():
    return application.send_static_file('index.html')


@application.route('/stats')
def get_stats():
    return application.send_static_file('stats.html')


# ----- Run the thing ----- #
if __name__ == "__main__":
    if not is_prod():
        application.debug = True

def create_app():
   return application
    # waitress-serve --port 5000 --url-scheme=http --call pager_duty_stats.application:create_app
