@echo off
rem =============================================================================
rem  check_and_format.bat
rem  -----------------------------------------------------------------------------
rem  CI pipeline for Odin projects.
rem  Runs:
rem    1. odinfmt -w <src>  -- reformat / normalize (odinfmt.json is the SoT)
rem    2. odin check <src>  -- lint (-vet-* rules defined in ols.json checker_args)
rem
rem  Usage:
rem    check_and_format.bat [src_folder]
rem
rem  Default src_folder: ..\source (relative to this script's location).
rem  If <src_folder> is not specified, the script defaults to the project
rem  layout where _tools\ lives next to source\.
rem =============================================================================
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
odin check "%src%" -strict-style -vet-unused -vet-unused-variables -vet-unused-imports -vet-shadowing -vet-style -vet-semicolon -vet-cast
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
