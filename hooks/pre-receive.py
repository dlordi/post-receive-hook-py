import argparse
import os
import subprocess
import sys


import commons


def main(dry_run: bool):
    git_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    deployment_py_path = '.deploy/deployment.py'

    commons.deploy(dry_run, checkout, git_dir, deployment_py_path)


def checkout(tmp_dir: str, git_dir: str, deployment_py_path: str):
    status_lines: list[str] = []
    checkout_files: list[tuple[str, str]] = []

    for line in sys.stdin:
        if not line.strip():
            continue

        oldrev, newrev, refname = line.strip().split()
        if refname.startswith('refs/heads/'):
            branch = refname.split('/', 2)[-1]
            if branch != commons.DEPLOYMENT_BRANCH:
                continue

        diff_file_lines = subprocess.run(
            [
                'git',
                f'--work-tree={tmp_dir}',
                f'--git-dir={git_dir}',
                'diff',
                '--name-status',
                oldrev if oldrev != '0' * 40 else '--root',
                newrev,
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.splitlines()
        for diff_file_line in diff_file_lines:
            status, repo_path = diff_file_line.split('\t', 1)
            if status in ('A', 'M'):
                checkout_files.append((newrev, repo_path))
            if repo_path.startswith('.deploy'):
                continue
            status_lines.append(diff_file_line)

    if status_lines:
        # TODO: extract all files in the .deploy directory
        for rev, checkout_file in checkout_files:
            if checkout_file == deployment_py_path:
                break
        else:
            missing_deployment_py = subprocess.run(
                [
                    'git',
                    f'--work-tree={tmp_dir}',
                    f'--git-dir={git_dir}',
                    'cat-file',
                    '-e',
                    f'{commons.DEPLOYMENT_BRANCH}:{deployment_py_path}',
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            if missing_deployment_py:
                return
            subprocess.run(
                [
                    'git',
                    f'--work-tree={tmp_dir}',
                    f'--git-dir={git_dir}',
                    'checkout',
                    '-f',
                    commons.DEPLOYMENT_BRANCH,
                    '--',
                    deployment_py_path,
                ],
                check=True,
            )
        for rev, checkout_file in checkout_files:
            checkout_path = os.path.join(tmp_dir, checkout_file)
            commons.makedirs(os.path.dirname(checkout_path))
            with open(checkout_path, 'w') as f:
                subprocess.run(
                    ['git', f'--git-dir={git_dir}', 'show', f'{rev}:{checkout_file}'],
                    check=True,
                    stdout=f,
                )
    return status_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    sys.exit(main(args.dry_run) or 0)
