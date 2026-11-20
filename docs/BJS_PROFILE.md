# BJS profile and optimization



The public optimized path uses state-period sufficient statistics, eliminates state fixed effects through a Schur complement, and solves only the time/covariate block. For 40 states and 8 periods without covariates, the repeated system shrinks from 47 dimensions to 7. Each assignment recomputes the untreated-state contributions exactly. Each state deletion subtracts its contribution from the small cross-products. The cache retains only the current assignment on the design object; no process-global data or unbounded cache is used.



The raw observation-level least-squares oracle remains in estimators/fast_bjs.py. Ill-conditioned normal equations fall back to raw least squares, including near-collinear ordinary covariates. No approximate low-rank inverse updates are used. Public dispatch was enabled only after deterministic point, coefficient, imputed outcome, component/weight, deletion, RI and placebo comparisons passed.



## Measured frozen workload



All figures below use the same frozen 167,809 observations, 40 states, 999 RI assignments and 999 assignments per Replace/Subtract procedure, with BLAS threads set to one.



| Stage | Old seconds | Candidate seconds |

| --- | ---: | ---: |

| Initial data collapse and design preparation | 0.027151 | 0.042942 |

| Jackknife preparation and all 40 deletions | 0.047294 | 0.004892 |

| RI assignment updates, point estimation, aggregation | 1.229325 | 0.238954 |

| Replace assignment updates and inner jackknives | 45.781870 | 3.941700 |

| Subtract preparation, assignment updates and inner jackknives | 45.564875 | 4.643576 |

| Full inference workload | 92.650514 | 8.872063 |



Matched full-workload speedup: 10.443x. The final common CPS runner, including its slow point/deletion checks and output work, took 9.602524s versus the stored historical 154.128503s (16.051x). The new measured runtime is below the aspirational 30-second target. Historical and current timings differ in machine load; the separately measured same-session old/new pair is the cleaner algorithmic comparison.



## Where time went



cProfile used 30 Replace assignments plus their 40 state deletions: 1,271 point calls. Old profile: 1.447s total, 1.371s cumulative untreated regression, including 0.891s direct regression-function overhead, 0.181s rank checking/SVD, 0.067s matrix inversion, and 0.222s NumPy reductions across all functions. These timings overlap and must not be added. Rebuilding/reducing large untreated cross-product blocks was the dominant cost.



Candidate profile: 0.270s total; 0.170s cumulative fit; 0.012s assignment block preparation/cache lookup; 0.031s eigenvalue checking and 0.026s linear solving. Assignment validation consumed 0.075s cumulatively. The small solve and scalar aggregation remain inside fit, which took 0.057s exclusive of subcalls. No pandas work occurs inside the optimized per-assignment regression/deletion loop. Initial data preparation and full-sample Subtract still visit observation-level data once per design.



The point/aggregation and assignment-update timings above include the exact operations needed for that procedure; cProfile does not separately time individual arithmetic lines. Raw profiles and full phase measurements are retained in codex_logs/bjs_old_profile.*, bjs_candidate_profile.*, bjs_old_cps_benchmark.json and bjs_candidate_cps_benchmark.json. Remaining bottlenecks are Python loop/assignment validation, repeated small solves, and inner jackknife orchestration. Further optimization is optional and was not pursued by weakening checks.



## Oracle benchmarks and limits



bjs_matched_benchmarks.csv measures old, candidate and raw oracle on identical small and moderate fixtures (3 draws per procedure) and the frozen CPS sample (1 draw per procedure). Each row records its actual draw count. The CPS raw oracle required about 10.62s for one complete jackknife and 21–22s per one-draw placebo call; a full 999-draw oracle workload was not run. It is not represented as an equal-workload comparison with the 999-draw optimized timings. Every small stress design compares all fixed assignment/deletion results to the oracle; the final CPS runner also checks raw reference point and selected raw deletions.



The transparent oracle and old pre-optimization API snapshot remain available. The optimization did not alter the BJS estimand or treat the untreated sample as fixed across timing assignments. External official Stata certification remains a separate gate, documented in STATA_DID_IMPUTATION_CERTIFICATION.md.

