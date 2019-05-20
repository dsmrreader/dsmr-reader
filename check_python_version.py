#!/usr/bin/env python3
import sys


MINIMUM_VERSION = (3, 5, 0)


def check():
    print('Running Python', sys.version)

    if sys.version_info < MINIMUM_VERSION:
        print('[!] Python version unsupported. Minimum version required:', '.'.join([str(x) for x in MINIMUM_VERSION]))
        sys.exit(1)


if __name__ == '__main__':
    check()
    sys.exit(0)
