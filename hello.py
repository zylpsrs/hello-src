import os
import time
import random
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

_port = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_msg  = "Hello, World!" if (os.environ.get("MESSAGE") is None) else os.environ.get("MESSAGE")

app = Flask(__name__)
PrometheusMetrics(app)

@app.route('/')
def hello():
    time.sleep(random.random())
    return "{}".format(_msg)

if __name__ == "__main__":
    app.run(host='::', port=_port, threaded=True)
