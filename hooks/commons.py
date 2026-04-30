import contextlib
import datetime
import hashlib
import importlib.util
import os
import shutil
import sys
import tempfile
import typing


DEPLOYMENT_BRANCH = 'main'


def deploy(dry_run, checkout, git_dir, deployment_py_path):
    with tempfile.TemporaryDirectory() as tmp_dir:
        status_lines = checkout(tmp_dir, git_dir, deployment_py_path)
        if not status_lines:
            return

        dry_run_descr = '*** DRY RUN! *** ' if dry_run else ''
        print(f'{dry_run_descr}running deployment using temporary directory "{tmp_dir}"...', flush=True)

        with contextlib.chdir(tmp_dir):
            spec = importlib.util.spec_from_file_location('deployment', os.path.join(*deployment_py_path.split('/')))
            if (not spec) or (not spec.loader):
                print('ERROR: unable to import deploy', file=sys.stderr, flush=True)
                raise Exception(f'unable to import "{deployment_py_path}"')
            sys.modules['deployment'] = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sys.modules['deployment'])

            for line in status_lines:
                line = line.strip()
                if not line:
                    continue

                deploy_one(dry_run, dry_run_descr, line, sys.modules['deployment'].get_deploy_info_from_repo_path)


def deploy_one(dry_run: bool, dry_run_descr: str, line: str, get_deploy_path_from_repo_path: typing.Callable[[str], str]):
    repo_status, repo_path = line.split('\t', 1)
    deploy_path = get_deploy_path_from_repo_path(repo_path)
    if deploy_path in (None, repo_path):
        print(f'{dry_run_descr}no deployment for {repo_path}', flush=True)
        return

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

    for action in actions:
        if action == 'bck':
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            print(f'{dry_run_descr}backup existing {deploy_path} to {deploy_path}.{timestamp}...', end='', flush=True)
            if not dry_run:
                shutil.copy2(deploy_path, f'{deploy_path}.{timestamp}')
            print(' ok', flush=True)
        elif action == 'put':
            print(f'{dry_run_descr}installing {repo_path} to {deploy_path}...', end='', flush=True)
            if not dry_run:
                makedirs(os.path.dirname(deploy_path))
                shutil.copy2(repo_path, deploy_path)
            print(' ok', flush=True)
        elif action == 'del':
            print(f'{dry_run_descr}uninstalling {repo_path} from {deploy_path}...', end='', flush=True)
            if not dry_run:
                os.remove(deploy_path)
            print(' ok', flush=True)


def md5(file_path: str):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def makedirs(dirs: str):
    if dirs:
        os.makedirs(dirs, exist_ok=True)
