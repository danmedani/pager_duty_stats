from flask import request
from flask import Flask

app = Flask(__name__, static_folder='web/')

@app.route('/')
def index():
    return """
<h1>Weclome to Pager Duty Stats v0.1</h1>

<form action="/view_graph" method="post">
  Service ID <input type="text" name="service_id"></input>
  Start Date <input type="text" name="start_date"></input>
  Grouping Window <input type="text" name="grouping_window"></input>
  <input type="submit" value="View Graph"></input>
</form>

"""

@app.route('/view_graph', methods = ['POST'])
def view_graph():
    service_id = request.form['service_id']
    start_date = request.form['start_date']
    grouping_window = request.form['grouping_window']
    return app.send_static_file('chart.html')