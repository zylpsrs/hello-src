FROM registry.ocp.zyl.io:5000/python:3.7.4-slim

WORKDIR /app

COPY requirements.txt ./

ENV INDEX_URL https://mirrors.aliyun.com/pypi/simple
RUN pip install -i $INDEX_URL --no-cache-dir -r requirements.txt

COPY lib/tracing.py ./lib/tracing.py
COPY hello.py ./

ENV PORT 9080

EXPOSE $PORT
ENTRYPOINT ["python", "hello.py"]
