@echo off

setlocal enabledelayedexpansion

set "head=%1"
@REM if "!head:~0,1!" == "'" set "head=!head:~1!"
@REM if "!head:~-1,1!" == "'" set "head=!head:~0,-1!"
if "!head:~0,1!" == "'" (
	if "!head:~-1,1!" == "'" (
		if not "!head!" == "'" (
			set "head=!head:~1,-1!"
			if "!head:~0,1!" == "/" (
				set "head=!head:~1!"
			)
		)
	)
)

endlocal & set "directory=%head%"

@REM echo "%directory%"
"%~dp0git-receive-pack.exe" %directory%
