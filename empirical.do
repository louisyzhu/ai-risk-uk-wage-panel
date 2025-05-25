/********************************************************************
*  empirical.do      AI-risk & UK wage panel   (FINAL May-2025)
********************************************************************/
clear all
set more off
cd "~/Desktop/master folder"
log using "output/empirical_log.smcl", replace

/********************************************************************
* 0.  Build (or rebuild) occupation-year wage panel  ───────────────
********************************************************************/
capture confirm file "data_work/panel.dta"
if _rc {                                         /* rebuild only if absent */
    tempfile wages
    save `wages', emptyok

    local years 2014/2023
    foreach y of numlist `years' {
        import excel using "ashe_`y'.xls", ///
            sheet("All") firstrow cellrange(A5:F500) clear
        keep Code Mean
        rename (Code Mean) (soc wage)
        destring soc,  replace
        destring wage, replace ignore("x")
        drop if missing(soc) | missing(wage)
        gen year  = `y'
        gen lnwage = ln(wage)
        append using `wages'
        save `wages', replace
    }

    import excel using "Automation risk by occupation.xlsx", ///
           sheet("Sheet1") firstrow clear
    rename _all, lower
    keep soc2010 probabilityofautomation
    rename (soc2010 probabilityofautomation) (soc risk)
    destring soc, replace

    merge 1:m soc using `wages', keep(match) nogen
    save "data_work/panel.dta", replace
}

/********************************************************************
* 1.  Set panel structure & helper variables  ───────────────────────
********************************************************************/
use "data_work/panel.dta", clear
xtset soc year
capture confirm variable post2016
if _rc gen post2016 = year >= 2016      /* create only if absent */

/********************************************************************
* 2.  Baseline fixed-effects regression  (Table 2)  ────────────────
********************************************************************/
eststo clear
xtreg lnwage c.risk##i.post2016 i.year, fe cluster(soc)
eststo m1                                        /* store as baseline */

esttab m1 using "output/Table2_FE.rtf", replace rtf  ///
      se label star(* 0.10 ** 0.05 *** 0.01)        ///
      title("Fixed-effects estimates of the impact of automation risk on log hourly wages, 2014–23") ///
      stats(N r2_w, fmt(0 3) labels("Observations" "R² within"))

/********************************************************************
* 3.  Robustness: drop pandemic years 2020-22  (Table 3)  ──────────
********************************************************************/
xtreg lnwage c.risk##i.post2016 i.year ///
      if !inlist(year,2020,2021,2022), fe cluster(soc)
eststo m2                                        /* robustness spec */

esttab m1 m2 using "output/Table3_robust.rtf", replace rtf      ///
      se label star(* 0.10 ** 0.05 *** 0.01)                    ///
      stats(N r2_w, fmt(0 3) labels("Observations" "R² within")) ///
      title("Robustness check: excluding pandemic years")

/********************************************************************
* 4.  Descriptive statistics  (Table 1)  ───────────────────────────
********************************************************************/
capture file close descstats
tempname fh
file open `fh' using "output/Table1_descstats.txt", write replace
file write `fh' "Variable\tN\tMean\tSD\tMin\tMax" _n
quietly foreach v of varlist lnwage risk post2016 {
    quietly su `v', meanonly
    file write `fh' "`v'\t" %9.0f r(N) "\t" %9.3f r(mean) "\t" ///
                       %9.3f r(sd) "\t" %9.3f r(min) "\t" %9.3f r(max) _n
}
file close `fh'
/*  → Open Table1_descstats.txt and Convert-to-Table in Word.           */

/********************************************************************
* 5.  Trend figure: high- vs low-risk occupations  (Figure 1)  ─────
********************************************************************/
use "data_work/panel.dta", clear
egen medrisk = median(risk)
gen  highrisk = risk > medrisk
collapse (mean) lnwage, by(year highrisk)

twoway ///
    (line lnwage year if highrisk==1, lpattern(solid) lwidth(medthick)) ///
    (line lnwage year if highrisk==0, lpattern(dash)  lwidth(medthick)), ///
    legend(order(1 "High-risk occupations" 2 "Low-risk occupations") ///
           ring(0) pos(6)) ///
    ytitle("Mean log hourly wage") ///
    xtitle("Year") ///
    title("Figure 1. Wage trends by automation risk, 2014–23")
graph export "output/Figure1_trend.png", width(1400) replace

log close
exit
