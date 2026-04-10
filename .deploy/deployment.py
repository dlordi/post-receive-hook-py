#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import os
import shutil
import sys


def get_deploy_info_from_repo_path(repo_path: str):
    deploy_path = repo_path  # TODO: convert to deploy path; set to None (or leave equal to repo_path) to ignore
    dry_run = True  # TODO: change to False to actually perform deployment actions
    return (deploy_path, dry_run)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    dry_run = args.dry_run

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        repo_status, repo_path = line.split('\t', 1)
        deploy_path, dry_run = get_deploy_info_from_repo_path(repo_path)
        if deploy_path in (None, repo_path):
            print(f'no deployment for {repo_path}')
            continue

        actions: list[str] = []
        deploy_path_exists = os.path.exists(deploy_path)
        if repo_status in ('A', 'M'):
            if not deploy_path_exists:
                actions.append('put')
            elif md5(repo_path) != md5(deploy_path):
                actions.append('bck')
                actions.append('put')
        elif repo_status == 'D':
            if deploy_path_exists:
                actions.append('bck')
                actions.append('del')

        if dry_run and actions:
            print('*** DRY RUN! ***')
        for action in actions:
            if action == 'bck':
                timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                print(f'backup existing {deploy_path} to {deploy_path}.{timestamp}...', end='')
                if not dry_run:
                    shutil.copy2(deploy_path, f'{deploy_path}.{timestamp}')
                print(' ok')
            elif action == 'put':
                print(f'installing {repo_path} to {deploy_path}...', end='')
                if not dry_run:
                    shutil.copy2(repo_path, deploy_path)
                print(' ok')
            elif action == 'del':
                print(f'uninstalling {repo_path} from {deploy_path}...', end='')
                if not dry_run:
                    os.remove(deploy_path)
                print(' ok')


def md5(file_path: str):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


if __name__ == '__main__':
    main()
