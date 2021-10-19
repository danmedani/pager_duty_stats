from flask import Flask, render_template

from pager_duty_stats.api import api
app = Flask(__name__)
app.register_blueprint(api)

@app.route("/")
def homepage():
    return render_template("index.html", title="Pager Duty Stats")

@app.route("/stats")
def stats():
    return render_template("stats.html", title="Stats")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
