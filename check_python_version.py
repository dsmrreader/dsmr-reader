#!/usr/bin/env python3
import sys

# EOL table @ https://www.python.org/downloads/
MINIMUM_VERSION = (3, 6, 0)
PREFERRED_MINIMUM_VERSION = (3, 7, 0)


def check():
    print('Running Python', sys.version)

    if sys.version_info < MINIMUM_VERSION:
        print('[!] Python version unsupported. Minimum version required: {}'.format(
            '.'.join([str(x) for x in MINIMUM_VERSION])
        ))
        sys.exit(1)

    # Deprecation.
    if sys.version_info < PREFERRED_MINIMUM_VERSION:
        print('[WARNING] Python version is deprecated. Preferred version for DSMR-reader is {} or higher.'.format(
            '.'.join([str(x) for x in PREFERRED_MINIMUM_VERSION])
        ))


if __name__ == '__main__':
    check()
    sys.exit(0)
