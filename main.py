from flask import Flask
from api import api_bp

# Initialize Flask app
app = Flask(__name__)

app.register_blueprint(api_bp, url_prefix='/api')

@app.route("/")
def hello_world():
    return "<p>Agent Ops backend is running!</p>"

app.run("0.0.0.0", debug=True)