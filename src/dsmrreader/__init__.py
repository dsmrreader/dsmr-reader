from django.utils.version import get_version

# Some options for the fourth element:
# "beta"  - Beta release - Unstable and for internal testing
# "rc"    - Release candidate - Stable and for external pre-release testing
# "final" - Final release - Stable and tested for everyone
VERSION = (6, 1, 0, "final", 0)

__version__ = get_version(VERSION)
