* Run from the package root; install the documented official comparator first.
clear all
set more off
set type double
set seed 20260904
set sortseed 20260904
adopath ++ "`c(pwd)'/tests/stata/oracle"
log using "`c(pwd)'/tests/stata/bjs_stata_explicit_certification.txt", text replace
postfile jkfile str32 design double omitted double estimate using "`c(pwd)'/tests/stata/official_deletions.dta", replace
import delimited "`c(pwd)'/tests/fixtures/panel.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/panel_explicit_stata.csv", replace
post jkfile ("panel") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("panel") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/balanced.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/balanced_explicit_stata.csv", replace
post jkfile ("balanced") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("balanced") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/one_cohort.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/one_cohort_explicit_stata.csv", replace
post jkfile ("one_cohort") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("one_cohort") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/unequal.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/unequal_explicit_stata.csv", replace
post jkfile ("unequal") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("unequal") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/extreme_sizes.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/extreme_sizes_explicit_stata.csv", replace
post jkfile ("extreme_sizes") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("extreme_sizes") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/missing_cells.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/missing_cells_explicit_stata.csv", replace
post jkfile ("missing_cells") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("missing_cells") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/covariates.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe* x z) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
generate double stata_beta_x=_b[x]
generate double stata_beta_z=_b[z]
export delimited using "`c(pwd)'/tests/stata/covariates_explicit_stata.csv", replace
post jkfile ("covariates") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
drop stata_beta_x stata_beta_z
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe* x z) nose minn(0)
post jkfile ("covariates") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/unbalanced_post.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/unbalanced_post_explicit_stata.csv", replace
post jkfile ("unbalanced_post") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("unbalanced_post") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/cohort_heterogeneous.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/cohort_heterogeneous_explicit_stata.csv", replace
post jkfile ("cohort_heterogeneous") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("cohort_heterogeneous") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/state_heterogeneous.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/state_heterogeneous_explicit_stata.csv", replace
post jkfile ("state_heterogeneous") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("state_heterogeneous") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/time_varying.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/time_varying_explicit_stata.csv", replace
post jkfile ("time_varying") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("time_varying") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/weak_null.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/weak_null_explicit_stata.csv", replace
post jkfile ("weak_null") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei, fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("weak_null") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/moderate_weights.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei [aw=w], fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/moderate_weights_explicit_stata.csv", replace
post jkfile ("moderate_weights") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei [aw=w], fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("moderate_weights") (`h') (_b[tau])
restore
}
import delimited "`c(pwd)'/tests/fixtures/extreme_weights.csv", clear varnames(1) asdouble
generate double Ei=g
replace Ei=. if g==0
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei [aw=w], fe(.) controls(constant sfe* tfe*) nose minn(0) saveestimates(stata_tau)
generate double stata_att=_b[tau]
generate byte stata_sample=e(sample)
generate double stata_y0=y-stata_tau
foreach v of varlist sfe* tfe* {
generate double coef_`v'=_b[`v']
}
export delimited using "`c(pwd)'/tests/stata/extreme_weights_explicit_stata.csv", replace
post jkfile ("extreme_weights") (.) (_b[tau])
drop sfe* tfe* coef_* constant stata_tau stata_att stata_sample stata_y0
levelsof state, local(states)
foreach h of local states {
preserve
drop if state==`h'
tabulate state, generate(sfe)
tabulate year, generate(tfe)
drop sfe1 tfe1
generate double constant=1
did_imputation y id year Ei [aw=w], fe(.) controls(constant sfe* tfe*) nose minn(0)
post jkfile ("extreme_weights") (`h') (_b[tau])
restore
}
postclose jkfile
use "`c(pwd)'/tests/stata/official_deletions.dta", clear
export delimited using "`c(pwd)'/tests/stata/official_deletions.csv", replace
log close
exit, clear
