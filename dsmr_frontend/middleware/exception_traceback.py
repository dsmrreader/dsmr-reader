import traceback

from django.http.response import HttpResponseServerError
from django.template.loader import render_to_string


class ExceptionTracebackMiddleware(object):
    """ Handles any uncaught exceptions crashing the webinterface, and displays them. """
    def process_exception(self, request, exception):
        return HttpResponseServerError(
            render_to_string(
                '500.html', {
                    'exception': exception,
                    'exception_class': exception.__class__.__name__,
                    'error_trace': traceback.format_tb(exception.__traceback__, limit=100)
                }
            )
        )
