# post-receive-hook-py

## Installation / Usage

- create a remote bare repo and configure it to accept push parameters:

```console
git init --bare
git config receive.advertisePushOptions true
```

- files to put in the `hooks` directory of the remote bare repo
  - [`pre-receive`](./hooks/pre-receive)
  - [`pre-receive.py`](./hooks/pre-receive.py)
  - [`post-receive`](./hooks/post-receive)
  - [`post-receive.py`](./hooks/post-receive.py)

- edit [`post-receive`](./hooks/post-receive) and [`pre-receive`](./hooks/pre-receive) to set the right python path for the OS in use

- on Linux/Mac: execute the following commands to ensure scripts are in the right format and are executable

```sh
dos2unix hooks/pre-receive hooks/post-receive
chmod +x hooks/pre-receive hooks/post-receive
```

- customize [`.deploy/deployment.py`](.deploy/deployment.py)

## Windows w/ OpenSSH

- issue: the default shell on Windows (`cmd`) **DOES NOT** handle single quotes in the same way bash does
  - in `cmd` single quote **IS NOT** a special character used to wrap string, it is just a regular character!
  - git client sends commands whose parameters (paths, etc...) are wrapped in single quotes; also, it uses POSIX paths
    - as a result, it is very likely to encounter errors such as "path not found."
- fix: **CHOOSE ONE** of the following options
  - change the default shell used by ssh server by applying [this change](./openssh-default-shell.reg) to the registry
    - more info on https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration
  - keep using default `cmd` but wrap commands by `.bat` scripts that remove single quotes and/or forward slahes
    - the "wrap" technique requires `cmd` to execute `.bat` files **BEFORE** `.exe` files, at least for ssh sessions
      - check `%PATHEXT%` environment variable: it must list `.BAT` **BEFORE** `.EXE`
        - if not, add `SetEnv PATHEXT=.BAT;.CMD;.COM;.EXE;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC` to `%ProgramData%\ssh\sshd_config`
    - put [`git-upload-pack.bat`](./cmd/git-upload-pack.bat) and [`git-receive-pack.bat`](./cmd/git-receive-pack.bat) in the same directory of `git-upload-pack.exe` and `git-receive-pack.exe`
      - to find the directory, run
      ```bat
      where git-upload-pack&@REM and/or where git-receive-pack
      ```
