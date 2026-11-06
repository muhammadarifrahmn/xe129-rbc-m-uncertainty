"""Phase 3 Task 2 (physiological-variability bands) and Task 3 (nonlinear fit / misspecification)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import mc_rbc_barrier_uncertainty as m
rng = np.random.default_rng(42)
HZ_PPM = 35.33  # Hz/ppm at 3 T
t = m.T_ARRAY

# ---------------- Task 2: bands from Kammerman 2020 relative spreads ----------------
# (whole-lung MRS, 1.5T; only relative spread applied to 3T means)
COH = {  # CV_T2rbc, CV_T2barrier, SD_shift_ppm (RBC-barrier, quadrature sum)
 "Healthy": (0.07/1.75, 0.07/2.16, np.hypot(0.8, 0.4)),
 "IPF":     (0.07/1.84, 0.08/2.29, np.hypot(0.7, 0.3)),
}
RATIO = {"Healthy": 0.50, "IPF": 0.18}
snrs = np.logspace(np.log10(5), np.log10(160), 40)
N = 2000
bands = {}
for k, (cvr, cvb, sdppm) in COH.items():
    ts_r = m.T2STAR_RBC*rng.normal(1, cvr, N)
    ts_b = rng.normal(1, cvb, N)
    df = rng.normal(0, sdppm*HZ_PPM, N)
    curves = np.empty((N, len(snrs)))
    for i in range(N):
        G = m.make_design_matrix(f_rbc=m.F_RBC+df[i], t2_rbc=ts_r[i],
                                 t2_bl=m.T2STAR_BARRIER_LORENTZ*ts_b[i],
                                 t2_bg=m.T2STAR_BARRIER_GAUSS*ts_b[i])
        curves[i] = [m.crlb_ratio_uncertainty(s, RATIO[k], G=G)/RATIO[k]*100 for s in snrs]
    bands[k] = np.percentile(curves, [5, 50, 95], axis=0)

fig, ax = plt.subplots(figsize=(8, 6))
for k, c in zip(bands, ["#1f77b4", "#d62728"]):
    lo, md, hi = bands[k]
    ax.fill_between(snrs, lo, hi, color=c, alpha=0.25)
    ax.plot(snrs, md, color=c, lw=2, label=f"{k} (RBC:M={RATIO[k]}), median and 5-95% band")
ax.set(xscale="log", yscale="log", xlabel="SNR (single acquisition)",
       ylabel="Relative uncertainty of RBC:M (%)",
       title="CRLB uncertainty bands from physiological parameter variation\n(T2* and chemical-shift spread, Kammerman 2020)")
for lv in (5, 10, 15): ax.axhline(lv, color="gray", ls=":", alpha=.5)
ax.legend(fontsize=9); ax.grid(alpha=.3, which="both")
plt.tight_layout(); plt.savefig("phase3_task2_uncertainty_bands.png", dpi=150); plt.close()
print("TASK 2: band width (95th/5th ratio) and median at SNR=20")
j = np.argmin(abs(snrs-20))
for k in bands: print(f"  {k}: median {bands[k][1][j]:.2f}%  5-95%: {bands[k][0][j]:.2f}-{bands[k][2][j]:.2f}%")
nominal = {k: m.crlb_ratio_uncertainty(snrs[j], RATIO[k])/RATIO[k]*100 for k in RATIO}
print("  nominal (fixed-parameter) at SNR=%.1f:"%snrs[j], {k: round(v,2) for k, v in nominal.items()})

# ---------------- Task 3: nonlinear fit & model misspecification ----------------
def voigt_b(f, tl, tg): return np.exp(2j*np.pi*f*t)*np.exp(-t/tl)*np.exp(-(t/tg)**2)
def lor_b(f, tl): return np.exp(2j*np.pi*f*t)*np.exp(-t/tl)

def model_A(p):  # correct form (Voigt barrier, T2G fixed), free amp/freq/T2L/phase
    ab, fb, tb, pb, ar, fr, tr, pr = p
    return ab*np.exp(1j*pb)*voigt_b(fb, tb, m.T2STAR_BARRIER_GAUSS) + ar*np.exp(1j*pr)*lor_b(fr, tr)
def model_B(p):  # misspecified: Lorentzian barrier
    ab, fb, tb, pb, ar, fr, tr, pr = p
    return ab*np.exp(1j*pb)*lor_b(fb, tb) + ar*np.exp(1j*pr)*lor_b(fr, tr)

def fit(model, y, p0):
    res = lambda p: np.concatenate([(model(p)-y).real, (model(p)-y).imag])
    lb = [0, -300, 3e-4, -1, 0, 400, 3e-4, -1]; ub = [10, 300, 2e-2, 1, 10, 1000, 1e-2, 1]
    return least_squares(res, np.clip(p0, np.add(lb, 1e-9), np.subtract(ub, 1e-9)), bounds=(lb, ub)).x

NIT = 400
print("\nTASK 3: relative RMSE (%) of RBC:M, linear-known vs nonlinear-free vs misspecified (N_avg=1)")
print(f"{'scen':8s}{'SNR':>5s}{'linear':>9s}{'CRLB':>8s}{'NL-correct':>12s}{'NL-Lorentz':>12s}{'bias_corr':>11s}{'bias_misspec':>13s}")
rows = []
for k, r in RATIO.items():
    y0 = m.simulate_ground_truth_fid(r)
    for snr in (10, 20, 40):
        sig = (1+r)/snr
        est = {"lin": [], "A": [], "B": []}
        for _ in range(NIT):
            y = y0 + rng.normal(0, sig, t.size) + 1j*rng.normal(0, sig, t.size)
            ab, ar = m.fit_amplitudes(y); est["lin"].append(ar/ab)
            p0 = [1, rng.normal(0, 20), 2e-3, 0, r, m.F_RBC+rng.normal(0, 20), 1.1e-3, 0]
            for nm, mod in (("A", model_A), ("B", model_B)):
                p = fit(mod, y, p0); est[nm].append(p[4]/p[0] if p[0] > 1e-6 else np.nan)
        out = {}
        for nm in est:
            e = np.array(est[nm]); e = e[np.isfinite(e)]
            out[nm] = (np.sqrt(np.mean((e-r)**2))/r*100, (e.mean()-r)/r*100)
        crlb = m.crlb_ratio_uncertainty(snr, r)/r*100
        print(f"{k:8s}{snr:5d}{out['lin'][0]:9.2f}{crlb:8.2f}{out['A'][0]:12.2f}{out['B'][0]:12.2f}{out['A'][1]:11.2f}{out['B'][1]:13.2f}")
