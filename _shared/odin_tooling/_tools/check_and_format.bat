@echo off
:: =============================================================================
::  check_and_format.bat
::  -----------------------------------------------------------------------------
::  CI pipeline for Odin projects.
::  Runs:
::    1. odinfmt -w <src>  -- reformat / normalize (odinfmt.json is the SoT)
::    2. odin check <src>  -- lint (-vet-* rules defined in ols.json checker_args)
::
::  Usage:
::    check_and_format.bat [src_folder]
::
::  Default src_folder: ..\source (relative to this script's location).
::  If <src_folder> is not specified, the script defaults to the project
::  layout where _tools\ lives next to source\.
:: =============================================================================
setlocal enableextensions enabledelayedexpansion

set cwd=%~dp0
set src=%~1
if "%src%"=="" set src=%cwd%..\source

echo.
echo === [1/2] odinfmt -w %src% ===
where odinfmt >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo ERROR: 'odinfmt' not found in PATH. Install Odin or update PATH.
  goto :ERROR
)
odinfmt -w "%src%"
if %ERRORLEVEL% neq 0 (
  echo ERROR: odinfmt failed.
  goto :ERROR
)

echo.
echo === [2/2] odin check %src% ===
where odin >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo ERROR: 'odin' not found in PATH. Install Odin or update PATH.
  goto :ERROR
)
odin check "%src%" -strict-style -vet-unused -vet-unused-variables -vet-unused-imports -vet-shadowing -vet-style -vet-semicolon -vet-cast -missing-blank-lines-between-procs
if %ERRORLEVEL% neq 0 (
  echo ERROR: odin check failed.
  goto :ERROR
)

echo.
echo === ALL CHECKS PASSED ===
goto :EOF

:ERROR
echo.
echo CI pipeline failed.
exit /b 1

:EOF
exit /b 0
