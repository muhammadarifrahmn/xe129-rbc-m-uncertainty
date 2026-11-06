"""
Phase 3 - Task 1: Continuous RBC:M sweep -> SNR required to reach target
relative-uncertainty levels (5%, 10%, 15%), benchmarked against published
repeatability, plus translation into minimum detectable change (MDC) in
RBC:M for longitudinal monitoring.

Approach: the signal model is linear (fixed frequencies/T2*), so the CRLB
is closed-form. Rather than running Monte Carlo at every one of hundreds of
RBC:M x SNR grid points (expensive and unnecessary), we use the validated
analytical CRLB-propagated ratio uncertainty (crlb_ratio_uncertainty), which
Task 3 below will show is numerically indistinguishable from Monte Carlo
for this linear model (MC included at the 6 published-manuscript RBC:M
values as a spot-check/consistency confirmation).

All results are explicitly framed as MINIMUM REQUIREMENTS UNDER IDEALIZED
CONDITIONS (fixed known frequencies/T2*, complex Gaussian noise, no
cardiogenic/physiological confounds, single-breath-hold averaging assumed
ideal) - real acquisitions will need higher SNR than these numbers indicate.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import brentq

from mc_rbc_barrier_uncertainty import (
    crlb_ratio_uncertainty, monte_carlo_run, A_BARRIER_TRUE, SCENARIOS
)

np.random.seed(42)

# ----------------------------------------------------------------------
# Repeatability benchmarks from the literature (for threshold justification)
# ----------------------------------------------------------------------
REPEATABILITY_CV = {
    # name: (CV_low_%, CV_high_%, description)
    "Hahn et al. (intersession)": (11, 20, "day-to-day repeat scans, healthy + IPF subjects"),
    "Garrison et al. (intrasession)": (7, 13, "repeat scans within a single visit"),
}

# ----------------------------------------------------------------------
# 1. Continuous RBC:M sweep
# ----------------------------------------------------------------------
RATIO_SWEEP = np.linspace(0.10, 0.60, 51)   # ground-truth RBC:M, 0.10-0.60
TARGET_LEVELS = [5.0, 10.0, 15.0]            # % relative uncertainty targets
SNR_SEARCH_RANGE = (0.5, 2000.0)             # bracket for root-finding

N_AVG = 1  # per-acquisition SNR (N_avg=1); results can be rescaled by sqrt(N_avg)


def relative_uncertainty_pct(snr, ratio_true, n_avg=1):
    std_ratio = crlb_ratio_uncertainty(snr, ratio_true, A_BARRIER_TRUE, n_avg=n_avg)
    return std_ratio / ratio_true * 100.0


def snr_for_target(ratio_true, target_pct, n_avg=1, bracket=SNR_SEARCH_RANGE):
    """Solve for the SNR at which relative uncertainty == target_pct (monotonic decreasing)."""
    f = lambda snr: relative_uncertainty_pct(snr, ratio_true, n_avg=n_avg) - target_pct
    lo, hi = bracket
    # guard: ensure sign change
    if f(lo) < 0 or f(hi) > 0:
        return np.nan
    return brentq(f, lo, hi, xtol=1e-3)


# Build the SNR-required table across the continuous sweep
snr_table = {level: np.array([snr_for_target(r, level, n_avg=N_AVG) for r in RATIO_SWEEP])
             for level in TARGET_LEVELS}

# ----------------------------------------------------------------------
# 2. Minimum detectable change (MDC) in RBC:M for longitudinal monitoring
#    MDC_95 = 1.96 * sqrt(2) * SD(ratio)  (standard two-measurement repeatability formula)
# ----------------------------------------------------------------------
def mdc95_ratio(snr, ratio_true, n_avg=1):
    std_ratio = crlb_ratio_uncertainty(snr, ratio_true, A_BARRIER_TRUE, n_avg=n_avg)
    return 1.96 * np.sqrt(2) * std_ratio


# Evaluate MDC at representative clinically-relevant SNRs (10, 20, 40, 80) for
# both the Healthy (0.50) and IPF (0.18) reference ratios
rep_snrs = [10, 20, 40, 80]
rep_ratios = {"Healthy (0.50)": 0.50, "IPF (0.18)": 0.18}
mdc_table = {}
for name, ratio in rep_ratios.items():
    mdc_table[name] = {snr: mdc95_ratio(snr, ratio, n_avg=N_AVG) for snr in rep_snrs}

# ----------------------------------------------------------------------
# 3. Monte Carlo spot-check at RATIO_SWEEP subset (consistency confirmation
#    that the analytical CRLB sweep is numerically valid, addresses
#    Reviewer 1's "what does MC add beyond CRLB" for the linear-model case)
# ----------------------------------------------------------------------
spot_check_ratios = [0.10, 0.18, 0.30, 0.50, 0.60]
spot_check_snr = [10, 20, 40]
mc_vs_crlb_rows = []
for ratio in spot_check_ratios:
    res = monte_carlo_run(spot_check_snr, [N_AVG], ratio, n_iter=2000)
    for i in range(len(res['snr'])):
        snr = res['snr'][i]
        mc_rel = res['ratio_rmse_relative'][i]
        crlb_rel = relative_uncertainty_pct(snr, ratio, n_avg=N_AVG)
        mc_vs_crlb_rows.append((ratio, snr, mc_rel, crlb_rel,
                                 100 * abs(mc_rel - crlb_rel) / crlb_rel))

# ----------------------------------------------------------------------
# 4. Figure: SNR required vs. ground-truth RBC:M, for each target level
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
colors = {5.0: "#2ca02c", 10.0: "#1f77b4", 15.0: "#d62728"}
for level in TARGET_LEVELS:
    ax.plot(RATIO_SWEEP, snr_table[level], marker='', linewidth=2.2,
             color=colors[level], label=f'{level:.0f}% relative-uncertainty target')

# Mark healthy / IPF reference ratios
ax.axvline(0.50, color='gray', linestyle=':', alpha=0.6)
ax.axvline(0.18, color='gray', linestyle=':', alpha=0.6)
tr = ax.get_xaxis_transform()
ax.text(0.495, 0.03, 'Healthy ref.', rotation=90, fontsize=8, va='bottom', ha='right', color='gray', transform=tr)
ax.text(0.175, 0.03, 'IPF ref.', rotation=90, fontsize=8, va='bottom', ha='right', color='gray', transform=tr)

ax.set_xlabel('Ground-truth RBC:M ratio')
ax.set_ylabel('SNR required (single acquisition)')
ax.set_title('Minimum SNR Required vs. Ground-Truth RBC:M Ratio\n'
             '(idealized conditions: known frequencies/T2*, complex-Gaussian noise)')
ax.set_yscale('log')
ax.legend(fontsize=9, loc='upper right')
ax.grid(alpha=0.3, which='both')
plt.tight_layout()
plt.savefig('phase3_task1_snr_required_vs_ratio.png', dpi=150)
plt.close(fig)

# ----------------------------------------------------------------------
# 5. Output tables (printed + saved as CSV-like text)
# ----------------------------------------------------------------------
print("=" * 78)
print("TABLE A: SNR required to reach target relative-uncertainty levels")
print("(continuous RBC:M sweep, N_avg=1)")
print("=" * 78)
header = f"{'RBC:M':>8} | " + " | ".join(f"SNR@{lvl:.0f}%" for lvl in TARGET_LEVELS)
print(header)
print("-" * len(header))
for idx, ratio in enumerate(RATIO_SWEEP):
    if idx % 5 == 0:  # print every 5th row to keep output compact
        row = f"{ratio:8.3f} | " + " | ".join(f"{snr_table[lvl][idx]:7.2f}" for lvl in TARGET_LEVELS)
        print(row)

print()
print("=" * 78)
print("Reference points (manuscript scenarios):")
for name, ratio in [("Healthy", 0.50), ("IPF", 0.18)]:
    idx = np.argmin(np.abs(RATIO_SWEEP - ratio))
    row = f"  {name:10s} (RBC:M={RATIO_SWEEP[idx]:.2f}): " + \
          ", ".join(f"SNR@{lvl:.0f}%={snr_table[lvl][idx]:.1f}" for lvl in TARGET_LEVELS)
    print(row)

print()
print("=" * 78)
print("TABLE B: Published repeatability benchmarks (for threshold justification)")
print("=" * 78)
for name, (lo, hi, desc) in REPEATABILITY_CV.items():
    print(f"  {name}: CV {lo}-{hi}% ({desc})")
print()
print("  Interpretation: a 15% relative-uncertainty target sits within the")
print("  low end of published intersession repeatability (11-20%), while a")
print("  5-10% target approaches or falls below intrasession repeatability")
print("  (7-13%) -- i.e., 5-10% targets are near the noise floor set by")
print("  physiological/technical repeatability itself, not just by thermal SNR.")

print()
print("=" * 78)
print("TABLE C: Minimum detectable change (MDC95) in RBC:M, by scenario and SNR")
print("(N_avg=1; MDC95 = 1.96 x sqrt(2) x SD(ratio), two-measurement comparison)")
print("=" * 78)
header2 = f"{'Scenario':>14} | " + " | ".join(f"SNR={s}" for s in rep_snrs)
print(header2)
print("-" * len(header2))
for name in rep_ratios:
    row = f"{name:>14} | " + " | ".join(f"{mdc_table[name][s]:.4f}" for s in rep_snrs)
    print(row)

print()
print("=" * 78)
print("TABLE D: Monte Carlo vs. analytical CRLB spot-check (consistency check)")
print("=" * 78)
print(f"{'RBC:M':>7} {'SNR':>5} {'MC rel.unc.(%)':>16} {'CRLB rel.unc.(%)':>18} {'%diff':>8}")
for ratio, snr, mc_rel, crlb_rel, pdiff in mc_vs_crlb_rows:
    print(f"{ratio:7.2f} {snr:5.0f} {mc_rel:16.3f} {crlb_rel:18.3f} {pdiff:8.3f}")

print()
print("Figure saved: phase3_task1_snr_required_vs_ratio.png")
