import os
from flask import Flask

_port = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_msg  = "Hello, World!" if (os.environ.get("MESSAGE") is None) else os.environ.get("MESSAGE")

app = Flask(__name__)

@app.route('/')
def hello():
    return "{}".format(_msg)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
