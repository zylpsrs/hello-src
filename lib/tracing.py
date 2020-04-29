import os
import sys
import logging
from flask import request, session
from flask import _request_ctx_stack as stack

from opentracing.ext import tags
from opentracing.propagation import Format
from opentracing_instrumentation.request_context import get_current_span, span_in_context

from jaeger_client import Config

# ref: https://www.jaegertracing.io/docs/1.17/client-features
_RPC = False if (os.environ.get("JAEGER_ONE_SPAN_PER_RPC") is None) else os.environ.get("JAEGER_ONE_SPAN_PER_RPC")

# ref: https://github.com/jaegertracing/jaeger-client-python
#      https://github.com/yurishkuro/opentracing-tutorial/tree/master/python
def init_jaeger_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'propagation': 'b3',
            'logging': True,
            'reporter_batch_size': 1,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    tracer = config.initialize_tracer()

    # Zipkin shares span ID between client and server spans; 
    # it must be enabled via the following option.
    # when call start_span, it will set:
    #     span_id = parent.span_id
    #     parent_id = parent.parent_id
    tracer.one_span_per_rpc = _RPC

    return tracer

# A note on distributed tracing:
#
# Although Istio proxies are able to automatically send spans, they need some
# hints to tie together the entire trace. Applications need to propagate the
# appropriate HTTP headers so that when the proxies send span information, the
# spans can be correlated correctly into a single trace.
#
# To do this, an application needs to collect and propagate the following
# headers from the incoming request to any outgoing requests:
#
# x-request-id
# x-b3-traceid
# x-b3-spanid
# x-b3-parentspanid
# x-b3-sampled
# x-b3-flags
#
# This example code uses OpenTracing (http://opentracing.io/) to propagate
# the 'b3' (zipkin) headers. Using OpenTracing for this is not a requirement.
# Using OpenTracing allows you to add application-specific tracing later on,
# but you can just manually forward the headers if you prefer.
#
# The OpenTracing example here is very basic. It only forwards headers. It is
# intended as a reference to help people get started, eg how to create spans,
# extract/inject context, etc.

def flask_top_request_trace(tracer, op_name):
    '''
    Function decorator that creates opentracing span from incoming b3 headers
    '''
    def decorator(f):
        def wrapper(*args, **kwargs):
            request = stack.top.request
            try:
                # Create a new span context, reading in values (traceid,
                # spanid, etc) from the incoming x-b3-*** headers.
                p_span = tracer.extract(Format.HTTP_HEADERS, dict(request.headers))

                # Note: this tag means that the span will *not* be
                # a child span. It will use the incoming traceid and
                # spanid. We do this to propagate the headers verbatim.
                rpc_tag = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
                c_span = tracer.start_span(operation_name=op_name, child_of=p_span, tag=rpc_tag)

                c_span.set_tag(tags.HTTP_METHOD, request.method)
                c_span.set_tag(tags.HTTP_URL, request.base_url)
            except Exception as e:
                # We failed to create a context, possibly due to no
                # incoming x-b3-*** headers. Start a fresh span.
                c_span = tracer.start_span(op_name)
                c_span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)

            # current jaeger-client <4.3 not support baggage when using b3codec
            # ref: https://github.com/jaegertracing/jaeger/issues/755
            # when call inject and extrat method, the baggage will missing
            #val = c_span.get_baggage_item('user-agent')
            #if val is None:
            #   val = request.headers.get('user-agent')
            #   c_span.set_baggage_item('user-agent', val)

            with span_in_context(c_span):
                r = f(*args, **kwargs)
                c_span.finish()
                return r
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def flask_child_method_trace(tracer, op_name):
    def decorator(f):
        def wrapper(*args, **kwargs):
            p_span = get_current_span()
            c_span = tracer.start_span(operation_name=op_name, child_of=p_span)

            with span_in_context(c_span):
                r = f(*args, **kwargs)
                c_span.finish()
                return r
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ref: https://github.com/istio/istio/blob/master/samples/bookinfo/src/productpage/productpage.py
def get_forward_http_headers(tracer):
    headers = {}

    # only x-b3-*** headers can be populated
    span = get_current_span()
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    tracer.inject(span_context=span.context, format=Format.HTTP_HEADERS, carrier=headers)

    # We handle other (non x-b3-***) headers manually
    if 'user' in session:
        headers['end-user'] = session['user']

    # Add user-agent to headers manually
    if 'user-agent' in request.headers:
        headers['user-agent'] = request.headers.get('user-agent')

    incoming_headers = ['x-request-id', 'x-datadog-trace-id', 
                        'x-datadog-parent-id', 'x-datadog-sampled']

    for ihdr in incoming_headers:
        val = request.headers.get(ihdr)
        if val is not None:
            headers[ihdr] = val
            #print("incoming: "+ihdr+":"+val)

    return headers
