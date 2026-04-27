import os
import re

# sample regex used to define deployment rules (change them according to your needs!)
BIN_PY_REGEX = re.compile(r"""bin/(.*\.py)$""")
WEB_ASSETS_REGEX = re.compile(r"""html/(.*\.(css|js))$""")


def get_deploy_info_from_repo_path(repo_path: str) -> str | None:
    deploy_path = repo_path  # TODO: convert to deploy path; set to None (or leave equal to repo_path) to ignore

    # tips:
    # - use os.path.normpath(repo_path) to generate a path with the OS-specific path separator

    if BIN_PY_REGEX.match(deploy_path):
        pass
    elif WEB_ASSETS_REGEX.match(deploy_path):
        pass

    return deploy_path
