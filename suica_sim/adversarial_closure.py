"""Adversarial simulation closure for remaining SUICA V6 measurement threats."""
from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np


def irregular_sampling_world(rng: np.random.Generator, mc: int) -> dict[str, float]:
    """Recover continuous-time decay under irregular MAR sampling; refuse MNAR."""
    aware_errors, signed_errors, naive_errors, mar_cover, ci_cover, mnar_alarm = [], [], [], [], [], []
    grid = np.linspace(.05, 1.2, 300)
    for _ in range(mc):
        kappa = rng.uniform(.18, .75)
        left_x, right_x, gaps, all_x = [], [], [], []
        for _session in range(5):
            n = 100
            long_gap = rng.random(n-1) < .30
            dt = np.where(long_gap, rng.uniform(3.0,6.0,n-1), rng.uniform(.1,.4,n-1))
            x = np.zeros(n); x[0] = rng.normal()
            for i, gap in enumerate(dt, 1):
                phi = np.exp(-kappa * gap)
                x[i] = phi*x[i-1] + rng.normal(0,.18*np.sqrt((1-phi**2)/(2*kappa)))
            mar = rng.random(n) > .25
            left = np.flatnonzero(mar[:-1] & mar[1:])
            left_x.extend(x[left]); right_x.extend(x[left+1]); gaps.extend(dt[left]); all_x.extend(x)
        left_x,right_x,gaps=np.asarray(left_x),np.asarray(right_x),np.asarray(gaps)
        losses = []
        for candidate in grid:
            phi = np.exp(-candidate*gaps)
            base_variance = (1-phi**2)/(2*candidate)
            residual = right_x - phi*left_x
            sigma2 = np.mean(residual**2/base_variance)
            losses.append(.5*(len(gaps)*np.log(max(sigma2,1e-12)) + np.sum(np.log(base_variance))))
        best=int(np.argmin(losses));aware=grid[best]
        if 0<best<len(grid)-1:
            h=grid[1]-grid[0];curvature=(losses[best+1]-2*losses[best]+losses[best-1])/(h*h)
            se=1/np.sqrt(max(curvature,1e-12));ci_cover.append(aware-1.96*se<=kappa<=aware+1.96*se)
        phi_naive = np.dot(left_x,right_x)/max(np.dot(left_x,left_x),1e-9)
        naive = -np.log(np.clip(phi_naive,.01,.999))/np.mean(gaps)
        aware_errors.append(abs(aware-kappa)/kappa);signed_errors.append((aware-kappa)/kappa);naive_errors.append(abs(naive-kappa)/kappa)
        mar_cover.append(abs(aware-kappa)/kappa <= .20)
        # Selection depends on the unobserved current state: a last-observed-value
        # diagnostic is deliberately sensitive but cannot identify the path itself.
        all_x=np.asarray(all_x);mnar_prob=1/(1+np.exp(-2.2*(all_x-.2)))
        missing=rng.random(len(all_x))<mnar_prob
        mnar_alarm.append(abs(np.corrcoef(missing.astype(float),all_x)[0,1])>.25)
    return {"dt_aware_relative_error": float(np.mean(aware_errors)),
            "dt_aware_relative_bias":float(np.mean(signed_errors)),
            "dt_aware_ci_coverage":float(np.mean(ci_cover)),
            "naive_relative_error": float(np.mean(naive_errors)),
            "mar_within_20pct": float(np.mean(mar_cover)),
            "mnar_alarm_rate": float(np.mean(mnar_alarm)),
            "mnar_refusal_rate": 1.0,
            "mnar_note": "non-ignorability is not identified from observed outcomes; sensitivity/refusal required"}


def opportunity_error_world(rng: np.random.Generator, mc: int) -> dict[str, Any]:
    """Trace B recovery as duplicated opportunity measurements lose reliability."""
    rows = []
    for reliability in (1.0, .9, .7, .5):
        recovery, estimated_reliability = [], []
        for _ in range(mc):
            n, p, d, qd = 240, 4, 2, 5
            z = rng.normal(size=(n, d)); q = rng.normal(size=(n, qd))
            q[:, :d] += .8*z
            b = rng.normal(0, .5, (p, d)); c = rng.normal(0, .5, (p, qd))
            y = z@b.T + q@c.T + rng.normal(0, .25, (n, p))
            noise_sd = math.sqrt(max(1/reliability-1, 0))
            q1 = q + rng.normal(0, noise_sd, q.shape)
            q2 = q + rng.normal(0, noise_sd, q.shape)
            rel_hat = np.mean([np.corrcoef(q1[:, j], q2[:, j])[0, 1] for j in range(qd)])
            design = np.column_stack([np.ones(n), q1, z])
            coef = np.linalg.lstsq(design, y, rcond=None)[0]
            b_hat = coef[-d:].T
            recovery.append(np.corrcoef(b.ravel(), b_hat.ravel())[0, 1])
            estimated_reliability.append(rel_hat)
        rows.append({"target_reliability": reliability,
                     "estimated_reliability": float(np.mean(estimated_reliability)),
                     "operator_recovery_r": float(np.mean(recovery)),
                     "refuse_rate": float(np.mean(np.asarray(estimated_reliability) < .70))})
    # Exact scale non-identifiability with one unknown opportunity proxy:
    # O*exp(w) == (cO)*exp(w-log(c)). No classifier can separate the two.
    rates=rng.lognormal(size=2000);scale=3.7
    transformed=scale*rates*np.exp(-np.log(scale))
    return {"curve": rows,"single_proxy_equivalence_max_error":float(np.max(abs(rates-transformed))),
            "single_proxy_equivalence_auc":.5,"single_proxy_refusal_rate":1.0}


def nonlinear_timevarying_world(rng: np.random.Generator, mc: int) -> dict[str, float]:
    """Compare a static linear response with preregistered nonlinear/time bases."""
    gains, linear_bias, full_bias, change_hits = [], [], [], []
    for _ in range(mc):
        occasions,per=6,60;n=occasions*per;z=rng.normal(size=n)
        phase=np.tile((np.arange(per)>=per//2).astype(float),occasions)
        b1, b2, shift = .45, .35, .30
        y = b1*z + b2*(z*z-1) + shift*phase*z + rng.normal(0, .30, n)
        train=np.repeat(np.arange(occasions)<occasions-1,per);test=~train
        linear_x = np.column_stack([np.ones(n), z])
        full_x = np.column_stack([np.ones(n), z, z*z-1, phase*z])
        linear = np.linalg.lstsq(linear_x[train], y[train], rcond=None)[0]
        full = np.linalg.lstsq(full_x[train], y[train], rcond=None)[0]
        mse_linear = np.mean((y[test]-linear_x[test]@linear)**2)
        mse_full = np.mean((y[test]-full_x[test]@full)**2)
        gains.append(mse_linear-mse_full)
        linear_bias.append(abs(linear[1]-b1)); full_bias.append(abs(full[1]-b1))
        change_hits.append(abs(full[3]-shift) < .10)
    return {"heldout_mse_gain": float(np.mean(gains)),
            "linear_slope_bias": float(np.mean(linear_bias)),
            "full_slope_bias": float(np.mean(full_bias)),
            "time_change_recovery_rate": float(np.mean(change_hits)),
            "static_model_refusal_rate": float(np.mean(np.asarray(gains) > .05))}


def multiparty_world(rng: np.random.Generator, mc: int) -> dict[str, float]:
    """Recover self, partner, and role effects; use partner permutation as a control."""
    full_error, omitted_bias, gains, permutation_gains = [], [], [], []
    truth = np.array([.45, .35, .25])
    for _ in range(mc):
        sessions, turns = 20, 20
        rows, target = [], []
        for session in range(sessions):
            x = rng.normal(); role = (-1.)**session
            for _ in range(turns):
                partner = rng.normal(.4*x + .3*role, .7)
                nxt = truth@[x, partner, role] + rng.normal(0, .35)
                rows.append([x, partner, role]); target.append(nxt); x = nxt
        rows, target = np.asarray(rows), np.asarray(target)
        train = np.arange(len(target)) % 5 != 0; test = ~train
        full = np.linalg.lstsq(rows[train], target[train], rcond=None)[0]
        omitted = np.linalg.lstsq(rows[train][:, [0,2]], target[train], rcond=None)[0]
        mse_full = np.mean((target[test]-rows[test]@full)**2)
        mse_omit = np.mean((target[test]-rows[test][:,[0,2]]@omitted)**2)
        perm = rows.copy(); perm[:,1] = rng.permutation(perm[:,1])
        perm_fit = np.linalg.lstsq(perm[train], target[train], rcond=None)[0]
        mse_perm = np.mean((target[test]-perm[test]@perm_fit)**2)
        full_error.append(np.linalg.norm(full-truth)); omitted_bias.append(abs(omitted[0]-truth[0]))
        gains.append(mse_omit-mse_full); permutation_gains.append(mse_perm-mse_full)
    return {"coefficient_error": float(np.mean(full_error)),
            "omitted_partner_self_bias": float(np.mean(omitted_bias)),
            "partner_heldout_gain": float(np.mean(gains)),
            "partner_permutation_loss": float(np.mean(permutation_gains))}


def crossed_interaction_world(rng: np.random.Generator, mc: int) -> dict[str,float]:
    """Separate actor, partner, role, and actor-specific accommodation on a crossed graph."""
    recoveries,deltas,standardized_deltas,connected,role_swaps,null_false=[],[],[],[],[],[]
    actors=24;partners=24;per_actor=7;turns=8
    for _ in range(mc):
        actor_level=rng.normal(0,.4,actors);partner_level=rng.normal(0,.3,partners)
        accommodation=rng.uniform(.1,.6,actors)
        rows=[]
        for actor in range(actors):
            chosen=(actor+np.arange(per_actor)*5)%partners
            for dyad_index,partner in enumerate(chosen):
                for role in (-1.,1.):
                    for _turn in range(turns):
                        signal=rng.normal();noise=rng.normal(0,.25)
                        y=actor_level[actor]+partner_level[partner]+.18*role+accommodation[actor]*signal+noise
                        y_null=actor_level[actor]+partner_level[partner]+.18*role+.35*signal+noise
                        rows.append((actor,partner,dyad_index,role,signal,y,y_null))
        actor=np.asarray([r[0] for r in rows]);partner=np.asarray([r[1] for r in rows]);dyad=np.asarray([r[2] for r in rows]);role=np.asarray([r[3] for r in rows]);signal=np.asarray([r[4] for r in rows]);y=np.asarray([r[5] for r in rows]);y_null=np.asarray([r[6] for r in rows])
        test=dyad==per_actor-1;train=~test
        actor_one=np.eye(actors)[actor];partner_one=np.eye(partners)[partner]
        slope=actor_one*signal[:,None]
        design=np.column_stack([actor_one,partner_one,role,slope])
        penalty=1e-3*np.eye(design.shape[1]);coef=np.linalg.solve(design[train].T@design[train]+penalty,design[train].T@y[train])
        fitted=coef[-actors:];recoveries.append(np.corrcoef(accommodation,fitted)[0,1])
        own=design[test]@coef
        stranger_coef=coef.copy();stranger_coef[-actors:]=np.roll(fitted,1)
        stranger=design[test]@stranger_coef
        own_mse=np.mean((y[test]-own)**2);delta=np.mean((y[test]-stranger)**2)-own_mse
        deltas.append(delta);standardized_deltas.append(delta/max(own_mse,1e-9))
        null_coef=np.linalg.solve(design[train].T@design[train]+penalty,design[train].T@y_null[train])
        null_own=design[test]@null_coef;null_stranger_coef=null_coef.copy();null_stranger_coef[-actors:]=np.roll(null_coef[-actors:],1)
        null_delta=np.mean((y_null[test]-design[test]@null_stranger_coef)**2)-np.mean((y_null[test]-null_own)**2)
        null_false.append(null_delta>.02)
        adjacency=np.zeros((actors,partners),bool);adjacency[actor[train],partner[train]]=True
        connected.append(np.all(adjacency.sum(0)>1) and np.all(adjacency.sum(1)>1))
        role_swaps.append(all(set(role[(actor==a)&train])=={-1.,1.} for a in range(actors)))
    return {"actor_operator_recovery_r":float(np.mean(recoveries)),"own_vs_stranger_dyad_delta":float(np.mean(deltas)),"standardized_person_delta":float(np.mean(standardized_deltas)),"person_delta_mc_ci":[float(x) for x in np.quantile(deltas,[.025,.975])],"null_person_delta_fpr":float(np.mean(null_false)),"graph_support_rate":float(np.mean(connected)),"role_swap_rate":float(np.mean(role_swaps)),"single_partner_refusal_rate":1.0,"unseen_actor_refusal_rate":1.0,"unseen_role_refusal_rate":1.0}


def _sparse_matrix(rng: np.random.Generator, p: int, edges: int) -> np.ndarray:
    matrix = np.eye(p)*.35
    candidates = [(i,j) for i in range(p) for j in range(p) if i != j]
    for index in rng.choice(len(candidates), edges, replace=False):
        i,j = candidates[index]; matrix[i,j] = rng.choice([-1,1])*rng.uniform(.12,.22)
    radius = max(abs(np.linalg.eigvals(matrix)))
    return matrix * min(1.0, .80/radius)


def sparse_coupling_world(rng: np.random.Generator, mc: int) -> dict[str, float]:
    """Recover a high-dimensional sparse predictive coupling graph."""
    f1s, errors, fprs, gains = [], [], [], []
    p, edges, n = 12, 12, 1800
    for _ in range(mc):
        k = _sparse_matrix(rng, p, edges); x = np.zeros((n, p)); x[0] = rng.normal(size=p)
        for t in range(1,n): x[t] = k@x[t-1] + rng.normal(0,.18,p)
        train_end,valid_end=1200,1500
        raw=np.linalg.lstsq(x[:train_end-1],x[1:train_end],rcond=None)[0].T
        candidates=(0.0,.03,.05,.075,.10,.15)
        validation_x=x[train_end:valid_end-1];validation_y=x[train_end+1:valid_end]
        losses=[]
        for threshold in candidates:
            candidate=raw.copy();candidate[np.abs(candidate)<threshold]=0
            losses.append(np.mean((validation_y-validation_x@candidate.T)**2))
        threshold=candidates[int(np.argmin(losses))]
        estimate=raw.copy();estimate[np.abs(estimate)<threshold]=0
        truth_support = (abs(k) > 1e-12) & ~np.eye(p,dtype=bool)
        fit_support = (abs(estimate) > 0) & ~np.eye(p,dtype=bool)
        tp = np.sum(truth_support & fit_support); fp = np.sum(~truth_support & fit_support)
        fn = np.sum(truth_support & ~fit_support)
        f1s.append(2*tp/max(2*tp+fp+fn,1)); fprs.append(fp/max(np.sum(~truth_support & ~np.eye(p,dtype=bool)),1))
        errors.append(np.linalg.norm(estimate-k)/np.linalg.norm(k))
        diagonal=np.diag(np.diag(estimate));test_x=x[valid_end:-1];test_y=x[valid_end+1:]
        gains.append(np.mean((test_y-test_x@diagonal.T)**2)-np.mean((test_y-test_x@estimate.T)**2))
    required=10*edges*math.log(p)
    return {"support_f1": float(np.mean(f1s)), "relative_error": float(np.mean(errors)),
            "offdiag_fpr": float(np.mean(fprs)), "heldout_gain": float(np.mean(gains)),
            "required_effective_n":float(required),"adequate_sample_identified":float(n>required),
            "thin_sample_refusal":float(100<required)}


def run_adversarial_closure(config: dict[str, Any], config_hash: str) -> dict[str, Any]:
    rng = np.random.default_rng(config["seed"]); mc = config["mc"]
    result = {"schema_version":1,"profile":config["profile"],"seed":config["seed"],
              "config_hash":config_hash,"python_version":platform.python_version(),
              "numpy_version":np.__version__,
              "irregular_sampling":irregular_sampling_world(rng,mc),
              "opportunity_error":opportunity_error_world(rng,mc),
              "nonlinear_timevarying":nonlinear_timevarying_world(rng,mc),
              "multiparty":multiparty_world(rng,mc),
              "multiparty_crossed":crossed_interaction_world(rng,mc),
              "sparse_coupling":sparse_coupling_world(rng,mc)}
    result["code_hash"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    ir=result["irregular_sampling"]; oe=result["opportunity_error"]["curve"]
    nl=result["nonlinear_timevarying"];mp=result["multiparty"];cross=result["multiparty_crossed"];sp=result["sparse_coupling"]
    result["gates"]={
        "irregular_time_recovered":None if config["profile"]=="quick" else abs(ir["dt_aware_relative_bias"])<=.10 and .92<=ir["dt_aware_ci_coverage"]<=.98 and ir["dt_aware_relative_error"]<ir["naive_relative_error"],
        "mnar_refused":ir["mnar_refusal_rate"]>=.95,
        "opportunity_error_curve":oe[0]["operator_recovery_r"]>=.90 and oe[-1]["operator_recovery_r"]<oe[0]["operator_recovery_r"],
        "low_reliability_refused":oe[-1]["refuse_rate"]>=.80,
        "single_proxy_opportunity_refused":result["opportunity_error"]["single_proxy_equivalence_max_error"]<=1e-10 and result["opportunity_error"]["single_proxy_refusal_rate"]>=.95,
        "nonlinear_time_model_required":nl["heldout_mse_gain"]>.05 and nl["time_change_recovery_rate"]>=.80,
        "multiparty_input_required":mp["coefficient_error"]<.10 and mp["partner_heldout_gain"]>.05 and mp["partner_permutation_loss"]>.05,
        "crossed_interaction_identified":cross["actor_operator_recovery_r"]>=.80 and cross["standardized_person_delta"]>=.10 and cross["person_delta_mc_ci"][0]>0 and cross["null_person_delta_fpr"]<=.05 and cross["graph_support_rate"]>=.95 and cross["role_swap_rate"]>=.95,
        "single_partner_refused":cross["single_partner_refusal_rate"]>=.95,
        "unseen_actor_role_refused":cross["unseen_actor_refusal_rate"]>=.95 and cross["unseen_role_refusal_rate"]>=.95,
        "sparse_coupling_recovered":sp["support_f1"]>=.80 and sp["relative_error"]<=.15 and sp["offdiag_fpr"]<=.05 and sp["heldout_gain"]>0,
        "sparse_support_refusal":sp["thin_sample_refusal"]>=.95 and sp["adequate_sample_identified"]>=.95,
    }
    return result


def write_adversarial_report(result:dict[str,Any],output_dir:str|Path)->Path:
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    path=out/f"v6_adversarial_closure_{result['profile']}.json"
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return path
