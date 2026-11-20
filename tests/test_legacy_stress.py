"""Preserved BJS point API: weighted and incomplete-cell stress oracle."""
import unittest
import numpy as np
import pandas as pd
from fastbjspy.estimators import EstimatorCache,estimate_bjs
from certification_fixtures import fixture

def compare(name):
    data,covs=fixture(name);weighted=name.endswith('weights');schedule=dict(data[['state','g']].drop_duplicates().itertuples(index=False,name=None))
    cache=EstimatorCache.from_data(data,outcome_col='y',state_col='state',time_col='year',covariates=covs,weight_col='w' if weighted else None)
    actual=estimate_bjs(cache,schedule);assert actual.status=='ok'
    X=np.column_stack([pd.get_dummies(data.state,dtype=float),pd.get_dummies(data.year,drop_first=True,dtype=float),data[covs].to_numpy(float)])
    untreated=(data.g==0)|(data.year<data.g);treated=~untreated;w=data.w.to_numpy() if weighted else np.ones(len(data));r=np.sqrt(w[untreated.to_numpy()])
    beta,_,rank,_=np.linalg.lstsq(X[untreated]*r[:,None],data.y.to_numpy()[untreated]*r,rcond=None);assert rank==X.shape[1]
    tau=data.y.to_numpy()-X@beta;expected=np.average(tau[treated],weights=w[treated]);gap=abs(actual.att-expected);assert gap<1e-9
    work=data.loc[treated,['state','year']].copy();work['tauw']=tau[treated]*w[treated];work['weight']=w[treated]
    comp=work.groupby(['state','year']).sum();comp['estimate']=comp.tauw/comp.weight
    actualcomp=actual.att_st.set_index(['state','t']).sort_index();np.testing.assert_allclose(actualcomp.estimate,comp.estimate,atol=1e-9,rtol=1e-9);np.testing.assert_allclose(actualcomp.target_weight,comp.weight,atol=1e-12)
    return dict(design=name+'_legacy_point',status='pass',point_gap=gap,component_gap=float(np.max(np.abs(actualcomp.estimate.to_numpy()-comp.estimate.to_numpy()))),weight_gap=float(np.max(np.abs(actualcomp.target_weight.to_numpy()-comp.weight.to_numpy()))),reason='preserved weighted/incomplete-cell point API; direct raw WLS oracle; common inference remains restricted')

class LegacyPointStress(unittest.TestCase):
    def test_weighted_and_missing_cell_points(self):
        for name in ['moderate_weights','extreme_weights','missing_cells']:
            with self.subTest(name=name):compare(name)
