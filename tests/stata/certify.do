* Run from the package root; install the documented official comparator first.
clear all
set more off
set type double
adopath ++ "`c(pwd)'/tests/stata/oracle"
capture which did_imputation
if _rc exit 111
log using "`c(pwd)'/tests/stata/bjs_stata_certification.txt", text replace
import delimited "`c(pwd)'/tests/fixtures/panel.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/panel_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/balanced.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/balanced_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/one_cohort.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/one_cohort_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/unequal.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/unequal_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/extreme_sizes.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/extreme_sizes_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/missing_cells.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/missing_cells_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/covariates.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau) controls(x z)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/covariates_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/unbalanced_post.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/unbalanced_post_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/cohort_heterogeneous.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/cohort_heterogeneous_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/state_heterogeneous.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/state_heterogeneous_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/time_varying.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/time_varying_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/weak_null.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei, fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/weak_null_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/moderate_weights.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei [aw=w], fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/moderate_weights_stata.csv", replace
import delimited "`c(pwd)'/tests/fixtures/extreme_weights.csv", clear varnames(1) asdouble
generate double Ei = g
replace Ei = . if g==0
did_imputation y id year Ei [aw=w], fe(state year) nose minn(0) saveestimates(stata_tau)
generate double stata_att = _b[tau]
generate byte stata_sample = e(sample)
generate double stata_y0 = y-stata_tau
export delimited using "`c(pwd)'/tests/stata/extreme_weights_stata.csv", replace
log close
exit, clear
