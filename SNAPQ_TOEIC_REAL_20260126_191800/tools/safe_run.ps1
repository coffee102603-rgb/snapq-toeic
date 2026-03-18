# ============================================================
# SNAPQ SAFE RUN (LITE v4) - SKIP BAD FILES
# ============================================================

$ROOT = "C:\Users\최정은\Desktop\SNAPQ_TOEIC"
Set-Location $ROOT

Write-Host "`n[SAFE RUN LITE v4] SNAPQ TOEIC (skip bad files)" -ForegroundColor Cyan
Write-Host "[ROOT] $ROOT" -ForegroundColor Green

cmd /c "taskkill /F /IM streamlit.exe >nul 2>&1"
cmd /c "taskkill /F /IM python.exe >nul 2>&1"

# main_hub
Write-Host "`n[CHECK] py_compile main_hub.py ..." -ForegroundColor Yellow
python -m py_compile .\main_hub.py
if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] main_hub.py compile failed" -ForegroundColor Red; Read-Host "Press Enter"; exit 1 }

# pages
Write-Host "`n[CHECK] py_compile pages/*.py ..." -ForegroundColor Yellow
$pages = Get-ChildItem .\pages -File -Filter "*.py" -ErrorAction SilentlyContinue
foreach($f in $pages){
  python -m py_compile $f.FullName
  if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] pages compile failed (SKIP) => $($f.Name)" -ForegroundColor Yellow
  }
}

# arenas (스킵 허용)
Write-Host "`n[CHECK] py_compile app/arenas/*.py (SKIP on error) ..." -ForegroundColor Yellow
$arenas = Get-ChildItem .\app\arenas -File -Filter "*.py" -ErrorAction SilentlyContinue
foreach($f in $arenas){
  python -m py_compile $f.FullName
  if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] arenas compile failed (SKIP) => $($f.Name)" -ForegroundColor Yellow
  }
}

Write-Host "`n[OK] 체크 완료. Streamlit 실행!" -ForegroundColor Green
Write-Host "  Local URL: http://localhost:8501" -ForegroundColor Cyan

python -m streamlit run .\main_hub.py

Read-Host "Press Enter to close"
