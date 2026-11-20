import unittest
import numpy as np
from fastbjspy import Design,assignment_draws
from fastbjspy._bjs import raw_fit
from fastbjspy._bjs_absorbed import absorbed_fit
from certification_fixtures import fixture
class InternalBJSProjectionTests(unittest.TestCase):
    def test_untreated_projection_changes_with_assignment(self):
        for name in ['balanced','covariates','unequal']:
            data,covs=fixture(name);d=Design(data,outcome='y',cluster='state',time='year',assignment=dict(data[['state','g']].drop_duplicates().itertuples(index=False,name=None)),covariates=covs)
            for a in [d.assignment,*assignment_draws(tuple(d.assignment),3,seed=928)]:
                for omit in [None,*range(len(d.states))]:
                    f=absorbed_fit(d,np.asarray(a),omit,True);r=raw_fit(d,np.asarray(a),omit,True)
                    keep=np.ones(len(data),bool) if omit is None else d._rowstate!=omit
                    for key in ['estimate','alpha','gamma']:np.testing.assert_allclose(f[key],r[key],atol=1e-9,rtol=1e-9,equal_nan=True)
                    for key in ['y0','tau']:np.testing.assert_allclose(f[key][keep],r[key][keep],atol=1e-9,rtol=1e-9)
