# Downloads the ten ASHE Table 14 releases and extracts each into raw\ex\<name>\,
# using the folder names analysis\build_panel.py expects.
#
# Run from the repository root:
#     powershell -ExecutionPolicy Bypass -File scripts\setup_raw.ps1
#
# Then:  python analysis\build_panel.py

$base = "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupation4digitsoc2010ashetable14"
New-Item -ItemType Directory -Force -Path raw\zips, raw\ex, raw\risk | Out-Null

$entries = @(
  @{ name = "rft-14(1)";              url = "$base/2014revised/rft-14%281%29.zip" },
  @{ name = "table142015revised";     url = "$base/2015/table142015revised.zip" },
  @{ name = "table142016revised";     url = "$base/2016revised/table142016revised.zip" },
  @{ name = "table142017revised";     url = "$base/2017revised/table142017revised.zip" },
  @{ name = "table142018revised";     url = "$base/2018revised/table142018revised.zip" },
  @{ name = "table142019revised";     url = "$base/2019revised/table142019revised.zip" },
  @{ name = "table142020revised";     url = "$base/2020revised/table142020revised.zip" },
  @{ name = "ashetable142021revised"; url = "$base/2021revised/ashetable142021revised.zip" },
  @{ name = "ashetable142022revised"; url = "$base/2022revised/ashetable142022revised.zip" },
  @{ name = "ashetable142023revised"; url = "$base/2023revised/ashetable142023revised.zip" }
)

$fail = 0
foreach ($e in $entries) {
  $zip = "raw\zips\$($e.name).zip"
  if (-not (Test-Path $zip)) {
    Write-Host "downloading $($e.name)"
    try { Invoke-WebRequest -Uri $e.url -OutFile $zip -UseBasicParsing }
    catch { Write-Host "  FAILED to download $($e.name)"; $fail = 1; continue }
  }
  New-Item -ItemType Directory -Force -Path "raw\ex\$($e.name)" | Out-Null
  try { Expand-Archive -Path $zip -DestinationPath "raw\ex\$($e.name)" -Force }
  catch { Write-Host "  FAILED to extract $($e.name)"; $fail = 1 }
}

try { Invoke-WebRequest -Uri "https://www.ons.gov.uk/visualisations/dvc599/beeswarm/data.xlsx" -OutFile "raw\risk\automation_risk_beeswarm.xlsx" -UseBasicParsing } catch {}
try { Invoke-WebRequest -Uri "https://www.ons.gov.uk/visualisations/dvc599/chatbot/data/data.xlsx" -OutFile "raw\risk\automation_risk_chatbot.xlsx" -UseBasicParsing } catch {}

Get-ChildItem raw\ex | Select-Object Name
if ($fail -eq 0) { Write-Host "`nAll ten releases are in place. Next: python analysis\build_panel.py" }
else { Write-Host "`nOne or more releases failed. See scripts\HOW_TO_GET_ONS_FILES.md for the manual route." }
