import numpy as np, mc_rbc_barrier_uncertainty as m
np.random.seed(42)
snr=[5,10,20,40,80,160]; nav=[1,4,16,64]
R={k:m.monte_carlo_run(snr,nav,r,n_iter=2000) for k,r in m.SCENARIOS.items()}
def get(k,n,s,key):
    d=R[k]; i=[j for j in range(len(d['snr'])) if d['n_avg'][j]==n and d['snr'][j]==s][0]; return d[key][i]
print("N_avg=1: SNR | bias H, IPF | biasrel% H, IPF | absRMSE H, IPF | IPF/H abs | relRMSE H, IPF | ratio")
for s in snr:
    bh,bi=get('Healthy',1,s,'ratio_bias'),get('IPF',1,s,'ratio_bias')
    ah,ai=get('Healthy',1,s,'ratio_rmse'),get('IPF',1,s,'ratio_rmse')
    rh,ri=get('Healthy',1,s,'ratio_rmse_relative'),get('IPF',1,s,'ratio_rmse_relative')
    print(f"{s:4d} | {bh:+.4f} {bi:+.4f} | {100*bh/.5:+.2f} {100*bi/.18:+.2f} | {ah:.4f} {ai:.4f} | {ai/ah:.2f} | {rh:.1f} {ri:.1f} | {ri/rh:.2f}")
print("bias rel% across Navg at SNR=5:",[ (n,round(100*get('Healthy',n,5,'ratio_bias')/.5,2),round(100*get('IPF',n,5,'ratio_bias')/.18,2)) for n in nav])
print("fold ranges: 0.49/0.21=%.2f 0.55/0.16=%.2f 0.50/0.18=%.2f 0.49/0.16=%.2f 0.55/0.21=%.2f"%(.49/.21,.55/.16,.5/.18,.49/.16,.55/.21))
