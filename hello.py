import os
from flask import Flask

_PORT = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host='::', port=_PORT, debug=True, threaded=True)
