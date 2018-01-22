from io import StringIO

from django.core.management import call_command


class InterceptStdoutMixin(object):
    """ Supresses stdout for tests. Returns stdout. """
    def _intercept_command_stdout(self, command, **kwargs):
        stdout = StringIO()
        stderr = StringIO()  # Only to mute.
        call_command(command, stdout=stdout, stderr=stderr, **kwargs)
        stdout.seek(0)
        return stdout.read()
