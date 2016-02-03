from io import StringIO

from django.core.management import call_command


class CallCommandStdoutMixin(object):
    """ Supresses stdout for tests. Returns stdout. """
    def _call_command_stdout(self, command, **kwargs):
        stdout = StringIO()
        call_command(command, stdout=stdout, **kwargs)
        stdout.seek(0)
        return stdout.read()
