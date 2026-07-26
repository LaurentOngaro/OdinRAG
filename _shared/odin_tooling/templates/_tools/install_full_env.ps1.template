<#
.SYNOPSIS
    This script installs the full environment for the Odin language.

.DESCRIPTION
    The script installs Portable Build Tools and Odin language compiler to the
    specified installation path. Odin is downloaded, unpacked, and the path is
    appended to PortableBuildTools' devcmd.bat so subsequent shells pick it up.

.PARAMETER install_path
    The path where the environment will be installed. Default is the value of
    the FLD_APPS environment variable.

.EXAMPLE
    .\install_full_env.ps1
    .\install_full_env.ps1 -install_path "C:\MyEnvironment"
#>

# -----------------------------------------------------------------------------
# Script Name: install_full_env.ps1
# Description: This script is used to install the full environment for Odin language
# -----------------------------------------------------------------------------

# Parse command line arguments
param (
    [string]$install_path = $env:FLD_APPS
)

# Display help if requested
if ($PSCmdlet.MyInvocation.BoundParameters.ContainsKey('help')) {
    Get-Help -Full $MyInvocation.MyCommand.Path
    exit
}

if (!(Test-Path $install_path)) {
    New-Item -Path $install_path -ItemType Directory
}

#$bt_path = "$install_path\\BuildTools"
$bt_path = "$install_path\\PortableBuildTools"
if (Test-Path $bt_path) {
    Write-Host 'Portable Build Tools is already installed.' -ForegroundColor Green
} else {
    Write-Host "Installing Portable Build Tools in $bt_path"
    $url = 'https://github.com/Data-Oriented-House/PortableBuildTools/releases/latest/download/PortableBuildTools.exe'
    $dst = "$install_path\\PortableBuildTools.exe"
    Start-BitsTransfer -Source $url -Destination $dst -DisplayName 'Downloading Portable Build Tools' -Description 'Downloading Portable Build Tools...'
    Start-Process -FilePath $dst -ArgumentList "cli accept_license install_path=$($bt_path)" -NoNewWindow -Wait
    Remove-Item -Path $dst -Force
}

#$odin_path = "$install_path\\Odin"
$odin_path = "$install_path\\_odin"
if (Test-Path "$odin_path\\odin.exe") {
    Write-Host 'Odin is already installed.' -ForegroundColor Green
} else {
    Write-Host 'Downloading Odin'
    $url = 'https://api.github.com/repos/odin-lang/Odin/releases/latest'
    $res = Invoke-RestMethod -Uri $url
    foreach ($asset in $res.assets) {
        if ($asset.name -match 'windows-amd64') {
            $dst = "$install_path\\$($asset.name)"
            Start-BitsTransfer -Source $asset.browser_download_url -Destination $dst -DisplayName 'Downloading Odin' -Description 'Downloading Odin...'
            Write-Host 'Odin downloaded. Unpacking...'
            Expand-Archive -Path $dst -DestinationPath $odin_path -Force

            $file = Get-ChildItem -Path $odin_path -Recurse -Filter 'odin.exe' | Select-Object -First 1
            if ($file) {
                Write-Host 'Odin unpacked. Modifying BuildTools script...'
                Add-Content -Path "$bt_path\\devcmd.bat" -Value "`nset PATH=%PATH%;$($file.DirectoryName)"
            } else {
                Write-Host 'Failed to find odin.exe' -ForegroundColor Red
            }

            Remove-Item -Path $dst -Force
        }
    }
}

Write-Host 'If you got this far without errors, looks good.' -ForegroundColor Green

Write-Host 'Press any key to continue...'
Read-Host