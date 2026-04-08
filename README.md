# poste-receive-hook-py

- Windows w/ OpenSSH
  - add `SetEnv PATHEXT=.BAT;.CMD;.COM;.EXE;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC` to `%ProgramData%\ssh\sshd_config`
  - put `git-upload-pack.bat` in the directory with `git-upload-pack.exe`
  - put `git-receive-pack.bat` in the directory with `git-receive-pack.exe`

- put `post-receive` in the `hooks` directory of the remote bare repo

- Windows: put `post-receive.bat` in the `hooks` directory of the remote bare repo

- Linux: execute the following commands

```sh
dos2unix hooks/post-receive
chmod +x hooks/post-receive
```
