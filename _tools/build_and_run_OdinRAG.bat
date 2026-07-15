@echo off
setlocal enableextensions enabledelayedexpansion

:: Mirror of code/projects/PVG03_RPG/_tools/build_and_run.bat for the OdinRAG root
:: workspace. Invoked by the VS Code F5 "Build + open Raddebugger on PVG03_RPG" launch
:: config (preLaunchTask). Preserves the exact pipeline used when the child project
:: is opened directly:
::   1. odin build with the same options as the child project
::   2. copy project.raddbg_project / project.raddbg_user from the child _tools
::      to the build/ folder
::   3. spawn raddbg.exe detached (via raddbg_start.bat) with the right project args
::
:: Args (same contract as the child script):
::   build | run | clean | test
::   --src <folder>
::   --out <file>
::   --debug (default)
::   --exec (for run action)
::   --raddebugger
::   --wipe
::   --verbose
::
:: Env:
::   FLD_APPS=<path to Raddebugger install dir> -- expected layout:
::       %FLD_APPS%\Raddebugger\raddbg.exe
::   If FLD_APPS is not set, the script falls back to `where raddbg.exe`.

set buildCommand=odin
set buildOptions=-thread-count:14 -vet-unused -vet-unused-variables -vet-unused-imports -vet-shadowing -vet-style -vet-semicolon -vet-cast -use-separate-modules
set raddebuggerExe=%FLD_APPS%\Raddebugger\raddbg.exe
set cwd=%~dp0
set debug=1
set fileMode=
set action=
set src=
set outputFile=out.exe
set execfile=0
set wipe=0
set raddebugger=0
set verbose=0

:: Default project when opened from the OdinRAG root workspace.
:: Override with --src / --out if you add a second project.
set defaultProject=PVG03_RPG
set defaultProjectDir=%cwd%..\code\projects\%defaultProject%
set defaultSrc=%defaultProjectDir%\source
set defaultOut=%defaultProjectDir%\build\%defaultProject%_debug.exe
set childToolsDir=%defaultProjectDir%\_tools

:LOOP
  if "%~1"=="" goto CHECK_CMD
  if "%~1"=="-v" set verbose=1
  if "%~1"=="--verbose" set verbose=1
  if "%~1"=="-d" set debug=1
  if "%~1"=="--debug" set debug=1
  if "%~1"=="-e" set execfile=1
  if "%~1"=="--exec" set execfile=1
  if "%~1"=="-w" set wipe=1
  if "%~1"=="--wipe" set wipe=1
  if "%~1"=="-f" set fileMode=-file
  if "%~1"=="--file" set fileMode=-file
  if "%~1"=="--rd" set raddebugger=1
  if "%~1"=="--raddebugger" set raddebugger=1
  if "%~1"=="-s" (set src=%2& shift)
  if "%~1"=="--src" (set src=%2& shift)
  if "%~1"=="-o" (set outputFile=%2& shift)
  if "%~1"=="--out" (set outputFile=%2& shift)
  if "%~1"=="b" set action=build
  if "%~1"=="build" set action=build
  if "%~1"=="r" set action=run
  if "%~1"=="run" set action=run
  if "%~1"=="c" set action=clean
  if "%~1"=="clean" set action=clean
  if "%~1"=="t" set action=test
  if "%~1"=="test" set action=test
  shift
  goto LOOP

:CHECK_CMD
  if "%action%"=="" set action=build

  if "%action%"=="clean" set outputFolder=%outputFile%

  if "%src%"=="" set src=%defaultSrc%
  if "%outputFile%"=="out.exe" set outputFile=%defaultOut%

  for %%i in ("%outputFile%") do set outputFolder=%%~dpi

  if %wipe%==1 (
    if exist "%outputFolder%" (
      rmdir /s /q "%outputFolder%\"
      echo Wiped "%outputFolder%".
    )
  )
  if "%action%"=="clean" goto EOF

  if not exist "%src%" (
    echo Source not found: "%src%"
    goto ERROR
  )
  if not exist "%outputFolder%" mkdir "%outputFolder%"

  if %debug%==1 (set debugMode=-debug -o:none) else (set debugMode=-o:speed& set raddebugger=0)

  set odin_build_cmd=%buildCommand% %action% "%src%" %debugMode% %fileMode% %buildOptions% -out:%outputFile%
  echo.
  echo 1 BUILDING -^> %odin_build_cmd%
  echo.
  %odin_build_cmd%
  if %ERRORLEVEL% neq 0 goto ERROR

  if %raddebugger%==1 (
    :: Resolve raddbg.exe: prefer %FLD_APPS%\Raddebugger\raddbg.exe, fall back to PATH.
    if not exist "%raddebuggerExe%" (
      for /f "delims=" %%r in ('where raddbg.exe 2^>nul') do (
        set raddebuggerExe=%%r
      )
    )
    if not exist "%raddebuggerExe%" (
      echo raddbg.exe not found - set FLD_APPS or add it to PATH.
      echo Binary ready: %outputFile%
      goto EOF
    )

    set RaddbgProjectFilename=project.raddbg_project
    set RaddbgUserFilename=project.raddbg_user
    set RaddbgProjectFile=%outputFolder%%RaddbgProjectFilename%
    set RaddbgUserFile=%outputFolder%%RaddbgUserFilename%
    set RaddbgStartupFile=%outputFolder%raddbg_start.bat

    if not exist "%outputFolder%%RaddbgProjectFilename%" (
      if exist "%childToolsDir%\%RaddbgProjectFilename%" (
        copy /y "%childToolsDir%\%RaddbgProjectFilename%" "%RaddbgProjectFile%" >nul
      ) else (
        echo WARNING: %RaddbgProjectFilename% not found in %childToolsDir%.
      )
    )
    if not exist "%outputFolder%%RaddbgUserFilename%" (
      if exist "%childToolsDir%\%RaddbgUserFilename%" (
        copy /y "%childToolsDir%\%RaddbgUserFilename%" "%RaddbgUserFile%" >nul
      ) else (
        echo WARNING: %RaddbgUserFilename% not found in %childToolsDir%.
      )
    )

    :: Arg order matters: --user: then --project: then target exe. (cf. raddbg docs.)
    set RaddbgCmd="!raddebuggerExe!" --user:"!RaddbgUserFile!" --project:"!RaddbgProjectFile!" "!outputFile!"

    echo @echo off > "!RaddbgStartupFile!"
    echo !RaddbgCmd! >> "!RaddbgStartupFile!"

    echo.
    echo 2 DEBUGGING -^> !RaddbgCmd!
    echo.
    :: `start ""` detaches raddbg.exe so the task can return immediately, avoiding
    :: VS Code "Waiting for preLaunchTask ..." hangs.
    start "" cmd /c ""!RaddbgStartupFile!""
    goto EOF
  )

  if "%execfile%"=="1" (
    echo.
    echo 2 RUNNING -^> %outputFile%
    echo.
    "%outputFile%"
    if %ERRORLEVEL% neq 0 goto ERROR
  )

:EOF
  echo DONE
  exit /b 0

:ERROR
  echo At least one error occurred.
  exit /b 1
