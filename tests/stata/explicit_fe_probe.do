* Run from the package root; install the documented official comparator first.
clear all
set more off
set type double
set seed 20260904
set sortseed 20260904
adopath ++ "`c(pwd)'/tests/stata/oracle"
log using "`c(pwd)'/tests/stata/bjs_stata_explicit_fe_probe.txt", text replace
import delimited "`c(pwd)'/tests/fixtures/extreme_weights.csv", clear varnames(1) asdouble
gen double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
gen double constant=1
did_imputation y id year Ei [aw=w], fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
gen double stata_att=_b[tau]
gen double stata_y0=y-stata_tau
export delimited using "`c(pwd)'/tests/stata/extreme_weights_explicit_probe.csv", replace
log close
exit, clear
