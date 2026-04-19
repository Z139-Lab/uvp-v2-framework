$ErrorActionPreference = "Stop"

Write-Host "== UVP smoke test: demo toy =="
python .un_uvp.py --config .\configs\demo_toy.yaml

Write-Host "== UVP smoke test: summary_results.csv =="
python .un_uvp.py --config .\configs\grid_default.yaml

Write-Host "== UVP smoke test: micro_rule_summary_results.csv =="
python .un_uvp.py --config .\configs\grid_micro_rule.yaml

Write-Host "== UVP smoke test: probe_summary.csv =="
python .un_uvp.py --config .\configs\grid_probe.yaml

Write-Host "All smoke tests completed."
