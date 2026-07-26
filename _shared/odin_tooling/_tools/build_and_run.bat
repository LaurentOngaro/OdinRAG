@echo off
setlocal enableextensions enabledelayedexpansion
echo.
:: echo CMD:%0 %*

:: !!! THIS SCRIPT WON'T WORK if there are spaces in some paths !!!

:: we don't use the full path to the odin compiler because we want to use the one in the PATH
set buildCommand=odin
set buildOptions=-thread-count:14 -vet-unused -vet-unused-variables -vet-unused-imports -vet-shadowing -vet-style -vet-semicolon -vet-cast -missing-blank-lines-between-procs -use-separate-modules
:: additional build options here
:: add timings info at the start of the build process
:: set buildOptions=%buildOptions% -show-timings
:: Resolve raddbg.exe portably:
::   1. Prefer %FLD_APPS%\Raddebugger\raddbg.exe (set by the user's env).
::   2. Fall back to whatever `where raddbg.exe` finds in PATH.
::   3. If neither resolves, the raddebugger flow is skipped and the binary
::      path is printed so the user can attach manually.
::      Set FLD_APPS=<parent of the Raddebugger install dir>, e.g.
::          set FLD_APPS=E:\Apps
::      so the resolved path is %FLD_APPS%\Raddebugger\raddbg.exe.
set raddebuggerExe=%FLD_APPS%\Raddebugger\raddbg.exe
set cwd=%~dp0
set toolsFolder=%cwd%

set debug=0
set fileMode=
set action=
set src=
set outputFile=out.exe
set execfile=0
set interactive=0
set cls=0
set verbose=0
set wipe=0
set raddebugger=0

if "%~1"=="" (
  echo Parameters for this script are missing.
  goto :ERROR
)

:LOOP
  :: set flags
  if "%~1"=="-v" set verbose=1
  if "%~1"=="--verbose" set verbose=1
  if %verbose%==1 (
    echo Analysing "%~1%" parameter:
  )
  :: !important! DO no use optimize flags (-o:XXX) when debugging because the source code and the debugged code will be different (aka breakpoints won't work or not been set in the correct lines)
  :: -o:none will disable all optimizations
  if "%~1"=="-d" set debug=1
  if "%~1"=="--debug" set debug=1

  if "%~1"=="-f" set fileMode=-file
  if "%~1"=="--file" set fileMode=-file
  if "%~1"=="-e" set execfile=1
  if "%~1"=="--exec" set execfile=1
  if "%~1"=="-i" set interactive=1
  if "%~1"=="--interactive" set interactive=1
  if "%~1"=="-c" set cls=1
  if "%~1"=="--cls" set cls=1
  if "%~1"=="-w" set wipe=1
  if "%~1"=="--wipe" set wipe=1
  if "%~1"=="--rd" set raddebugger=1
  if "%~1"=="--raddebugger" set raddebugger=1

  :: set values
  if "%~1"=="-s" (
    set src=%2
    shift
  )
  if "%~1"=="--src" (
    set src=%2
    shift
  )
  if "%~1"=="-o" (
    set outputFile=%2
    shift
  )
  if "%~1"=="--out" (
    set outputFile=%2
    shift
  )

  :: set command
  if "%~1"=="h" goto HELP
  if "%~1"=="help" goto HELP
  if "%~1"=="b" set action=build
  if "%~1"=="build" set action=build
  if "%~1"=="r" set action=run
  if "%~1"=="run" set action=run
  if "%~1"=="c" set action=clean
  if "%~1"=="clean" set action=clean
  if "%~1"=="t" set action=test
  if "%~1"=="test" set action=test
  shift
  :: no more parameters to process and action is set
  if "%~1"=="" (
    if %cls%==1 (
      cls
      echo THE CONSOLE OUTPUT HAS BEEN CLEARED
    )
    if %verbose%==1 (
      goto DEBUG_INFO
    ) else (
      goto CHECK_CMD
    )
  )
goto LOOP

:HELP
  :: Add usage instructions here
  echo Usage: "build_and_run.bat [h|help] [b|build] [r|run] [-s|--src <src>] [-o|--out <output_file>] [-d|--debug] [-e|--exec] [-v|--verbose]"
  :: add more instructions here
  echo ----
  echo Flags to change the behavior of the script:
  echo ----
  echo "-s , --src            The source FOLDER (or FILE if -f flag is specified) to build or run."
  echo "-o , --out            The output file to build to."
  echo "-d , --debug          Build the output file with debug data (of the Odin compiler)."
  echo "-f , --file           Enable file mode (of the Odin compiler)."
  echo "-e , --exec           Execute the output file after building."
  echo "-i , --interactive    Ask the user for some confirmations. If not present, the script won't prompt the user."
  echo "-c , --cls            Clear the console before run."
  echo "-w , --wipe           Wipe all the existing output data (including folders and files created during previous build processes) before running the task."
  echo "-rd, --raddebugger    Open the the output file as target in Raddebugger. Only works if the -d or --debug flag is set."
  echo "-v , --verbose        Verbose mode: print more details during the processus."
  echo "----"
  echo "Commands to be executed by the script:"
  echo "----"
  echo "-h, --help : Display this help message."
  echo "-b, --build: Build the source file or folder."
  echo "-r, --run  : Build and Run the source file or folder."
  echo "-r, --clean: Empty the output folder."
  echo "-t, --test : Run the Tests for the source file or folder."
goto :EOF

:DEBUG_INFO
  echo.
  echo script parameters:
  echo -----
  echo current folder=%cwd%
  echo toolsFolder=%toolsFolder%
  echo debug=%debug%
  echo fileMode=%fileMode%
  echo action=%action%
  echo src=%src%
  echo outputFile=%outputFile%
  echo execfile=%execfile%
  echo interactive=%interactive%
  echo cls=%cls%
  echo verbose=%verbose%
  echo wipe=%wipe%
  echo raddebugger=%raddebugger%
  echo.

:CHECK_CMD
  if "%action%" == "" (
    echo Please specify a valid action to perform or use the h or help to see the usage instructions.
    goto :ERROR
  )

  if "%action%"=="clean" (
    set wipe=1
    set outputFolder=%outputFile%
  ) else (
    :: get the folder of the output file
    for %%i in ("%outputFile%") do set outputFolder=%%~dpi
    :: get the filename of the output file withgout the extension
    for %%i in ("%outputFile%") do set outputFileName=%%~ni
  )

  if %wipe%==1 (
    if exist "%outputFolder%" (
      rmdir /s /q "%outputFolder%\"
      echo The output folder "%outputFolder%" has been wiped.
    )
  )
  if "%action%"=="clean" goto EOF

  if "%src%" == "" (
    echo A source file or folder to build must be specified using the "-s <folder_or_file>" or "--src <folder_or_file>"command line option.
    goto :ERROR
  )

  if not exist "%src%" (
    echo The Source file or folder "%src%" does not exist.
    goto :ERROR
  )

  if not exist "%outputFolder%" (
    if %interactive%==0 (
      echo The output folder "%outputFolder%" will be created.
      set answer=y
    ) else (
      echo The output folder "%outputFolder%" does not exist.
      set /p answer="Do you want to create it [y/n] ?"
    )
    if /i "!answer!"=="y" (
      mkdir %outputFolder%
      goto :RUN_CMD
    )
    goto :ERROR
  )

:RUN_CMD
  :: run the command "where link.exe" and if it fails, then we are not in a Visual Studio environment
  where link.exe >nul 2>&1
  if %ERRORLEVEL% neq 0 (
    :: set the path to the build tools
    :: BUILD_TOOLS_BIN=E:\Apps\PortableBuildTools\Windows Kits\10\bin\10.0.26100.0\x64
    :: echo "%BUILD_TOOLS_BIN%\..\..\..\..\..\..\..\devcmd.bat"
    call "%BUILD_TOOLS_BIN%\..\..\..\..\..\..\..\devcmd.bat"
  )

  if %debug%==1 (
    set debugMode=-debug -o:none -define:ODIN_RUN_MODE=debug
  ) else (
    set debugMode=-o:speed -define:ODIN_RUN_MODE=release
    set raddebugger=0
  )

  set odin_build_cmd=%buildCommand% %action% %src% %debugMode% %fileMode% %buildOptions% -out:%outputFile%

  echo.
  echo -------------
  echo "1 BUILDING -> %odin_build_cmd%"
  echo -------------
  echo.
  %odin_build_cmd%
  if %ERRORLEVEL% neq 0 (
    echo Error building the source file
    goto :ERROR
  )

  if %raddebugger%==1 (
    :: Resolve raddbg.exe portably: prefer %FLD_APPS%, fall back to PATH.
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
    set RaddbgProjectFile=!outputFolder!!RaddbgProjectFilename!
    set RaddbgUserFilename=project.raddbg_user
    set RaddbgUserFile=!outputFolder!!RaddbgUserFilename!
    set RaddbgStartupFile=!outputFolder!raddbg_start.bat
    :: the order of the parameters is important and must not be changed without reading the raddebugger documentation before
    :: see the Raddebugger README (path is installation-dependent; check %FLD_APPS%\Raddebugger\raddbg_readme.md)
    set RaddbgCmd=!raddebuggerExe! --user:!RaddbgUserFile! --project:!RaddbgProjectFile! !outputFile!
    if %verbose%==1 (
      echo.
      echo RadDebugger parameters:
      echo -----
      echo RaddbgProject=!RaddbgProjectFile!
      echo RaddbgUserFile=!RaddbgUserFile!
      echo RaddbgCmd=!RaddbgCmd!
    )

    :: create the raddebugger startup files id they don't exist
    :: NOTE: we are in the tool folder, where the raddebugger initial startup files are located
    :: we need to copy the project file and the user file to the output folder
    if not exist !RaddbgProjectFilename! (
      if %verbose%==1 echo Creating the project file: !RaddbgProjectFile!
      copy /y %toolsFolder%!RaddbgProjectFilename! !RaddbgProjectFile!
    )
    if not exist !RaddbgUserFile! (
      if %verbose%==1 echo Creating the user file: !RaddbgUserFile!
      copy /y %toolsFolder%!RaddbgUserFilename! !RaddbgUserFile!
    )
    if %verbose%==1 echo Creating the raddebugger startup file
    echo @echo off > !RaddbgStartupFile!
    echo !RaddbgCmd! >> !RaddbgStartupFile!
    :: echo DONE >> !RaddbgStartupFile!
    :: echo pause >> !RaddbgStartupFile!

    echo.
    echo -------------
    echo "2 DEBUGGING -> !RaddbgCmd!"
    echo -------------
    echo.
    :: start the debugger
    !RaddbgStartupFile!
    if %ERRORLEVEL% neq 0 (
      echo Error launching Raddebugger
      goto :ERROR
    )
  ) else (
    if %execfile%==1 (
      echo.
      echo -------------
      echo "2 RUNNING -> %outputFile%"
      echo -------------
      echo.
      %outputFile%
      if %ERRORLEVEL% neq 0 (
        echo Error running outputfile
        goto :ERROR
      )
    )
  )
  goto :EOF

:ERROR
  echo.
  echo At least error occurred running the script.
  pause
  exit /b 1

:EOF
  echo DONE
  exit /b 0
