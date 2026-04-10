import os
import subprocess
import tempfile
import sys

git_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
deployment_py_path = '.deploy/deployment.py'

with tempfile.TemporaryDirectory() as tmp_dir:
    status_lines: list[str] = []
    checkout_files: list[tuple[str, str]] = []
    for line in sys.stdin:
        if not line.strip():
            continue
        oldrev, newrev, refname = line.strip().split()
        diff = subprocess.run(
            [
                'git',
                f'--git-dir={git_dir}',
                'diff',
                '--name-status',
                oldrev if oldrev != '0' * 40 else '--root',
                newrev,
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        for file_line in diff.stdout.splitlines():
            status, path = file_line.split('\t', 1)
            status_lines.append(file_line)
            if status in ('A', 'M'):
                checkout_files.append((newrev, path))
    flag = False
    for rev, checkout_file in checkout_files:
        if checkout_file == deployment_py_path:
            flag = True
        subprocess.run(
            ['git', f'--git-dir={git_dir}', 'show', f'{rev}:{checkout_file}'],
            check=True,
        )
    if not flag:
        result = subprocess.run(
            ['git', f'--git-dir={git_dir}', 'cat-file', '-e', f'main:{deployment_py_path}'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        flag = not result.returncode
        if flag:
            subprocess.run(
                [
                    'git',
                    f'--work-tree={tmp_dir}',
                    f'--git-dir={git_dir}',
                    'checkout',
                    '-f',
                    'main',
                    '--',
                    deployment_py_path,
                ],
                check=True,
            )
    if not flag:
        print(f'no deployment (missing "{deployment_py_path}")', flush=True)
        sys.exit(0)

    print(f'dry running deployment using temporary directory "{tmp_dir}"...', flush=True)

    subprocess.run(
        [sys.executable, os.path.join(tmp_dir, '.deploy', 'deployment.py'), '--dry-run'],
        cwd=tmp_dir,
        check=True,
        input='\n'.join(status_lines),
        text=True,
    )
