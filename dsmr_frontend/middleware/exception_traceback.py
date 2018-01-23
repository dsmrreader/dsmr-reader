import traceback

from django.http.response import HttpResponseServerError
from django.template.loader import render_to_string
from django.conf import settings


class ExceptionTracebackMiddleware(object):
    """ Handles any uncaught exceptions crashing the webinterface, and displays them. """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        if settings.DEBUG:
            # Default exception handling, which is already nice when in DEBUG mode.
            return

        return HttpResponseServerError(
            render_to_string(
                '500.html', {
                    'exception': exception,
                    'exception_class': exception.__class__.__name__,
                    'error_trace': traceback.format_tb(exception.__traceback__, limit=100)
                }
            )
        )
