"""Assignment-specific untreated-sample FE projection fallback; no dummy matrix."""
import numpy as np
from ._fe import FEAbsorber,ConvergenceError
from ._inference import InferenceError

def absorbed_fit(d,a,omit=None,details=False):
    keep=np.ones(len(d.data),bool) if omit is None else d._rowstate!=omit
    D=(a[d._rowstate]>0)&(d.times[d._rowtime]>=a[d._rowstate]);u=keep&~D;target=keep&D
    if not u.any() or not target.any():raise InferenceError('empty_comparison_group')
    x=d.data[d.covariates].to_numpy(float);y=d.data[d.outcome].to_numpy(float)
    try:
        if x.shape[1]:
            # Reparameterize ordinary covariates before absorption to protect nearly dependent columns.
            qtrain,R=np.linalg.qr(x[u],mode='reduced')
            if np.linalg.matrix_rank(R)<x.shape[1]:raise InferenceError('rank_deficient')
            q=np.linalg.solve(R.T,x.T).T
            q[u]=qtrain
        else:q=x;R=np.empty((0,0))
        fe=FEAbsorber(d._rowstate[u],d._rowtime[u])
        residual,diagnostic,effects=fe.residualize(np.column_stack([y[u],q[u]]),tol=1e-14,return_effects=True)
        if q.shape[1]:
            if np.any(np.linalg.norm(residual[:,1:],axis=0)<1e-12):raise InferenceError('rank_deficient')
            beta,_,rank,_=np.linalg.lstsq(residual[:,1:],residual[:,0],rcond=None)
            if rank<q.shape[1]:raise InferenceError('rank_deficient')
            gamma=np.linalg.solve(R,beta)
        else:beta=gamma=np.empty(0)
        predictions=fe.predict_effects(effects,d._rowstate[keep],d._rowtime[keep]);y0=np.full(len(y),np.nan)
        y0[keep]=predictions[:,0]+(q[keep]-predictions[:,1:])@beta
        tau=y-y0;estimate=float(tau[target].mean())
        if not details:return estimate
        potential=[e[:,0]-e[:,1:]@beta for e in effects]
        times=np.array([potential[1][fe.maps[1][t]] for t in range(len(d.times))]);alpha=np.full(len(d.states),np.nan)
        for h in np.unique(d._rowstate[keep]):alpha[h]=potential[0][fe.maps[0][h]]+times[0]
        return dict(estimate=estimate,alpha=alpha,gamma=np.r_[times[1:]-times[0],gamma],y0=y0,tau=tau,target=target,solver='internal_fe',fe_diagnostics=diagnostic)
    except ConvergenceError as e:raise InferenceError('fe_nonconvergence',str(e)) from e
    except (KeyError,ValueError,np.linalg.LinAlgError) as e:raise InferenceError('rank_deficient',str(e)) from e
