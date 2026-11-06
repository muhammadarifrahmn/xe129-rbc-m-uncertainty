import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, mc_rbc_barrier_uncertainty as m
plt.rcParams.update({'font.size':13,'axes.labelsize':14,'axes.titlesize':14,'legend.fontsize':10.5,'xtick.labelsize':12,'ytick.labelsize':12})
np.random.seed(42)
snr=[5,10,20,40,80,160]; nav=[1,4,16,64]
R={k:m.monte_carlo_run(snr,nav,r,n_iter=2000) for k,r in m.SCENARIOS.items()}
fig,axes=plt.subplots(1,2,figsize=(14,6)); cols=plt.cm.viridis(np.linspace(0,.85,4))
for ax,(k,r),pan in zip(axes,m.SCENARIOS.items(),"ab"):
    d=R[k]
    for c,n in zip(cols,nav):
        ix=[i for i,x in enumerate(d['n_avg']) if x==n]
        ax.plot([d['snr'][i] for i in ix],[d['ratio_rmse'][i] for i in ix],'o-',color=c,label=f'N_avg={n} (MC)')
        ax.plot([d['snr'][i] for i in ix],[d['ratio_std_crlb'][i] for i in ix],'--',color=c,alpha=.6,label=f'N_avg={n} (CRLB)')
    ax.set(xscale='log',yscale='log',xlabel='SNR (single acquisition)',ylabel='Absolute RMSE of RBC:M ratio',title=f'({pan}) {k} scenario (true RBC:M = {r})')
    ax.legend(fontsize=9,ncol=2); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig('fig1_en.png',dpi=150); plt.close()
fig,ax=plt.subplots(figsize=(7.5,5.5))
for k,mk,ls in (("Healthy",'o','-'),("IPF",'s','--')):
    d=R[k]; ix=[i for i,x in enumerate(d['n_avg']) if x==1]
    ax.plot([d['snr'][i] for i in ix],[d['ratio_rmse_relative'][i] for i in ix],marker=mk,ls=ls,lw=2,ms=7,label=f'{k} (true RBC:M = {m.SCENARIOS[k]})')
ax.axhline(15,color='red',alpha=.4,ls=':',label='15% relative-uncertainty target')
ax.set(xscale='log',xlabel='SNR (single acquisition, N_avg = 1)',ylabel='Relative RMSE of RBC:M (%)',title='Relative uncertainty: healthy vs. IPF scenario')
ax.legend(fontsize=8.5); ax.grid(alpha=.3,which='both'); plt.tight_layout(); plt.savefig('fig2_en.png',dpi=150); plt.close()
fig,ax=plt.subplots(figsize=(9,7))
for k,mk in (("Healthy",'o'),("IPF",'s')):
    d=R[k]; ix=[i for i,x in enumerate(d['n_avg']) if x==1]; s=np.array([d['snr'][i] for i in ix]); y=np.array([d['ratio_rmse_relative'][i] for i in ix])
    a,b,r2=m.fit_power_law(s,y); ax.loglog(s,y,marker=mk,ms=8,label=f'Simulation {k}: RMSE ~ SNR^{b:.2f}')
se=np.array([v[0] for v in m.EXTERNAL_DATA.values()]); ne=np.array([v[1] for v in m.EXTERNAL_DATA.values()])
ax.scatter(se,ne,color='k',marker='D',s=70,zorder=5,label='Cohort-mean NMAE (Pilgrim-Morris et al., 2025, Table 1)')
for n,(s_,v) in m.EXTERNAL_DATA.items(): ax.annotate(n,(s_,v),fontsize=9,xytext=(4,4),textcoords='offset points')
a,k,r2=m.fit_power_law(se,ne); sf=np.linspace(se.min(),se.max(),50); ax.loglog(sf,a*sf**k,'k--',alpha=.6,label=f'Cohort-mean refit: NMAE = {a:.1f} x SNR^{k:.2f} (illustrative)')
ax.set(xlabel='SNR (simulation: time-domain |S(0)|/sigma; cohorts: image-domain RBC gridding SNR)',ylabel='Relative uncertainty / NMAE (%)',title='Qualitative comparison (different SNR definitions and error metrics)')
ax.xaxis.label.set_size(11); ax.legend(fontsize=9.5); ax.grid(alpha=.3,which='both'); plt.tight_layout(); plt.savefig('fig3_en.png',dpi=150)
