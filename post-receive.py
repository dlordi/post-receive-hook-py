import argparse
import contextlib
import datetime
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile


DEPLOYMENT_BRANCH = 'main'


def main(dry_run: bool):
    git_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    deployment_py_path = '.deploy/deployment.py'
    missing_deployment_py = subprocess.run(
        ['git', f'--git-dir={git_dir}', 'cat-file', '-e', f'{DEPLOYMENT_BRANCH}:{deployment_py_path}'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode
    if missing_deployment_py:
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        status_lines = checkout(tmp_dir, git_dir, deployment_py_path)
        if not status_lines:
            return

        mode = '*** DRY RUN! *** ' if dry_run else ''
        print(f'{mode}running deployment using temporary directory "{tmp_dir}"...', flush=True)

        with contextlib.chdir(tmp_dir):
            spec = importlib.util.spec_from_file_location('deployment', os.path.join(*deployment_py_path.split('/')))
            sys.modules['deployment'] = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sys.modules['deployment'])

            deploy(dry_run, status_lines, sys.modules['deployment'].get_deploy_info_from_repo_path)


def checkout(tmp_dir: str, git_dir: str, deployment_py_path: str):
    status_lines: list[str] = []
    checkout_files: list[tuple[str, str]] = []

    for line in sys.stdin:
        if not line.strip():
            continue

        oldrev, newrev, refname = line.strip().split()
        if refname.startswith('refs/heads/'):
            branch = refname.split('/', 2)[-1]
            if branch != DEPLOYMENT_BRANCH:
                continue

        diff_file_lines = subprocess.run(
            ['git', f'--work-tree={tmp_dir}', f'--git-dir={git_dir}', 'diff', '--name-status', oldrev if oldrev != '0' * 40 else '--root', newrev],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.splitlines()
        for diff_file_line in diff_file_lines:
            print(diff_file_line) # TODO: remove me
            status, repo_path = diff_file_line.split('\t', 1)
            if status in ('A', 'M'):
                checkout_files.append((newrev, repo_path))
            if repo_path.startswith('.deploy'):
                continue
            status_lines.append(diff_file_line)

    if status_lines:
        # TODO: add all files in .deploy directory
        checkout_files.append((None, deployment_py_path))
        for _, checkout_file in checkout_files:
            subprocess.run(
                ['git', f'--work-tree={tmp_dir}', f'--git-dir={git_dir}', 'checkout', '-f', DEPLOYMENT_BRANCH, '--', checkout_file],
                check=True,
            )
    return status_lines


def deploy(dry_run: bool, status_lines, get_deploy_path_from_repo_path):
    mode = '*** DRY RUN! *** ' if dry_run else ''

    for line in status_lines:
        line = line.strip()
        if not line:
            continue

        repo_status, repo_path = line.split('\t', 1)
        deploy_path = get_deploy_path_from_repo_path(repo_path)
        if deploy_path in (None, repo_path):
            print(f'{mode}no deployment for {repo_path}', flush=True)
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

        for action in actions:
            if action == 'bck':
                timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                print(f'{mode}backup existing {deploy_path} to {deploy_path}.{timestamp}...', end='', flush=True)
                if not dry_run:
                    shutil.copy2(deploy_path, f'{deploy_path}.{timestamp}')
                print(' ok', flush=True)
            elif action == 'put':
                print(f'{mode}installing {repo_path} to {deploy_path}...', end='', flush=True)
                if not dry_run:
                    makedirs(os.path.dirname(deploy_path))
                    shutil.copy2(repo_path, deploy_path)
                print(' ok', flush=True)
            elif action == 'del':
                print(f'{mode}uninstalling {repo_path} from {deploy_path}...', end='', flush=True)
                if not dry_run:
                    os.remove(deploy_path)
                print(' ok', flush=True)


def md5(file_path: str):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def makedirs(dirs: str):
    if dirs:
        os.makedirs(dirs, exist_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    sys.exit(main(args.dry_run) or 0)
