# Stress-test report

{
  "package": "fastbjspy",
  "candidate": false,
  "counts": {
    "pass": 23,
    "expected_failure": 5,
    "not_applicable": 2
  },
  "maxima": {
    "point_gap": 6.128431095930864e-12,
    "component_gap": 1.3811174426336947e-13,
    "weight_gap": 0.0,
    "delete_gap": 3.1961100432909006e-10,
    "jk_gap": 1.7467747248645082e-09,
    "ri_gap": 1.1170064873056162e-10,
    "placebo_gap": 1.3777290419625388e-10
  }
}

See stress_test_results.csv for each design and stress_test_draws.json for fixed-assignment statistics and inner p-values. Missing cells are an explicit inference-adapter restriction; unsupported weights are N/A. Singleton-cohort deletion failures retain G and all deletions. Heterogeneous effects are diagnostic, not a validity proof. Reference point checks gate inference.
