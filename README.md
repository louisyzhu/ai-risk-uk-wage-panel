# AI Risk and UK Wages: An Occupation-Year Panel

Did occupations more exposed to automation see their wages diverge from less exposed ones after
2016? This builds a UK occupation-year panel of mean hourly pay from 2014 to 2023, merges an
automation-risk score onto each occupation, and estimates a fixed-effects specification with an
interaction between risk and the post-2016 period.

STATA. Occupation and year fixed effects, standard errors clustered by occupation.

## Design

The panel is occupation by year, keyed on SOC code (`xtset soc year`). The outcome is log mean
hourly pay. The regressor of interest is an automation-risk probability interacted with a post-2016
indicator:

```stata
xtreg lnwage c.risk##i.post2016 i.year, fe cluster(soc)
```

Automation risk is a property of the occupation and does not vary over time, so occupation fixed
effects absorb its main effect entirely. STATA reports it as omitted for collinearity, which is the
expected behaviour. All the identifying variation sits in the interaction: it asks whether the
gradient between risk and pay shifted after 2016, not what the level of that gradient is.

## Result

From the committed log, 367 occupations and 3,255 occupation-year observations, within R² = 0.368:

| Term | Coefficient | Robust SE | t | 95% CI |
|---|---:|---:|---:|---|
| `post2016` | 0.135 | 0.021 | 6.46 | [0.094, 0.176] |
| `post2016 × risk` | **0.205** | 0.028 | 7.21 | [0.149, 0.261] |
| `risk` | omitted (absorbed by occupation FE) | | | |

**The interaction is positive**, and precisely estimated. Relative to the pre-2016 period,
higher-automation-risk occupations show *higher* log pay after 2016 than lower-risk ones. Across the
full range of the risk score the implied gap is about 0.2 log points.

That sign runs against the simple prior that exposure to automation depresses pay in exposed
occupations. Read it carefully. This is a descriptive panel association, not a causal estimate.
There is no instrument, no control group that is unexposed by design, and no attempt to separate
automation from anything else that moved differentially across occupations after 2016. Composition
within occupation is unobserved here, so a rising mean can reflect who remains in an occupation as
much as what those people are paid. The estimate is a fact about the data that wants explaining,
not an answer.

## What is in this repository

```
├── empirical.do              # The full pipeline: build, estimate, robustness, descriptives, figure
├── data_work/panel.dta       # The built occupation-year panel
├── data_work/risk.dta        # Automation-risk scores by SOC
└── output/                   # Tables, the trend graph, and the STATA log
```

The raw inputs are **not** committed. `empirical.do` section 0 builds the panel from `ashe_YYYY.xls`
files for 2014 to 2023 and from `Automation risk by occupation.xlsx`, neither of which is in the
repository. The script is written to skip that rebuild when `data_work/panel.dta` already exists,
which it does, so the estimation runs from the committed panel.

## Running it

Two things need changing first.

1. `empirical.do` line 6 hard-codes `cd "~/Desktop/master folder"`. Point it at wherever you cloned
   this instead. Nothing else in the script uses an absolute path.
2. Estimation needs `estout` for the `esttab` calls. Install with `ssc install estout`.

Then run the script from STATA. It writes tables and the trend figure into `output/`.

## Known gaps

Worth stating plainly, because a reader comparing the script against `output/` will notice.

- **The committed log predates the current script.** `output/empirical_log.smcl` was written on
  24 May 2025 and contains only the baseline regression. The robustness specification that drops
  the pandemic years, the descriptive statistics table, and the trend figure were all added to
  `empirical.do` afterwards, so no committed log covers them. The result table above is the baseline
  only.
- **Output filenames have drifted.** The script writes `Table2_FE.rtf`, `Table1_descstats.txt` and
  `Figure1_trend.png`. What is committed is `Table2_AI.rtf`, `Table_FE.rtf`, `main_table.rtf` and
  `Trend.gph`. The committed outputs come from earlier runs under different names. Re-running
  produces the script's names, not these.
- **The robustness check is unreported.** Dropping 2020 to 2022 is in the script but its result has
  never been recorded anywhere in this repository. That is the first thing to run if anyone picks
  this up.

---

Originally submitted as coursework. Retained because the question stands on its own.
