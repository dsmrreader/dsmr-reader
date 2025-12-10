from io import StringIO
from typing import Tuple

from django.core.management import call_command


class InterceptCommandStdoutMixin:
    def _intercept_command_stdout(self, command: str, *args, **kwargs) -> str:
        """Suppresses stderr for tests. Returns stdout."""
        stdout = StringIO()
        stderr = StringIO()
        call_command(command, *args, stdout=stdout, stderr=stderr, **kwargs)  # noqa: B026
        stdout.seek(0)
        return stdout.read()

    def _intercept_command(self, command: str, *args, **kwargs) -> Tuple[str, str]:
        """Returns stdout and stderr."""
        stdout = StringIO()
        stderr = StringIO()
        call_command(command, *args, stdout=stdout, stderr=stderr, **kwargs)  # noqa: B026
        stdout.seek(0)
        stderr.seek(0)

        return stdout.read(), stderr.read()
