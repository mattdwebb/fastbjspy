# Native clustered inference

`Design.native_cluster(null=0, engine="fast")` exposes BJS default non-leaveout imputation-weight clustered sandwich, with treated residuals centered by cohort-time smartweights. No finite sample multiplier; normal p-values.

Returns native_cluster_method, native_cluster_se, native_cluster_stat, native_cluster_df, native_cluster_p, native_cluster_distribution and cluster_scores. Jackknife remains a separate method and its existing definition is unchanged. The transparent `engine="reference"` forms explicit dummy scores on small samples. This addition retains the existing Design sample and weighting scope; it does not expand weighted support.

Ten matched deterministic fixtures compare point estimates, SEs, statistics and p-values against Stata did_imputation commit 767c8d6670a751170910d419bbafd323df92ef08 (explicit dummy controls, default cohort-time centering). See native_cluster_external_results.csv.
