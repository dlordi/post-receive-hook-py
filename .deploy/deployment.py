#!/usr/bin/env python3

import datetime
import os
import sys


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        status, path = line.split('\t', 1)
        if os.path.exists(path):
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            print(f'backup existing {path} to {path}.{timestamp}...')
        if status in ('A', 'M'):
            print(f'installing {path}...')
        elif status == 'D':
            print(f'deleting {path}...')


if __name__ == '__main__':
    main()
