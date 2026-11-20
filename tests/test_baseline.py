from pathlib import Path
import json, unittest
import numpy as np
import pandas as pd
from fastbjspy.estimators import EstimatorCache, estimate_bjs

def estimate(data, covariates):
    cache=EstimatorCache.from_data(data,outcome_col="y",state_col="state",time_col="year",covariates=covariates)
    return float(estimate_bjs(cache,dict(data[["state","g"]].drop_duplicates().itertuples(index=False,name=None))).att)

class BaselineTests(unittest.TestCase):
    def test_frozen_research_values(self):
        base=Path(__file__).parent/'fixtures'
        for case in json.loads((base/'expected.json').read_text()):
            data=pd.read_csv(base/case['file'],float_precision='round_trip')
            value=estimate(data,case['covariates'])
            np.testing.assert_allclose(value,case['estimate'],rtol=2e-12,atol=2e-12)
    def test_row_and_state_label_invariance(self):
        base=Path(__file__).parent/'fixtures'
        data=pd.read_csv(base/'unequal.csv',float_precision='round_trip')
        value=estimate(data,[])
        data=data.sample(frac=1,random_state=33)
        data['state']=data['state'].map({s:s*17+41 for s in data['state'].unique()})
        np.testing.assert_allclose(estimate(data,[]),value,rtol=2e-12,atol=2e-12)

if __name__=='__main__':unittest.main()
