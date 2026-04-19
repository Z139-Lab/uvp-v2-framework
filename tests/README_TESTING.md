# Testing checklist

## 1. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 2. Run the toy smoke test

```powershell
python .un_uvp.py --config .\configs\demo_toy.yaml
```

Expected:
- `results/demo_toy/critical/sigma_c.json`
- `results/demo_toy/z_fit/z_fit.json`

## 3. Run the main summary table

```powershell
python .un_uvp.py --config .\configs\grid_default.yaml
```

Expected:
- `results/grid_main16/processed_input.csv`
- `results/grid_main16/critical/sigma_c.json`
- `results/grid_main16/z_fit/z_fit.json`

## 4. Run the micro-rule robustness table

```powershell
python .un_uvp.py --config .\configs\grid_micro_rule.yaml
```

## 5. Run the probe scan

```powershell
python .un_uvp.py --config .\configs\grid_probe.yaml
```

## 6. Full smoke test

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```
