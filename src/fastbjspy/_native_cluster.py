"""Static BJS default cohort-time centered imputation-weight cluster sandwich.

Independent implementation of the default (non-leaveout) did_imputation VCE.
No new point estimator or change to the existing jackknife.
"""
import math
import numpy as np
from ._bjs import fit, blocks, raw_fit
from ._inference import InferenceError

def native_cluster(d,*,null=0.,engine='fast'):
    a=d.assignment;G=len(d.states);T=len(d.times)
    if engine=='fast':
        result=fit(d,a,details=True)
        if result['solver']!='state_schur':
            return native_cluster(d,null=null,engine='reference')
        n,sy,sz,S,b,lhs,rhs,tn,ty,tz,treated=blocks(d,a)
        gamma=result['gamma'];alpha=result['alpha'];mass=tn.sum()
        delta=np.linalg.solve(lhs,(tz-tn[:,None]*sz/n[:,None]).sum(0))
        first_score=b-np.einsum('gpq,q->gp',S,gamma)
        zs=d._bjs_moments[0]
        cell_tau=d.ysum.reshape(G,T)-d.counts*alpha[:,None]-np.einsum('gtp,p->gt',zs,gamma)
        centered=cell_tau.copy()
        for g in np.unique(a[a>0]):
            cohort=a==g
            for t in np.flatnonzero(d.times>=g):
                # Official cluster-by-cohort-time smart weights; cell sizes squared.
                c=d.counts[cohort,t]
                avg=np.sum(c*cell_tau[cohort,t])/np.sum(c*c)
                centered[cohort,t]-=c*avg
        scores=((centered*treated).sum(1)-first_score@delta)/mass
    elif engine=='reference':
        result=raw_fit(d,a,details=True)
        z=np.column_stack([np.eye(G)[d._rowstate],np.eye(T)[d._rowtime,1:],d.data[d.covariates].to_numpy(float)])
        target=result['target'];u=~target;mass=target.sum();tau=result['tau']
        h=np.linalg.solve(z[u].T@z[u],z[target].sum(0))/mass
        weights=np.where(target,1./mass,-z@h)
        residual=tau.copy()
        for g in np.unique(a[a>0]):
            for t in np.flatnonzero(d.times>=g):
                rows=(a[d._rowstate]==g)&(d._rowtime==t)
                counts=np.bincount(d._rowstate[rows],minlength=G)
                smart=counts[d._rowstate[rows]]
                residual[rows]-=np.average(tau[rows],weights=smart)
        scores=np.bincount(d._rowstate,weights=weights*residual,minlength=G)
    else:raise ValueError('engine must be fast or reference')
    se=float(np.linalg.norm(scores));theta=float(result['estimate']);stat=(theta-null)/se if se>0 else float('nan')
    return dict(estimate=theta,native_cluster_method='BJS_imputation_default_cohort_time',
                native_cluster_se=se,native_cluster_stat=stat,native_cluster_df=None,
                native_cluster_p=math.erfc(abs(stat)/math.sqrt(2)),native_cluster_distribution='normal',
                cluster_scores=scores,finite_sample_multiplier=1.,status='ok' if se>0 else 'zero_standard_error')
