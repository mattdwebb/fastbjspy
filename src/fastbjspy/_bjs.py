"""BJS sufficient-statistic candidate, retaining an independent raw OLS oracle.

State effects are eliminated exactly; each timing assignment builds untreated
state blocks once. Deletion subtracts one block from the small time/covariate
normal equations. No approximate inverse or low-rank downdate is used.
"""
import numpy as np
from ._inference import InferenceError
from ._bjs_absorbed import absorbed_fit


def prepare(d):
    G=len(d.states);T=len(d.times);k=len(d.covariates);C=G*T
    q=np.tile(np.eye(T)[:,1:],(G,1));p=T-1+k
    x=d.data[d.covariates].to_numpy(float);y=d.data[d.outcome].to_numpy(float)
    xs=np.zeros((C,k));xy=np.zeros((C,k));xx=np.zeros((C,k,k))
    for j in range(k):
        xs[:,j]=np.bincount(d._rowcell,weights=x[:,j],minlength=C)
        xy[:,j]=np.bincount(d._rowcell,weights=x[:,j]*y,minlength=C)
        for l in range(k):xx[:,j,l]=np.bincount(d._rowcell,weights=x[:,j]*x[:,l],minlength=C)
    zs=np.column_stack([q*d.n[:,None],xs]);zy=np.column_stack([q*d.ysum[:,None],xy]);zz=np.zeros((C,p,p))
    zz[:,:T-1,:T-1]=d.n[:,None,None]*q[:,:,None]*q[:,None,:]
    if k:
        zz[:,:T-1,T-1:]=q[:,:,None]*xs[:,None,:]
        zz[:,T-1:,:T-1]=zz[:,:T-1,T-1:].transpose(0,2,1);zz[:,T-1:,T-1:]=xx
    d._bjs_moments=(zs.reshape(G,T,p),zy.reshape(G,T,p),zz.reshape(G,T,p,p))
    d._bjs_assignment_cache=None


def blocks(d,a):
    if not hasattr(d,'_bjs_moments'):prepare(d)
    key=tuple(a);cache=d._bjs_assignment_cache
    if cache is not None and cache[0]==key:return cache[1]
    zs,zy,zz=d._bjs_moments
    treated=(a[:,None]>0)&(d.times[None,:]>=a[:,None]);u=~treated
    n=(d.counts*u).sum(1);sy=(d.ysum.reshape(d.counts.shape)*u).sum(1)
    if (n<=0).any():raise InferenceError('rank_deficient','state has no untreated observations')
    sz=np.einsum('gtp,gt->gp',zs,u);qy=np.einsum('gtp,gt->gp',zy,u);qq=np.einsum('gtpq,gt->gpq',zz,u)
    S=qq-sz[:,:,None]*sz[:,None,:]/n[:,None,None];b=qy-sz*sy[:,None]/n[:,None]
    target_n=(d.counts*treated).sum(1);target_y=(d.ysum.reshape(d.counts.shape)*treated).sum(1);target_z=np.einsum('gtp,gt->gp',zs,treated)
    out=(n,sy,sz,S,b,S.sum(0),b.sum(0),target_n,target_y,target_z,treated)
    d._bjs_assignment_cache=(key,out)
    return out


def raw_fit(d,a,omit=None,details=False):
    keep=np.ones(len(d.data),dtype=bool) if omit is None else d._rowstate!=omit
    states=np.arange(len(d.states));states=states if omit is None else states[states!=omit]
    x=np.column_stack([np.eye(len(d.states))[d._rowstate][:,states],np.eye(len(d.times))[d._rowtime,1:],d.data[d.covariates].to_numpy(float)])
    D=(a[d._rowstate]>0)&(d.times[d._rowtime]>=a[d._rowstate]);u=keep&~D;target=keep&D
    if not u.any() or not target.any():raise InferenceError('empty_comparison_group')
    beta,_,rank,_=np.linalg.lstsq(x[u],d.data[d.outcome].to_numpy(float)[u],rcond=None)
    if rank<x.shape[1]:raise InferenceError('rank_deficient','raw nuisance design')
    y0=x@beta;tau=d.data[d.outcome].to_numpy(float)-y0;estimate=float(tau[target].mean())
    if not details:return estimate
    alpha=np.full(len(d.states),np.nan);alpha[states]=beta[:len(states)]
    return dict(estimate=estimate,alpha=alpha,gamma=beta[len(states):],y0=y0,tau=tau,target=target,solver='raw_lstsq')


def fit(d,a,omit=None,details=False):
    n,sy,sz,S,b,totalS,totalb,tn,ty,tz,treated=blocks(d,a)
    keep=np.ones(len(n),dtype=bool)
    if omit is not None:keep[omit]=False
    lhs=totalS if omit is None else totalS-S[omit];rhs=totalb if omit is None else totalb-b[omit]
    if tn[keep].sum()<=0:raise InferenceError('empty_comparison_group')
    scale=np.sqrt(np.maximum(np.diag(lhs),0))
    # Cross-products square conditioning; route unstable systems to raw QR/SVD.
    if (scale<=np.sqrt(np.finfo(float).eps)*max(1.,float(scale.max()))).any():
        return fallback_fit(d,a,omit,details)
    scaled=lhs/scale[:,None]/scale[None,:]
    eig=np.linalg.eigvalsh(scaled)
    if eig[0]<=1e-9*eig[-1]:return fallback_fit(d,a,omit,details)
    try:gamma=np.linalg.solve(scaled,rhs/scale)/scale
    except np.linalg.LinAlgError:return fallback_fit(d,a,omit,details)
    alpha=(sy-sz@gamma)/n
    estimate=float((ty[keep].sum()-tn[keep]@alpha[keep]-tz[keep].sum(0)@gamma)/tn[keep].sum())
    if not details:return estimate
    time_effect=np.r_[0.,gamma[:len(d.times)-1]]
    y0=alpha[d._rowstate]+time_effect[d._rowtime]
    if d.covariates:y0+=d.data[d.covariates].to_numpy(float)@gamma[len(d.times)-1:]
    target=treated[d._rowstate,d._rowtime]&keep[d._rowstate]
    alpha=alpha.copy()
    if omit is not None:alpha[omit]=np.nan
    return dict(estimate=estimate,alpha=alpha,gamma=gamma,y0=y0,tau=d.data[d.outcome].to_numpy(float)-y0,target=target,solver='state_schur')


def fallback_fit(d,a,omit=None,details=False):
    # Preserve the validated small raw oracle when individual coefficients are
    # numerically unstable under near-collinear covariate reparameterization.
    # This bounded oracle is never a large-design FE algorithm.
    if d.covariates:
        keep=np.ones(len(d.data),bool) if omit is None else d._rowstate!=omit
        untreated=keep & ~((a[d._rowstate]>0)&(d.times[d._rowtime]>=a[d._rowstate]))
        x=d.data[d.covariates].to_numpy(float)[untreated]
        if np.linalg.cond(x)>1e6:
            elements=len(d.data)*(len(d.states)+len(d.times)-1+len(d.covariates))
            if elements<=250000:return raw_fit(d,a,omit,details)
            raise InferenceError('ill_conditioned','near-collinear large-design FE fallback is not certified; small raw oracle limit exceeded')
    return absorbed_fit(d,a,omit,details)
