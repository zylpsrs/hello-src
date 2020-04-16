import sys
import logging
import functools
from os import getenv
from jaeger_client import Config

from flask import _request_ctx_stack as stack
from flask import request, session

from opentracing.ext import tags
from opentracing.propagation import Format
from opentracing_instrumentation.request_context import get_current_span, span_in_context

def http_debug(app):
    try:
        import http.client as http_client
    except ImportError:
        import httplib as http_client

    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.DEBUG)

JAEGER_AGENT_HOST = getenv('JAEGER_AGENT_HOST', 'localhost')
JAEGER_AGENT_PORT = getenv('JAEGER_AGENT_PORT', 6831)
JAEGER_SAMPLING_PORT = getenv('JAEGER_SAMPLING_PORT', 6832)

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': JAEGER_AGENT_HOST,
                'reporting_port': JAEGER_AGENT_PORT,
                'sampling_port': JAEGER_SAMPLING_PORT
            },
            'propagation': 'b3',
            'logging': True,
            'reporter_batch_size': 1,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

def local_trace(tracer, op_name, tag={}, log={}):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with tracer.start_active_span(op_name) as scope:
                for key,value in tag.items():
                    scope.span.set_tag(key,value)

                if log:
                    scope.span.log_kv(log)

                r = f(*args, **kwargs)
                return r
        return wrapper
    return decorator

def http_trace(tracer, op_name, tag={}, log={}):
    def decorator(f):
        def wrapper(*args, **kwargs):
            request = stack.top.request
            try:
                rpc_tag = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
                span_ctx = tracer.extract(Format.HTTP_HEADERS, dict(request.headers))
                span = tracer.start_span(
                     operation_name=op_name, child_of=span_ctx)
            except Exception as e:
                span = tracer.start_span(operation_name=op_name)

            with span_in_context(span):
                for key,value in tag.items():
                    scope.span.set_tag(key,value)

                if log:
                    scope.span.log_kv(log)

                r = f(*args, **kwargs)
                span.finish()
                return r

        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def get_forward_http_headers(tracer, tag={}):
    headers = {}
    span = get_current_span()
    for key,value in tag.items():
        span.set_tag(key,value)
    tracer.inject(span_context=span.context,format=Format.HTTP_HEADERS,carrier=headers)

    if 'user' in session:
        headers['end-user'] = session['user']

    incoming_headers = ['x-request-id', 'x-datadog-trace-id', 'x-datadog-parent-id', 'x-datadog-sampled']

    if 'user-agent' in request.headers:
        headers['user-agent'] = request.headers.get('user-agent')

    for ihdr in incoming_headers:
        val = request.headers.get(ihdr)
        if val is not None:
            headers[ihdr] = val

    return headers
