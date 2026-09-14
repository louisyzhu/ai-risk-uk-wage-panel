# Automation Exposure and the UK Labour Market: Employment, Pay and the Wage Floor, 2014–2020

Replication materials for the working paper of that name by Louis Yiven Zhu (SSRN 5736503, revised September 2026).

The paper joins the ONS probability of automation to seven ASHE Table 14 releases on the SOC 2010 classification and follows mean hourly pay, employee jobs and paid hours across 366 four-digit occupations. Employment in more automatable occupations fell after 2016 with a break at the treatment date. Mean pay rose along a path that began before 2016 and that exposure to the National Living Wage accounts for.

## Relationship to the December 2025 version

The December 2025 version covered 2014 to 2023 and read a positive post-2016 interaction between automation risk and pay as evidence of augmentation. That reading is withdrawn. The 2021 to 2023 ASHE releases are published on SOC 2020, and joining them to SOC 2010 risk scores by numeric code attaches the score to a different occupation for 125 of the 261 codes present in both classifications. The revised paper covers 2014 to 2020 on a single classification, adds employment and hours, and reaches the opposite conclusion on the labour-market story. Appendix E of the paper lists every withdrawn claim.

The files behind the December 2025 version remain in this repository at the tag `v1-ssrn-dec2025`, namely `empirical.do`, `data_work/panel.dta` and `output/`. They are kept because the revised paper states that the rebuilt panel reproduces the archived one cell for cell, and that claim should be checkable.

## What is here

| Path | Contents |
|---|---|
| `paper/` | `main.tex`, `main.pdf`, and the `tables/` and `figures/` the build reads |
| `analysis/` | The pipeline: panel build, estimation, table generation, figure-data export |
| `analysis/locked_numbers_v2.json` | Every estimate the paper reports, in one file |
| `build/` | The extracted occupation-year panels and the workbook provenance tables |
| `figures/` | Figure scripts, `paperstyle.py`, the data each figure reads, and the rendered PDF, SVG and PNG |
| `scripts/` | One-command download of the raw ASHE workbooks, and a manual fallback |
| `data_work/risk.dta` | The ONS probability of automation, 369 SOC 2010 unit groups |
| `empirical.do`, `output/` | The December 2025 Stata pipeline and its logs, retained for comparison |

## Rebuilding from the raw files

The ten ASHE zip archives are not committed because of their size. Everything else needed is here.

1. **Download the raw workbooks.** From the repository root, run `bash scripts/get_ashe_files.sh` on macOS or Linux, or `scripts/get_ashe_files.ps1` on Windows. If the ONS reorganises its dataset page, `scripts/HOW_TO_GET_ONS_FILES.md` gives the manual click-through route.
2. **Unpack them.** Each of the ten zips should be extracted into its own folder under `raw/ex/`, named after the zip. For example `ashe_2015.zip` extracts to `raw/ex/table142015revised/`. The folder names the build script expects are listed in the `YEAR_DIR` dictionary at the top of `analysis/build_panel.py`.
3. **Build the panel.** `python analysis/build_panel.py` writes `build/*_raw.csv` and the provenance tables.
4. **Estimate.** `python analysis/run3.py` then `python analysis/run4.py` write `analysis/locked_numbers_v2.json`. The permutation test uses seed 20260912.
5. **Export the figure data.** `python analysis/export_figure_data.py` writes the four figure CSVs from the locked estimates. Run this after any change to the locked file, so the figures cannot drift from the tables.
6. **Generate the tables.** `python analysis/make_tables_v3.py` writes every table in `paper/tables/` from the locked estimates. No number in the paper is typed by hand.
7. **Render the figures.** Run the three scripts in `figures/`. They require Helvetica or Arial and stop with an error rather than falling back to a serif font, which is deliberate.
8. **Compile.** `cd paper && latexmk -pdf main.tex`.

Steps 3 to 8 take a few minutes. Step 1 downloads roughly 80 MB.

## Requirements

Python 3.11 or later with `pandas`, `numpy`, `pyfixest` 0.60, `statsmodels`, `xlrd`, `openpyxl` and `matplotlib` 3.11. A TeX distribution with `lmodern`, `booktabs`, `threeparttable`, `natbib` and `microtype`.

## Data sources

Annual Survey of Hours and Earnings, Table 14, occupation by four-digit SOC 2010, revised editions for the 2014 to 2023 releases, Office for National Statistics. Probability of automation by occupation, Office for National Statistics, 2019. Both are public. The analysis uses published aggregate statistics only.

## Licence

Code is released under the MIT Licence. The ONS source data are subject to the Open Government Licence.
