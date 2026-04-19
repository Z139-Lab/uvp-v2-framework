$ErrorActionPreference = "Stop"

Write-Host "[1/6] Moving to repo root"
Set-Location $PSScriptRoot\..

Write-Host "[2/6] Installing dependencies"
python -m pip install -r .\requirements.txt

Write-Host "[3/6] Running demo toy config"
python .\run_uvp.py --config .\configs\demo_toy.yaml

Write-Host "[4/6] Running main summary_results config"
python .\run_uvp.py --config .\configs\grid_default.yaml

Write-Host "[5/6] Running micro-rule config"
python .\run_uvp.py --config .\configs\grid_micro_rule.yaml

Write-Host "[6/6] Running probe config"
python .\run_uvp.py --config .\configs\grid_probe.yaml

Write-Host "Done. Check the results\ folder."
