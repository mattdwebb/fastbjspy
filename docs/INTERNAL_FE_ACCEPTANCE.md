# Internal FE and dependency acceptance

| package | tests | result |
|---|---|---|
| fastbjspy | 12 | pass |

Runtime dependency claims and limitations are in DEPENDENCIES.md and the README. Jackknife, RI, Replace, Subtract and MNW bootstrap definitions were preserved; Add remains TWFE-only.

FEABSORB-1/FEFIXTURE-1: 14 projection fixtures, 13 converge and one expected cap failure. Maximum converged dummy gap 1.3115107611039178e-10; cross-language gap 5.10702591327572e-15. Singletons retained; arbitrary K core; positive weights.

| package | procedure | before_seconds | after_seconds | speedup |
|---|---|---|---|---|
| fastbjspy | setup | 0.0242886 | 0.0245472 | 0.989465 |
| fastbjspy | point | 0.0003006 | 0.0003164 | 0.950063 |
| fastbjspy | jackknife | 0.0032796 | 0.0031813 | 1.0309 |
| fastbjspy | ri999 | 0.193807 | 0.20055 | 0.966376 |
| fastbjspy | replace999 | 3.36845 | 3.32827 | 1.01207 |
| fastbjspy | subtract999 | 3.39421 | 3.29529 | 1.03002 |

Performance acceptance includes small tradeoffs: TWFE setup +36ms, MNW Python STAR +11ms and R scalar fine +0.5ms. Repeated-assignment workflows remain acceptable. BJS severe near-collinear large fallbacks are intentionally rejected pending certification; the small raw oracle remains bounded.
