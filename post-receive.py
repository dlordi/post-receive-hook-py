import os
import subprocess
import tempfile
import sys

git_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
deployment_py_path = '.deploy/deployment.py'

result = subprocess.run(
    ['git', f'--git-dir={git_dir}', 'cat-file', '-e', f'main:{deployment_py_path}'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
if result.returncode:
    print(f'no deployment (missing "{deployment_py_path}")', flush=True)
    sys.exit(0)

with tempfile.TemporaryDirectory() as tmp_dir:
    print(f'running deployment using temporary directory "{tmp_dir}"...', flush=True)
    status_lines: list[str] = []
    checkout_files: list[str] = []
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
            if path != deployment_py_path:
                status_lines.append(file_line)
                if status in ('A', 'M'):
                    checkout_files.append(path)
    checkout_files.append(deployment_py_path)
    batch_size = 30
    for i in range(0, len(checkout_files), batch_size):
        batch = checkout_files[i : i + batch_size]
        subprocess.run(
            ['git', f'--work-tree={tmp_dir}', f'--git-dir={git_dir}', 'checkout', '-f', 'main', '--'] + batch,
            check=True,
        )

    subprocess.run(
        [sys.executable, os.path.join(tmp_dir, '.deploy', 'deployment.py')],
        cwd=tmp_dir,
        check=True,
        input='\n'.join(status_lines),
        text=True,
    )
