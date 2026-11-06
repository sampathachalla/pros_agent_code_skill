# Install the toolkit globally on Windows. Accepts the options of `pros install`.
# Not yet tested on Windows.
$ErrorActionPreference = "Stop"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git is required" }
$python = if (Get-Command py -ErrorAction SilentlyContinue) { @("py", "-3") } else { @("python3") }
$pros = Join-Path $PSScriptRoot "..\pros.py"
& $python[0] $python[1..($python.Count)] $pros install @args
exit $LASTEXITCODE
