param(
    [switch]$InstallPython,
    [switch]$InstallPackages
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' is missing. Install Python 3.11+ and enable the Python Launcher, then rerun."
}

py -3 -c "import sys; print(sys.version)"
if ($InstallPackages) {
    py -3 -m pip install -r (Join-Path $root 'requirements.txt')
}

py -3 (Join-Path $root 'fund_engine.py') health
