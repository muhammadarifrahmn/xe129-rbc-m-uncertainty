"""
Monte Carlo / Analytical CRLB Uncertainty Quantification of the RBC:M Ratio
in Hyperpolarized 129Xe Gas-Exchange MRI.

Core simulation module (rebuilt after environment reset).
Validated parameters carried over from the submitted manuscript
(NMR in Biomedicine, Manuscript ID 7081852).
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. GROUND-TRUTH SPECTRAL PARAMETERS (validated against literature)
# ----------------------------------------------------------------------
F_BARRIER = 0.0        # Hz, reference (barrier ~197.7 ppm)
F_RBC = 700.0           # Hz, offset (~19.8 ppm x 35.33 Hz/ppm @3T)

# Voigt lineshape for barrier (Bier et al. 2019 - structural heterogeneity)
T2STAR_BARRIER_LORENTZ = 2.0e-3   # s, homogeneous (Lorentzian) component
T2STAR_BARRIER_GAUSS = 3.0e-3     # s, inhomogeneous (Gaussian) component

# Pure Lorentzian for RBC
T2STAR_RBC = 1.1e-3     # s (Wang et al. 2018, 3T)

A_BARRIER_TRUE = 1.0

SCENARIOS = {
    "Healthy": 0.50,   # midpoint of 0.49-0.55 (Kaushik 2014; multisite reference)
    "IPF":     0.18,   # midpoint of 0.16-0.21 (Kaushik 2014; Rankine 2021)
}

BANDWIDTH = 8000.0      # Hz
N_SAMPLES = 512          # points (Bier et al. 2019 protocol)
DT = 1.0 / BANDWIDTH
T_ARRAY = np.arange(N_SAMPLES) * DT


def make_design_matrix(t=T_ARRAY, f_barrier=F_BARRIER, f_rbc=F_RBC,
                        t2_bl=T2STAR_BARRIER_LORENTZ, t2_bg=T2STAR_BARRIER_GAUSS,
                        t2_rbc=T2STAR_RBC):
    """Linear design matrix G = [b_barrier, b_rbc] for the two-compartment FID."""
    b_barrier = (np.exp(1j * 2 * np.pi * f_barrier * t) *
                 np.exp(-t / t2_bl) *
                 np.exp(-(t / t2_bg) ** 2))
    b_rbc = np.exp(1j * 2 * np.pi * f_rbc * t) * np.exp(-t / t2_rbc)
    return np.column_stack([b_barrier, b_rbc])


G_TRUE = make_design_matrix()


def simulate_ground_truth_fid(ratio_true, a_barrier_true=A_BARRIER_TRUE, G=None):
    if G is None:
        G = G_TRUE
    a_rbc_true = ratio_true * a_barrier_true
    coeffs = np.array([a_barrier_true, a_rbc_true], dtype=complex)
    return G @ coeffs


def add_noise(fid, snr, n_avg=1):
    """SNR defined as |S(0)| / sigma of the whole-lung (barrier-dominated) FID."""
    peak = np.abs(fid[0])
    sigma = (peak / snr) / np.sqrt(n_avg)
    noise = (np.random.normal(0, sigma, size=fid.shape) +
             1j * np.random.normal(0, sigma, size=fid.shape))
    return fid + noise, sigma


def fit_amplitudes(fid_noisy, G=G_TRUE):
    coeffs, *_ = np.linalg.lstsq(G, fid_noisy, rcond=None)
    return np.abs(coeffs[0]), np.abs(coeffs[1])


def compute_crlb(sigma, G=G_TRUE):
    """Closed-form CRLB for the linear complex least-squares amplitude estimator."""
    GhG = np.real(np.conjugate(G.T) @ G)
    cov = (sigma ** 2) * np.linalg.inv(GhG)
    return np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1])


def compute_crlb_cov(sigma, G=G_TRUE):
    GhG = np.real(np.conjugate(G.T) @ G)
    return (sigma ** 2) * np.linalg.inv(GhG)


def crlb_ratio_uncertainty(snr, ratio_true, a_barrier_true=A_BARRIER_TRUE,
                            n_avg=1, G=G_TRUE):
    """
    Analytical (closed-form) propagated CRLB standard deviation of the
    ratio R = A_rbc / A_barrier, via first-order error propagation:
        Var(R) ~= Var(A_rbc)/A_barrier^2 + (A_rbc^2/A_barrier^4) * Var(A_barrier)
    SNR is defined on the barrier-dominated whole-lung FID peak, |S(0)|, with
    peak amplitude A_barrier_true (since barrier >> RBC in whole-lung signal).
    """
    a_rbc_true = ratio_true * a_barrier_true
    # Peak of the FID at t=0 equals the SUM of compartment amplitudes
    # (both basis vectors equal 1 at t=0 regardless of frequency offset),
    # matching the convention used by add_noise()/Monte Carlo.
    peak_t0 = a_barrier_true + a_rbc_true
    sigma = (peak_t0 / snr) / np.sqrt(n_avg)
    cov = compute_crlb_cov(sigma, G=G)
    # full first-order delta method incl. covariance term
    var_ratio = (cov[1, 1] / a_barrier_true ** 2 +
                 (a_rbc_true ** 2 / a_barrier_true ** 4) * cov[0, 0] -
                 2 * a_rbc_true / a_barrier_true ** 3 * cov[0, 1])
    return np.sqrt(var_ratio)


def monte_carlo_run(snr_list, navg_list, ratio_true, a_barrier_true=A_BARRIER_TRUE,
                     n_iter=2000, label="", G=G_TRUE):
    results = {'snr': [], 'n_avg': [], 'ratio_bias': [], 'ratio_std': [],
               'ratio_rmse': [], 'ratio_std_crlb': [], 'ratio_rmse_relative': []}
    a_rbc_true = ratio_true * a_barrier_true
    fid_true = simulate_ground_truth_fid(ratio_true, a_barrier_true, G=G)
    for n_avg in navg_list:
        for snr in snr_list:
            ratio_estimates = np.zeros(n_iter)
            sigma_used = None
            for i in range(n_iter):
                fid_noisy, sigma = add_noise(fid_true, snr, n_avg=n_avg)
                sigma_used = sigma
                A_b, A_r = fit_amplitudes(fid_noisy, G=G)
                ratio_estimates[i] = A_r / A_b if A_b > 0 else np.nan
            ratio_estimates = ratio_estimates[~np.isnan(ratio_estimates)]
            bias = np.mean(ratio_estimates) - ratio_true
            std = np.std(ratio_estimates)
            rmse = np.sqrt(np.mean((ratio_estimates - ratio_true) ** 2))
            rmse_relative = rmse / ratio_true * 100
            std_ratio_crlb = crlb_ratio_uncertainty(snr, ratio_true, a_barrier_true,
                                                      n_avg=n_avg, G=G)
            results['snr'].append(snr)
            results['n_avg'].append(n_avg)
            results['ratio_bias'].append(bias)
            results['ratio_std'].append(std)
            results['ratio_rmse'].append(rmse)
            results['ratio_std_crlb'].append(std_ratio_crlb)
            results['ratio_rmse_relative'].append(rmse_relative)
    return results


def fit_power_law(snr_array, rmse_array):
    log_snr = np.log(snr_array)
    log_rmse = np.log(rmse_array)
    b, log_a = np.polyfit(log_snr, log_rmse, 1)
    a = np.exp(log_a)
    pred = log_a + b * log_snr
    ss_res = np.sum((log_rmse - pred) ** 2)
    ss_tot = np.sum((log_rmse - np.mean(log_rmse)) ** 2)
    r_squared = 1 - ss_res / ss_tot
    return a, b, r_squared


EXTERNAL_DATA = {
    "Healthy": (9.2, 9.9), "Healthy-NA": (5.9, 15.0), "Post-COVID": (4.9, 17.2),
    "PC-RLA": (3.4, 19.5), "COPD": (2.1, 27.6),
}
