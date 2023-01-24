from flask import Flask, render_template
from config import config
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/user')
def user():
    return render_template('user.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config['web_server_port'])