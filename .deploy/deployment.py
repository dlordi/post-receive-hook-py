#!/usr/bin/env python3

import datetime
import os
# import shutil
import sys


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        repo_status, repo_path = line.split('\t', 1)
        deploy_path = get_deploy_path_from_repo_path(repo_path)
        deploy_path_exists = os.path.exists(deploy_path)
        if deploy_path_exists:
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            print(f'TODO: backup existing {deploy_path} to {deploy_path}.{timestamp}...')
            # shutil.copy2(deploy_path, f'{deploy_path}.{timestamp}')

        if repo_status in ('A', 'M'):
            print(f'TODO: installing {repo_path} to {deploy_path}...')
            # shutil.copy2(repo_path, deploy_path)
        elif repo_status == 'D':
            print(f'TODO: uninstalling {repo_path} from {deploy_path}...')
            # if deploy_path_exists:
            #     os.remove(deploy_path_exists)


def get_deploy_path_from_repo_path(repopath):
    print('TODO: convert {repopath} to deployment path...')
    return repopath


if __name__ == '__main__':
    main()
