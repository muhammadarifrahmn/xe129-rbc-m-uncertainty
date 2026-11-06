"""Task 3 final: 2000 repeats, Gaussian T2* freed (9-parameter Voigt model) vs Lorentzian-barrier misspecified model."""
import numpy as np, sys
from multiprocessing import Pool
from scipy.optimize import least_squares
import mc_rbc_barrier_uncertainty as m
t = m.T_ARRAY
def vb(f, tl, tg): return np.exp(2j*np.pi*f*t)*np.exp(-t/tl)*np.exp(-(t/tg)**2)
def lb(f, tl): return np.exp(2j*np.pi*f*t)*np.exp(-t/tl)
def mA(p):  # free Voigt barrier: ab,fb,tl,tg,pb ; rbc: ar,fr,tr,pr
    ab, fb, tl, tg, pb, ar, fr, tr, pr = p
    return ab*np.exp(1j*pb)*vb(fb, tl, tg) + ar*np.exp(1j*pr)*lb(fr, tr)
def mB(p):
    ab, fb, tl, pb, ar, fr, tr, pr = p
    return ab*np.exp(1j*pb)*lb(fb, tl) + ar*np.exp(1j*pr)*lb(fr, tr)
LA = [0, -300, 3e-4, 5e-4, -1, 0, 400, 3e-4, -1]; UA = [10, 300, 2e-2, 2e-2, 1, 10, 1000, 1e-2, 1]
LB = [0, -300, 3e-4, -1, 0, 400, 3e-4, -1];       UB = [10, 300, 2e-2, 1, 10, 1000, 1e-2, 1]
def fit(mod, y, p0, lo, hi):
    res = lambda p: np.concatenate([(mod(p)-y).real, (mod(p)-y).imag])
    p0 = np.clip(p0, np.add(lo, 1e-9), np.subtract(hi, 1e-9))
    s = least_squares(res, p0, bounds=(lo, hi))
    edge = np.any((np.abs(s.x-lo) < 1e-6*np.abs(np.subtract(hi, lo))) | (np.abs(s.x-hi) < 1e-6*np.abs(np.subtract(hi, lo))))
    return s.x, edge
def job(a):
    r, snr, seed = a
    rng = np.random.default_rng(seed)
    y0 = m.simulate_ground_truth_fid(r); sig = (1+r)/snr
    y = y0 + rng.normal(0, sig, t.size) + 1j*rng.normal(0, sig, t.size)
    ab, ar = m.fit_amplitudes(y); lin = ar/ab
    j = lambda s: rng.normal(0, s)
    pA, eA = fit(mA, y, [1, j(20), 2e-3*(1+.2*j(1)), 3e-3*(1+.2*j(1)), 0, r, m.F_RBC+j(20), 1.1e-3*(1+.2*j(1)), 0], LA, UA)
    pB, eB = fit(mB, y, [1, j(20), 2e-3*(1+.2*j(1)), 0, r, m.F_RBC+j(20), 1.1e-3*(1+.2*j(1)), 0], LB, UB)
    return lin, pA[5]/pA[0] if pA[0] > 1e-6 else np.nan, pB[4]/pB[0] if pB[0] > 1e-6 else np.nan, eA, eB
if __name__ == "__main__":
    N = 2000; RATIO = {"Healthy": 0.5, "IPF": 0.18}
    print(f"{'scen':8s}{'SNR':>5s}{'CRLB':>7s}{'linear':>8s}{'NL-Voigt':>10s}{'biasV':>7s}{'edge%V':>8s}{'NL-Lor':>8s}{'biasL':>7s}")
    with Pool() as pool:
        for k, r in RATIO.items():
            for snr in (10, 20, 40):
                out = np.array(pool.map(job, [(r, snr, 1000*snr+i+(7 if k == 'IPF' else 0)*100000) for i in range(N)], chunksize=20), dtype=float)
                st = lambda e: (np.sqrt(np.nanmean((e[np.isfinite(e)]-r)**2))/r*100, (np.nanmean(e)-r)/r*100)
                l, a, b = st(out[:, 0]), st(out[:, 1]), st(out[:, 2])
                print(f"{k:8s}{snr:5d}{m.crlb_ratio_uncertainty(snr, r)/r*100:7.2f}{l[0]:8.2f}{a[0]:10.2f}{a[1]:7.2f}{100*out[:,3].mean():8.1f}{b[0]:8.2f}{b[1]:7.2f}", flush=True)
