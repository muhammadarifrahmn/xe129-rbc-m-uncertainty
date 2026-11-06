import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, mc_rbc_barrier_uncertainty as m
plt.rcParams.update({'font.size':13,'axes.labelsize':14,'axes.titlesize':14,'legend.fontsize':10.5,'xtick.labelsize':12,'ytick.labelsize':12})
rng=np.random.default_rng(7); T=m.T_ARRAY; f=np.fft.fftshift(np.fft.fftfreq(T.size,m.DT))
r=0.5; snr=20
y0=m.simulate_ground_truth_fid(r); sig=(1+r)/snr
y=y0+rng.normal(0,sig,T.size)+1j*rng.normal(0,sig,T.size)
b=m.G_TRUE[:,0]; rb=m.G_TRUE[:,1]*r
sp=lambda x: np.fft.fftshift(np.fft.fft(x)).real
fig,ax=plt.subplots(2,2,figsize=(12,8))
tm=T*1e3
ax[0,0].plot(tm,y.real,color='0.6',lw=.8,label='Noisy FID (real part)'); ax[0,0].plot(tm,y0.real,'k',lw=1.6,label='Noise-free total')
ax[0,0].set(xlim=(0,25),xlabel='Time (ms)',ylabel='Signal (a.u.)',title='(a) Time domain'); ax[0,0].legend()
ax[0,1].plot(tm,np.abs(b),color='#1f77b4',lw=2,label='Barrier: Voigt envelope'); ax[0,1].plot(tm,np.abs(rb),color='#d62728',lw=2,label='RBC: Lorentzian envelope (x0.5)')
ax[0,1].set(xlim=(0,25),xlabel='Time (ms)',ylabel='Envelope (a.u.)',title='(b) Compartment decays'); ax[0,1].legend()
ax[1,0].plot(f,sp(y),color='0.6',lw=.8,label='Noisy spectrum'); ax[1,0].plot(f,sp(y0),'k',lw=1.6,label='Noise-free total')
ax[1,0].set(xlim=(-1500,2500),xlabel='Frequency offset from barrier (Hz)',ylabel='Real part (a.u.)',title='(c) Frequency domain'); ax[1,0].legend()
ax[1,1].plot(f,sp(b),color='#1f77b4',lw=2,label='Barrier (0 Hz)'); ax[1,1].plot(f,sp(rb),color='#d62728',lw=2,label='RBC (~700 Hz)')
ax[1,1].set(xlim=(-1500,2500),xlabel='Frequency offset from barrier (Hz)',ylabel='Real part (a.u.)',title='(d) Simulated resonances'); ax[1,1].legend()
plt.tight_layout(); plt.savefig('fig6_schematic.png',dpi=150); plt.close()
# bias distributions
np.random.seed(3)
fig,axs=plt.subplots(1,2,figsize=(12,5),sharey=False)
for a,(k,rt) in zip(axs,m.SCENARIOS.items()):
    for s,c in ((5,'#d62728'),(10,'#ff7f0e'),(40,'#1f77b4')):
        y0=m.simulate_ground_truth_fid(rt); sg=(1+rt)/s; est=[]
        for _ in range(2000):
            yy=y0+np.random.normal(0,sg,T.size)+1j*np.random.normal(0,sg,T.size); A,B=m.fit_amplitudes(yy); est.append(B/A)
        est=np.array(est)/rt; a.hist(est,bins=np.linspace(0,3,121),histtype='step',lw=2,color=c,label=f'SNR {s} (mean {est.mean():.2f}, n_avg = 1)')
    a.axvline(1,color='k',ls=':'); a.set(xlabel='Estimated / true RBC:M',ylabel='Count (2000 repetitions)',title=f'{k} (true RBC:M = {rt})'); a.legend()
plt.tight_layout(); plt.savefig('fig7_bias.png',dpi=150); plt.close()
