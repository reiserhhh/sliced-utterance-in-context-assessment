"""Executable simulation worlds SIM-W0 through SIM-W8."""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

import numpy as np

from .algebra import conditional_innovation, stationary_mean_variance, three_point_mixed_moments

CRITERIA = {
    "exact_1e-10": lambda r: abs(r["bias"]) <= 1e-10,
    "bias_15pct": lambda r: abs(r["bias"]) <= max(.04, .15 * abs(r["truth"])),
    "coverage_nominal_95": lambda r: ((r["mc_ci_low"] <= .95 <= r["mc_ci_high"]) or
                                       (.93 <= r["estimate"] <= .97)),
    "guard_rate_80": lambda r: r["guard_rate"] >= .80,
    "fpr_10": lambda r: r["fpr"] <= .10,
    "power_70": lambda r: r["power"] >= .70,
    "auc_55": lambda r: abs(r["estimate"] - .5) <= .05,
    "error_10": lambda r: r["estimate"] <= .10,
    "rank_accuracy_80": lambda r: r["estimate"] >= .80,
}


def _wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0: return (math.nan, math.nan)
    z = 1.96; p = k/n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return max(0., c-h), min(1., c+h)


def _row_targets(world: str, scenario: str, metric_type: str) -> list[str]:
    """Assign narrow theory targets from the row's actual estimand."""
    if world == "SIM-W0": return ["T1-prime"] if scenario.startswith("T1") else ["T2-prime"]
    if world == "SIM-W1": return ["T1-prime-stationary-mean-variance"]
    if world == "SIM-W2": return ["T1-prime-short-memory-guard"] if "serial" not in scenario else ["zero-inflated-person-null"]
    if world == "SIM-W3": return ["T2-prime-endpoint-identification"]
    if world == "SIM-W4": return ["opportunity-identifiability"]
    if world == "SIM-W5": return ["cross-construct-lag-coupling"]
    if world == "SIM-W6": return ["above-Nyquist-frequency-nonidentifiability"] if "alias" in scenario else ["below-Nyquist-frequency-recovery"]
    if world == "SIM-W7": return ["response-operator-excitation"]
    return ["T8-prime-conditional-innovation-rank"]


def _metric(world: str, scenario: str, metric_type: str, values: list[float], truth: float,
            criterion_id: str, *, ci_hits: list[bool] | None = None,
            rate_role: str | None = None, theory_targets: list[str] | None = None) -> dict[str, Any]:
    a = np.asarray(values, float); estimate = float(a.mean()); bias = estimate - truth
    if rate_role or ci_hits is not None or metric_type.endswith("coverage"):
        lo, hi = _wilson(int(round(estimate * len(a))), len(a))
    elif len(a) > 1:
        b = a - truth; lo, hi = map(float, np.quantile(b, [.025, .975]))
    else:
        lo = hi = bias
    row = {"world": world, "theory_targets": theory_targets or _row_targets(world, scenario, metric_type), "scenario": scenario,
           "metric_type": metric_type, "estimate": estimate, "truth": float(truth), "bias": float(bias),
           "mc_ci_low": lo, "mc_ci_high": hi,
           "ci_coverage": float(np.mean(ci_hits)) if ci_hits is not None else None,
           "fpr": estimate if rate_role == "fpr" else None,
           "power": estimate if rate_role == "power" else None,
           "guard_rate": estimate if rate_role == "guard" else None,
           "criterion_id": criterion_id}
    row["verdict"] = "pass" if CRITERIA[criterion_id](row) else "fail"
    return row


def _gamma(kind: str, m: int) -> np.ndarray:
    h=np.arange(m)
    if kind=="iid": return np.r_[1.,np.zeros(m-1)]
    if kind=="ma1": return np.r_[1.2025,.45,np.zeros(max(0,m-2))][:m]
    if kind=="ar1": return .6**h/(1-.6**2)
    a1,a2=.55,-.25; g=np.zeros(m); g[0]=1/(1-a1*(a1/(1-a2))-a2*(a1*a1/(1-a2)+a2))
    if m>1:g[1]=a1*g[0]/(1-a2)
    for k in range(2,m):g[k]=a1*g[k-1]+a2*g[k-2]
    return g


def _ar_paths(rng: np.random.Generator, count: int, m: int, phi: float) -> np.ndarray:
    e=rng.standard_normal((count,m+300)); x=np.zeros_like(e)
    for k in range(1,x.shape[1]):x[:,k]=phi*x[:,k-1]+e[:,k]
    return x[:,-m:]


def _paths(rng: np.random.Generator, kind: str, count: int, m: int) -> np.ndarray:
    if kind=="iid": return rng.standard_normal((count,m))
    if kind=="ma1":
        e=rng.standard_normal((count,m+1)); return e[:,1:]+.45*e[:,:-1]
    if kind=="ar1": return _ar_paths(rng,count,m,.6)
    if kind=="ar2":
        e=rng.standard_normal((count,m+300));x=np.zeros_like(e)
        for k in range(2,x.shape[1]):x[:,k]=.55*x[:,k-1]-.25*x[:,k-2]+e[:,k]
        return x[:,-m:]
    raise ValueError(kind)


def _auc(a: np.ndarray, b: np.ndarray) -> float:
    return float((a[:,None]>b[None,:]).mean()+.5*(a[:,None]==b[None,:]).mean())


def _perm_serial_p(rng: np.random.Generator, z: np.ndarray, permutations: int) -> float:
    def score(a: np.ndarray) -> float:
        vals=[]
        for v in a:
            c=v-v.mean(); vals.append(np.mean(c[:-1]*c[1:])/max(np.mean(c*c),1e-12))
        return abs(float(np.mean(vals)))
    obs=score(z); null=[score(np.array([rng.permutation(v) for v in z])) for _ in range(permutations)]
    return (1+sum(v>=obs for v in null))/(permutations+1)


def _decay_guard(x: np.ndarray) -> bool:
    ms=np.array([4,8,16,32]); vals=[]
    for m in ms:
        chunks=x[:len(x)//m*m].reshape(-1,m); vals.append(np.var(chunks.mean(1)))
    slope=np.polyfit(np.log(ms),np.log(np.maximum(vals,1e-12)),1)[0]
    spectrum=np.abs(np.fft.rfft(x-x.mean()))**2
    concentration=float(spectrum[1:].max()/max(spectrum[1:].sum(),1e-12))
    return bool(slope > -.60 or concentration > .20)


def flow_standard_error(v_s: float, v_delta: float, n: int, m: int) -> float:
    """SE for V_s - V_delta/(m-1)^2 from two independent samples.

    Each sample variance has approximate variance 2*V^2/(n-1). Independence
    therefore makes the two contributions additive after endpoint scaling.
    """
    endpoint_scale = (m - 1) ** 2
    return math.sqrt(2 * v_s**2 / (n - 1) +
                     2 * (v_delta / endpoint_scale) ** 2 / (n - 1))


def _chi2_quantile_wh(probability: float, df: int) -> float:
    """Wilson-Hilferty chi-square quantile approximation using stdlib NormalDist."""
    z = NormalDist().inv_cdf(probability)
    return df * (1 - 2/(9*df) + z*math.sqrt(2/(9*df)))**3


def variance_interval(sample_variance: float, n: int, alpha: float = .05) -> tuple[float, float]:
    """Approximate normal-theory variance CI via Wilson-Hilferty quantiles."""
    df=n-1
    return (df*sample_variance/_chi2_quantile_wh(1-alpha/2,df),
            df*sample_variance/_chi2_quantile_wh(alpha/2,df))


def flow_bonferroni_interval(v_s: float, v_delta: float, n: int, m: int) -> tuple[float, float]:
    """97.5%+97.5% Bonferroni interval for two independent variance estimates.

    Chi-square quantiles use the Wilson-Hilferty approximation because scipy is
    intentionally not a dependency of this simulation package.
    """
    df=n-1; q_lo=_chi2_quantile_wh(.0125,df); q_hi=_chi2_quantile_wh(.9875,df)
    vs_lo,vs_hi=df*v_s/q_hi,df*v_s/q_lo
    vd_lo,vd_hi=df*v_delta/q_hi,df*v_delta/q_lo
    scale=(m-1)**2
    return vs_lo-vd_hi/scale,vs_hi-vd_lo/scale


def flow_parametric_bootstrap_interval(
    rng: np.random.Generator,
    v_s: float,
    v_delta: float,
    n: int,
    m: int,
    draws: int,
) -> tuple[float, float]:
    """Gaussian parametric-bootstrap CI for a difference of variances.

    The slope and calibration samples are independent. Under the licensed
    normal world, each sample variance is a scaled chi-square variate. The
    bootstrap therefore propagates uncertainty from both variance estimates.
    """
    if draws < 100:
        raise ValueError("draws must be at least 100")
    df = n - 1
    scale = (m - 1) ** 2
    estimate = v_s - v_delta / scale
    boot = (v_s * rng.chisquare(df, draws) / df
            - (v_delta * rng.chisquare(df, draws) / df) / scale)
    err_lo, err_hi = np.quantile(boot - estimate, [.025, .975])
    return float(estimate - err_hi), float(estimate - err_lo)


def m3_equivalent_samples(rng: np.random.Generator, n: int) -> tuple[np.ndarray,np.ndarray]:
    out=[]
    for flow,g2 in ((.4,0.),(.2,-.4)):
        cov=np.array([[1.,0.,g2],[0.,1.,0.],[g2,0.,1.]])
        gust=rng.multivariate_normal(np.zeros(3),cov,n); b=rng.normal(0,math.sqrt(flow),n)
        out.append(b+(gust[:,2]-gust[:,0])/2)
    return out[0],out[1]


def opportunity_identifiable(observed: bool) -> bool:
    return observed


def recover_response(x: np.ndarray,y: np.ndarray)->tuple[np.ndarray,float]:
    return np.linalg.pinv(x)@y,float(np.linalg.cond(x))


def run_world(world_index: int, rng: np.random.Generator, cfg: dict[str,Any])->list[dict[str,Any]]:
    world=f"SIM-W{world_index}"; mc=int(cfg["mc"]); n=int(cfg["paths_per_mc"]); perms=int(cfg["null_permutations"]); nested=int(cfg["nested_bootstrap"]); rows=[]
    if world_index==0:
        g=np.array([[[1.,.2],[.2,2.]],[[.3,-.1],[.05,.4]],np.zeros((2,2))]);
        cov=np.block([[g[abs(i-j)] if i<=j else g[abs(i-j)].T for j in range(3)] for i in range(3)])
        k=np.kron(np.ones((1,3))/3,np.eye(2)); err=np.max(abs(stationary_mean_variance(g,3)-k@cov@k.T))
        ell,q,cross=three_point_mixed_moments(np.array([[.4]]),np.array([[[1.]],[[.2]],[[.1]]]))
        rows=[_metric(world,"T1_toeplitz","algebra_error",[err],0.,"exact_1e-10"),
              _metric(world,"T2_three_point","algebra_error",[max(abs(ell.item()-.85),abs(q.item()-23/30),abs(cross.item()))],0.,"exact_1e-10")]
    elif world_index==1:
        for kind in ("iid","ma1","ar1","ar2"):
            for m in (3,5,8,16):
                truth=float(stationary_mean_variance(_gamma(kind,m),m)); est=[]; hits=[]
                for _ in range(mc):
                    means=_paths(rng,kind,n,m).mean(1); v=float(np.var(means,ddof=1)); est.append(v)
                    lo,hi=variance_interval(v,n);hits.append(lo<=truth<=hi)
                rows += [_metric(world,f"{kind}_m{m}","mean_variance_bias",est,truth,"bias_15pct"),
                         _metric(world,f"{kind}_m{m}","ci_coverage",[float(x) for x in hits],.95,"coverage_nominal_95",ci_hits=hits)]
    elif world_index==2:
        for name,kind in (("short_memory_iid","iid"),("short_memory_ar06","ar1")):
            false_guards=[]
            for _ in range(mc):
                x=rng.standard_normal(2048) if kind=="iid" else _ar_paths(rng,1,2048,.6)[0]
                false_guards.append(_decay_guard(x))
            rows.append(_metric(world,name,"decay_guard_fpr",false_guards,0.,"fpr_10",rate_role="fpr"))
        for name in ("near_unit_ar098","unit_root","random_phase_periodic","multiscale_ar_mixture"):
            detected=[]
            for _ in range(mc):
                length=2048; e=rng.standard_normal(length)
                if name=="near_unit_ar098": x=_ar_paths(rng,1,length,.98)[0]
                elif name=="unit_root": x=np.cumsum(e)
                elif name=="random_phase_periodic": x=np.sin(2*np.pi*np.arange(length)/16+rng.uniform(0,2*np.pi))+.2*e
                else: x=sum(w*_ar_paths(rng,1,length,p)[0] for w,p in zip((.5,.3,.15,.05),(.3,.7,.93,.985)))
                detected.append(_decay_guard(x))
            rows.append(_metric(world,name,"guard_detection_rate",detected,1.,"guard_rate_80",rate_role="guard"))
        for alternative in (False,True):
            reject=[]
            for _ in range(mc):
                persons,occ=30,16; h=rng.beta(2,3,persons); z=np.zeros((persons,occ))
                latent=np.zeros((persons,occ))
                if alternative:
                    for t in range(1,occ):latent[:,t]=.75*latent[:,t-1]+rng.normal(0,.7,persons)
                for u in range(persons):
                    o=rng.poisson(rng.integers(4,15),occ); p=1/(1+np.exp(-(np.log(h[u]/(1-h[u]))+latent[u])))
                    z[u]=rng.binomial(o,p)/np.maximum(o,1)
                reject.append(_perm_serial_p(rng,z,perms)<=.05)
            role="power" if alternative else "fpr"; crit="power_70" if alternative else "fpr_10"
            rows.append(_metric(world,"zero_inflated_serial_"+role,role,reject,1. if alternative else 0.,crit,rate_role=role))
    elif world_index==3:
        aucs=[]
        for _ in range(mc): a,b=m3_equivalent_samples(rng,n); aucs.append(_auc(a,b))
        rows.append(_metric(world,"m3_observational_equivalence","classification_auc",aucs,.5,"auc_55"))
        for m in (5,8):
            est=[];hits=[];truth=.35
            for _ in range(mc):
                b=rng.normal(0,math.sqrt(truth),n);g=_ar_paths(rng,n,m,.45);s=b+(g[:,-1]-g[:,0])/(m-1)
                cal=_ar_paths(rng,n,m,.45)
                v_s=float(np.var(s,ddof=1))
                v_delta=float(np.var(cal[:,-1]-cal[:,0],ddof=1))
                v=v_s-v_delta/(m-1)**2
                est.append(v)
                lo,hi=flow_parametric_bootstrap_interval(rng,v_s,v_delta,n,m,nested)
                hits.append(lo<=truth<=hi)
            rows += [_metric(world,f"flow_m{m}","flow_bias",est,truth,"bias_15pct"),_metric(world,f"flow_m{m}","ci_coverage",hits,.95,"coverage_nominal_95",ci_hits=hits)]
    elif world_index==4:
        for label,lam in (("high",6.),("low",.25)):
            hits=[];reject=[];est=[]
            for _ in range(mc):
                o=rng.poisson(lam,n);y=rng.binomial(o,.3);total=max(o.sum(),1);ph=y.sum()/total;est.append(ph)
                lo,hi=_wilson(int(y.sum()),int(total));hits.append(lo<=.3<=hi);reject.append(abs(ph-.1)>1.96*math.sqrt(max(.1*.9/total,1e-12)))
            rows += [_metric(world,f"observed_O_{label}","rate_bias",est,.3,"bias_15pct"),_metric(world,f"observed_O_{label}","ci_coverage",hits,.95,"coverage_nominal_95",ci_hits=hits),_metric(world,f"observed_O_{label}","power",reject,1.,"power_70",rate_role="power")]
        aucs=[]
        for _ in range(mc):
            y1=rng.poisson(4*.25,n);y2=rng.poisson(2*.5,n);aucs.append(_auc(y1,y2))
        rows.append(_metric(world,"hidden_O_poisson_thinning_equivalence","classification_auc",aucs,.5,"auc_55"))
    elif world_index==5:
        for planted,role,crit in ((0.,"fpr","fpr_10"),(.45,"power","power_70")):
            reject=[];est=[]
            for _ in range(mc):
                a=np.array([[.35,planted],[0.,.25]]);x=np.zeros((n+100,2));e=rng.standard_normal(x.shape)
                for t in range(1,len(x)):x[t]=a@x[t-1]+e[t]
                xx=x[100:-1];y=x[101:,0];beta=np.linalg.lstsq(xx,y,rcond=None)[0];res=y-xx@beta;s2=res@res/(len(y)-2);se=math.sqrt(s2*np.linalg.inv(xx.T@xx)[1,1]);est.append(beta[1]);reject.append(abs(beta[1]/se)>1.96)
            rows += [_metric(world,f"A01_{planted:g}","coupling_bias",est,planted,"bias_15pct"),_metric(world,f"A01_{planted:g}",role,reject,1. if planted else 0.,crit,rate_role=role)]
    elif world_index==6:
        # At integer samples, f_low and f_high=1-f_low induce the same family:
        # sin(2*pi*f_high*t + pi-phi) == sin(2*pi*f_low*t + phi).
        # No generator frequency is exposed to a guard or classifier.
        aucs=[];f_low=.18;length=256
        for _ in range(mc):
            low_features=[];high_features=[];t=np.arange(length)
            for _j in range(n):
                phi=rng.uniform(0,2*np.pi)
                low=np.sin(2*np.pi*f_low*t+phi)+.35*rng.standard_normal(length)
                phi_high=rng.uniform(0,2*np.pi)
                high=np.sin(2*np.pi*(1-f_low)*t+phi_high)+.35*rng.standard_normal(length)
                for series,bucket in ((low,low_features),(high,high_features)):
                    spec=np.abs(np.fft.rfft(series-series.mean()))**2
                    bucket.append(float(np.sum(np.arange(len(spec))*spec)/np.sum(spec)))
            aucs.append(_auc(np.asarray(low_features),np.asarray(high_features)))
        rows.append(_metric(world,"above_Nyquist_alias_equivalence","classification_auc",aucs,.5,"auc_55",
                            theory_targets=["above-Nyquist-original-frequency-nonidentifiability"]))
        recovered=[];target=.12
        for _ in range(mc):
            t=np.arange(length);phi=rng.uniform(0,2*np.pi)
            x=np.sin(2*np.pi*target*t+phi)+.35*rng.standard_normal(length)
            peak=np.argmax(np.abs(np.fft.rfft(x-x.mean()))[1:])+1
            recovered.append(abs(peak/length-target)<=1/length)
        rows.append(_metric(world,"below_Nyquist_frequency","frequency_recovery_accuracy",recovered,1.,"rank_accuracy_80",
                            theory_targets=["below-Nyquist-frequency-recovery"]))
    elif world_index==7:
        truth=np.array([[1.2,-.3],[.4,.8]])
        for eps in (0.,.01,.02,.05,.1,.25,1.):
            guards=[];errors=[]
            for _ in range(mc):
                x=rng.standard_normal((n,2));x[:,1]=x[:,0]+eps*x[:,1];cond=np.linalg.cond(x);guards.append(cond>50)
                rh,_=recover_response(x,x@truth.T+rng.normal(0,.08,(n,2)))
                if cond<=50:errors.append(np.linalg.norm(rh.T-truth)/np.linalg.norm(truth))
            scenario=f"condition_sweep_eps_{eps:g}"
            if eps in (0.,.01,.02):
                rows.append(_metric(world,scenario,"excitation_guard_rate",guards,1.,"guard_rate_80",rate_role="guard",
                                    theory_targets=["response-operator-weak-excitation-guard"]))
            else:
                rows.append(_metric(world,scenario,"excitation_guard_fpr",guards,0.,"fpr_10",rate_role="fpr",
                                    theory_targets=["response-operator-sufficient-excitation"] if eps==1. else ["response-operator-condition-number-curve"]))
            if eps==1.:
                rows.append(_metric(world,scenario,"response_relative_error",errors,0.,"error_10",
                                    theory_targets=["response-operator-recovery"]))
    else:
        threshold=.12;band=(.055,.21)
        for eigenvalue in (.03,.08,.12,.18,.3):
            guarded=[];correct=[]
            for _ in range(mc):
                x=rng.standard_normal((n,2));noise=np.zeros((n,2));noise[:,0]=rng.normal(0,math.sqrt(eigenvalue),n)
                y=x@np.array([[.6,.2],[-.1,.5]]).T+noise;cov=np.cov(np.c_[x,y],rowvar=False)
                schur,_=conditional_innovation(cov,[0,1],[2,3]);observed=float(np.linalg.eigvalsh(schur)[-1])
                is_guard=band[0]<=observed<=band[1];guarded.append(is_guard)
                if not is_guard:correct.append((observed>threshold)==(eigenvalue>threshold))
            boundary=eigenvalue in (.08,.12,.18);role="guard" if boundary else "fpr"
            rows.append(_metric(world,f"innovation_eigen_{eigenvalue:g}","innovation_boundary_guard_rate",guarded,1. if boundary else 0.,
                                "guard_rate_80" if boundary else "fpr_10",rate_role=role,
                                theory_targets=["T8-prime-innovation-boundary-undecidable"] if boundary else ["T8-prime-conditional-rank-identifiable"] ))
            if correct and not boundary:
                rows.append(_metric(world,f"innovation_eigen_{eigenvalue:g}","rank_recovery_accuracy",correct,1.,"rank_accuracy_80",
                                    theory_targets=["T8-prime-conditional-rank-identifiable"]))
        correct=[]
        for _ in range(mc):
            x=rng.standard_normal((n,2));noise=rng.multivariate_normal([0,0],[[.3,.12],[.12,.3]],n)
            y=x@np.array([[.6,.2],[-.1,.5]]).T+noise;cov=np.cov(np.c_[x,y],rowvar=False)
            schur,_=conditional_innovation(cov,[0,1],[2,3]);correct.append(np.sum(np.linalg.eigvalsh(schur)>threshold)==2)
        rows.append(_metric(world,"correlated_innovation_rank2","rank_recovery_accuracy",correct,1.,"rank_accuracy_80",
                            theory_targets=["T8-prime-correlated-innovation-rank"] ))
    return rows
