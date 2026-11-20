* Run from the package root; install the documented official comparator first.
clear all
set more off
set type double
set seed 20260904
set sortseed 20260904
adopath ++ "`c(pwd)'/tests/stata/oracle"
log using "`c(pwd)'/tests/stata/bjs_stata_weight_diagnostic.txt", text replace
import delimited "`c(pwd)'/tests/fixtures/extreme_weights.csv", clear varnames(1) asdouble
gen double Ei=g
replace Ei=. if g==0
gen byte untreated=g==0 | year<g
regress y i.state i.year [aw=w] if untreated
predict double direct_y0, xb
gen double direct_tau=y-direct_y0 if !untreated
summarize direct_tau [aw=w]
reghdfe y [aw=w] if untreated, absorb(state year) keepsingletons residuals(hdfe_default_resid)
scalar default_rss=e(rss)
reghdfe y [aw=w] if untreated, absorb(state year) keepsingletons tolerance(1e-14) residuals(hdfe_tight_resid)
scalar tight_rss=e(rss)
display "DEFAULT_RSS " %24.17g default_rss
display "TIGHT_RSS " %24.17g tight_rss
did_imputation y id year Ei [aw=w], fe(state year) nose minn(0) saveestimates(official_tau)
gen double official_att=_b[tau]
export delimited using "`c(pwd)'/tests/stata/extreme_weight_diagnostic.csv", replace
log close
exit, clear
