# post-receive-hook-py

## Windows w/ OpenSSH

- issue: the default shell on Windows (`cmd`) **does not** handle single quotes in the same way bash does
  - in `cmd` single quote **is not** a special character used to wrap string, it is just a regular character...
  - git client sends commands whose parameters (paths, etc...) are wrapped in single quotes; also, it uses POSIX paths
    - as a consequence it is very likely to get errors such as "path not found"
- fix
  - change the default shell used by ssh server by applying [this change](./openssh-default-shell.reg) to the registry
    - more info on https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration
  - **OR** keep using default `cmd` but wrap commands by `.bat` scripts that remove single quotes and/or forward slahes
    - the "wrap" technique requires `cmd` to execute `.bat` files **BEFORE** `.exe` files, at least for ssh sessions
      - check `%PATHEXT%` environment variable: it must list `.BAT` **BEFORE** `.EXE`
        - if not, add `SetEnv PATHEXT=.BAT;.CMD;.COM;.EXE;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC` to `%ProgramData%\ssh\sshd_config`
    - put `git-upload-pack.bat` and in the same directory of `git-upload-pack.exe` and `git-receive-pack.exe`
      - to find the directory, run `where git-upload-pack` and `where git-receive-pack`

- put `post-receive` and `post-receive.py` in the `hooks` directory of the remote bare repo

- edit `post-receive` to set the right python path for the OS in use

- on Linux/Mac: execute the following commands

```sh
dos2unix hooks/post-receive
chmod +x hooks/post-receive
```

- customize `.deploy/deployment.py`
