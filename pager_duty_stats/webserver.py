from flask import request
from flask import Flask

app = Flask(__name__, static_folder='../ui/dist/', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('chart.html')
