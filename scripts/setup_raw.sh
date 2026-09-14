#!/usr/bin/env bash
# Downloads the ten ASHE Table 14 releases used by the paper and extracts each
# into raw/ex/<name>/, using the folder names analysis/build_panel.py expects.
# Also fetches the two ONS automation-risk workbooks for provenance.
#
# Run from the repository root:
#     bash scripts/setup_raw.sh
#
# Then:  python analysis/build_panel.py

set -u
BASE="https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupation4digitsoc2010ashetable14"
mkdir -p raw/zips raw/ex

# Each entry is: <folder name build_panel.py expects>|<download URL>
ENTRIES=(
  "rft-14(1)|$BASE/2014revised/rft-14%281%29.zip"
  "table142015revised|$BASE/2015/table142015revised.zip"
  "table142016revised|$BASE/2016revised/table142016revised.zip"
  "table142017revised|$BASE/2017revised/table142017revised.zip"
  "table142018revised|$BASE/2018revised/table142018revised.zip"
  "table142019revised|$BASE/2019revised/table142019revised.zip"
  "table142020revised|$BASE/2020revised/table142020revised.zip"
  "ashetable142021revised|$BASE/2021revised/ashetable142021revised.zip"
  "ashetable142022revised|$BASE/2022revised/ashetable142022revised.zip"
  "ashetable142023revised|$BASE/2023revised/ashetable142023revised.zip"
)

fail=0
for entry in "${ENTRIES[@]}"; do
  name="${entry%%|*}"
  url="${entry#*|}"
  zip="raw/zips/${name}.zip"
  if [ ! -s "$zip" ]; then
    echo "downloading ${name}"
    if ! curl -fsSL --retry 3 -o "$zip" "$url"; then
      echo "  FAILED to download ${name}"
      rm -f "$zip"; fail=1; continue
    fi
  fi
  mkdir -p "raw/ex/${name}"
  if ! unzip -o -q "$zip" -d "raw/ex/${name}"; then
    echo "  FAILED to extract ${name}"; fail=1
  fi
done

mkdir -p raw/risk
curl -fsSL -o "raw/risk/automation_risk_beeswarm.xlsx" \
  "https://www.ons.gov.uk/visualisations/dvc599/beeswarm/data.xlsx" || true
curl -fsSL -o "raw/risk/automation_risk_chatbot.xlsx" \
  "https://www.ons.gov.uk/visualisations/dvc599/chatbot/data/data.xlsx" || true

echo
echo "--- extracted release folders ---"
ls raw/ex
echo
if [ "$fail" -eq 0 ]; then
  echo "All ten releases are in place. Next: python analysis/build_panel.py"
else
  echo "One or more releases failed. See scripts/HOW_TO_GET_ONS_FILES.md for the manual route."
  exit 1
fi
