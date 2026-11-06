import docx, copy, os, re, glob
from docx.shared import Pt, Inches
R1="/mnt/user-data/outputs/R1"; FIG="/home/claude"
def find(d,prefix):
    for p in d.paragraphs:
        if p.text.strip().startswith(prefix): return p
def settext(p,t):
    if not p.runs: p.add_run(t); return
    p.runs[0].text=t
    for r in p.runs[1:]: r.text=""
def sub(p,a,b):
    if p is None or a not in p.text: return False
    for r in p.runs:
        if a in r.text: r.text=r.text.replace(a,b); return True
    settext(p,p.text.replace(a,b)); return True
def clone_after(anchor_el,tmpl,text,parent):
    new=copy.deepcopy(tmpl._p); anchor_el.addnext(new)
    p=docx.text.paragraph.Paragraph(new,parent)
    for r in p.runs[1:]: r.text=""
    (p.runs[0] if p.runs else p.add_run()).text=text
    for e in new.xpath('.//w:drawing'): e.getparent().remove(e)
    return p
def all_paras(d):
    for p in d.paragraphs: yield p
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs: yield p
def superscript(d):
    n=0
    for p in all_paras(d):
        for r in list(p.runs):
            if "129Xe" in r.text and "129" in r.text:
                parts=r.text.split("129Xe")
                base=r._r
                prev=base
                # first segment keeps original run
                r.text=parts[0]
                for seg in parts[1:]:
                    sup=copy.deepcopy(base); prev.addnext(sup); 
                    sr=docx.text.run.Run(sup,p); sr.text="129"; sr.font.superscript=True
                    xe=copy.deepcopy(base); sup.addnext(xe)
                    xr=docx.text.run.Run(xe,p); xr.text="Xe"+seg; xr.font.superscript=False
                    prev=xe; n+=1
    return n
D1=("Beyond its role as a biomarker, the spectroscopically derived RBC:M ratio is a key input to 129Xe gas-exchange imaging: it sets the phase for one-point Dixon decomposition of the dissolved-phase image into RBC and barrier images. An error in the ratio therefore leaks signal between the RBC and membrane images, and the same absolute error causes proportionally greater contamination of the RBC image when RBC signal is low, as in IPF. This further motivates quantifying the precision of the ratio, and the SNR requirements derived here (Section 3.5) apply directly to the calibration spectrum used for Dixon decomposition.")
CRLB=("The CRLB is the smallest variance that any unbiased estimator can attain for a given signal model and noise level. Here it gives the noise-limited floor on the precision of the fitted amplitudes, from which the ratio uncertainty follows by first-order error propagation including the barrier-RBC covariance. It is included as an analytical benchmark rather than as an independent validation: for a linear model with known parameters and Gaussian noise, least squares attains the bound by construction, and the bound strictly applies to unbiased estimators, whereas the magnitude-based ratio is positively biased at low SNR (Table 5).")
PAR22=("The healthy ratio range (0.49-0.55) is consistent with the 3 T multisite reference value of 0.49 +/- 0.11 (Leewiwatwong et al., 2025). The IPF range (0.16-0.21) comes from earlier studies, and because the ratio depends on field strength (Wang et al., 2018) it may differ at 3 T; the continuous sweep in Section 3.5 is therefore intended to cover the plausible range of RBC:M rather than rely on a single IPF value. The Voigt barrier T2* values (T2*L = 2.0 ms, T2*G = 3.0 ms) are representative values chosen to follow the Voigt form recommended by Bier et al. (2019), not a single published measurement; they correspond to a 1/e envelope time of 1.5 ms. The 2025 multisite 3 T study reports global T2* of 0.99 +/- 0.04 ms (membrane) and 1.04 +/- 0.03 ms (RBC) and an RBC chemical shift of 218.2 +/- 0.5 ppm; substituting these values (Lorentzian lineshapes) raised the SNR required for 15% relative uncertainty from 10.6 to 11.8 (healthy) and from 20.8 to 22.3 (IPF), a change of about 10%.")
SNRP=(" To relate the time-domain SNR to conventional per-resonance SNR (noise-free peak height divided by the SD of the noise in the real part of the spectrum), a time-domain SNR of 10 corresponds to about 3.5 (barrier) and 1.6 (RBC) in the healthy scenario and about 4.3 and 0.9 in the IPF scenario; the fit uses all 512 points, which is why the ratio is estimated more precisely than these peak SNRs suggest. Figure 6 shows a simulated FID and spectrum with the added noise.")
MERGED=("Two ground-truth RBC:M scenarios were simulated: healthy (0.50, the midpoint of the 0.49-0.55 range) and IPF (0.18, the midpoint of the 0.16-0.21 range). For each scenario and for each combination of SNR (5, 10, 20, 40, 80, 160) and averaging number (1, 4, 16, 64), 2000 Monte Carlo iterations generated a distribution of estimated RBC:M ratios. Four metrics were computed: bias (mean estimate minus true ratio), which shows whether the estimator is centered on the true value; standard deviation, which measures precision; absolute RMSE, which combines both and is the quantity the CRLB bounds for unbiased estimators; and relative RMSE (RMSE divided by the true ratio, in %), which is used to compare the two scenarios because the question of interest is the size of the error relative to the value being measured. Full numerical results for all tested conditions are provided in the Supplementary Material (not for review).")
def edit(fn,full):
    d=docx.Document(os.path.join(R1,fn)); P=d.paragraphs
    for p in list(all_paras(d)):
        for a,b in [("Spectral SNR","Time-Domain SNR"),("spectral SNR","time-domain SNR"),("sensitive quantitative biomarker of","sensitive biomarker of"),("clinically important quantitative biomarker","clinically important biomarker"),("Figures: 5 | Tables: 7","Figures: 7 | Tables: 7"),
                    ("Voigt: T2*Lorentz~2.0 ms; T2*Gauss~3.0 ms","Representative Voigt values: T2*Lorentz = 2.0 ms; T2*Gauss = 3.0 ms (1/e time 1.5 ms)"),("Bier et al. (2019)","Bier et al. (2019) for the Voigt form") if False else ("",""),]:
            if a and a in p.text: sub(p,a,b)
    if not full and fn.startswith("01"):
        pass
    # intro Dixon paragraph
    pi=find(d,"The RBC:M signal ratio has emerged")
    if pi and not find(d,"Beyond its role as a biomarker"): clone_after(pi._p,pi,D1,pi._parent)
    # 2.2 parameter paragraph
    p21=find(d,"Table 1 summarizes the ground-truth")
    if p21 and not find(d,"The healthy ratio range (0.49-0.55) is consistent"): clone_after(p21._p,p21,PAR22,p21._parent)
    # 2.4 SNR paragraph
    p24=find(d,"Complex Gaussian noise was added")
    if p24 and "Figure 6 shows" not in p24.text: sub(p24,"on |S(0)|, the sum of the barrier and RBC amplitudes, and held fixed across scenarios, so the IPF scenario corresponds to constant total signal with a lower RBC fraction.","on |S(0)|, the sum of the barrier and RBC amplitudes, and held fixed across scenarios, so the IPF scenario corresponds to constant total signal with a lower RBC fraction."+SNRP)
    # CRLB paragraph after the CRLB section paragraph
    pc=find(d,"providing the theoretical lower bound")
    if pc and not find(d,"The CRLB is the smallest variance"): clone_after(pc._p,pc,CRLB,pc._parent)
    # merge 2.6/2.7
    h6=find(d,"2.6 Monte Carlo Simulation"); h7=find(d,"2.7 Clinical Scenarios")
    if h6 and h7:
        settext(h6,"2.6 Ground-Truth Scenarios and Monte Carlo Procedure")
        b6=find(d,"For each combination of SNR"); b7=find(d,"Simulations were repeated for two")
        settext(b6,MERGED)
        for x in (h7,b7):
            if x is not None: x._p.getparent().remove(x._p)
        for old,new in (("2.8 Qualitative","2.7 Qualitative"),("2.9 Computational","2.8 Computational"),("2.10 Additional","2.9 Additional")):
            q=find(d,old); 
            if q: settext(q,q.text.replace(old[:4],new[:4],1))
    # bias paragraph figure 7 mention + Dixon discussion + metrics
    pb=find(d,"The ratio estimator was positively biased")
    if pb and "Figure 7" not in pb.text: sub(pb,"(Table 5):","(Table 5; Figure 7 shows the distributions of the estimates):")
    pdx=find(d,"The continuous sweep (Section 3.5) translates")
    if pdx and "Dixon" not in pdx.text: pdx.runs[-1].text+=" The same SNR requirements apply to the calibration spectrum used to set the Dixon phase for gas-exchange imaging, where a biased or imprecise ratio leaks signal between RBC and membrane images and matters most at low RBC:M."
    # figures
    if full:
        swapmap={0:"fig1_en.png",1:"fig2_en.png",2:"fig3_en.png"}
        for pos,f in swapmap.items():
            rid=d.inline_shapes[pos]._inline.graphic.graphicData.pic.blipFill.blip.embed; d.part.related_parts[rid]._blob=open(f"{FIG}/{f}","rb").read()
        cap_t=find(d,"Figure 1. Absolute RMSE")
        # Figure 6 after 2.4 body
        p24=find(d,"Complex Gaussian noise was added")
        c6=clone_after(p24._p,cap_t,"Figure 6. Simulated FID and spectrum (healthy scenario, time-domain SNR = 20): (a) noisy and noise-free FID; (b) barrier (Voigt) and RBC (Lorentzian) envelopes; (c) real part of the noisy and noise-free spectrum; (d) the two simulated resonances separately. The barrier is at 0 Hz and the RBC at about 700 Hz.",p24._parent)
        d.add_picture(f"{FIG}/fig6_schematic.png",width=Inches(5.8)); pic=d.paragraphs[-1]; pic.alignment=1; p24._p.addnext(pic._p)
        # Figure 7 after Table 5
        cap5=find(d,"Table 5. Bias and absolute")
        tb=cap5._p.getnext()
        c7=clone_after(tb,cap_t,"Figure 7. Distributions of the estimated RBC:M ratio relative to the true value (2000 repetitions, N_avg = 1) at time-domain SNR 5, 10 and 40 for the healthy and IPF scenarios; the dotted line marks the true value.",cap5._parent)
        d.add_picture(f"{FIG}/fig7_bias.png",width=Inches(5.8)); pic2=d.paragraphs[-1]; pic2.alignment=1; tb.addnext(pic2._p)
    d.save(os.path.join(R1,fn)); print(fn,"edited")
edit("00_Manuscript_FULL_Combined.docx",True); edit("01_Main_Manuscript.docx",False)
# 02 figures
d=docx.Document(os.path.join(R1,"02_Figures.docx"))
for pos,f in {0:"fig1_en.png",1:"fig2_en.png",2:"fig3_en.png"}.items():
    rid=d.inline_shapes[pos]._inline.graphic.graphicData.pic.blipFill.blip.embed; d.part.related_parts[rid]._blob=open(f"{FIG}/{f}","rb").read()
caps=[p for p in d.paragraphs if p.text.startswith("Figure 5.")][0]; last=caps
for path,cap in (("fig6_schematic.png","Figure 6. Simulated FID and spectrum (healthy scenario, time-domain SNR = 20): (a) noisy and noise-free FID; (b) barrier (Voigt) and RBC (Lorentzian) envelopes; (c) real part of the noisy and noise-free spectrum; (d) the two simulated resonances separately."),("fig7_bias.png","Figure 7. Distributions of the estimated RBC:M ratio relative to the true value (2000 repetitions, N_avg = 1) at time-domain SNR 5, 10 and 40 for the healthy and IPF scenarios; the dotted line marks the true value.")):
    d.add_picture(f"{FIG}/{path}",width=Inches(5.8)); pic=d.paragraphs[-1]; pic.alignment=1
    nc=copy.deepcopy(caps._p); last._p.addnext(pic._p); pic._p.addnext(nc)
    cp=docx.text.paragraph.Paragraph(nc,last._parent); settext(cp,cap); last=cp
d.save(os.path.join(R1,"02_Figures.docx"))
# 04 GA image, then superscript + title in all
d=docx.Document(os.path.join(R1,"04_Supplementary_Material_for_Review_Graphical_Abstract.docx"))
rid=d.inline_shapes[0]._inline.graphic.graphicData.pic.blipFill.blip.embed; d.part.related_parts[rid]._blob=open(f"{FIG}/fig2_en.png","rb").read(); d.save(os.path.join(R1,"04_Supplementary_Material_for_Review_Graphical_Abstract.docx"))
for f in sorted(glob.glob(R1+"/0[0-7]_*.docx")):
    d=docx.Document(f)
    for p in all_paras(d):
        for a,b in (("Spectral SNR","Time-Domain SNR"),("spectral SNR","time-domain SNR")):
            if a in p.text: sub(p,a,b)
    n=superscript(d); d.save(f); print(os.path.basename(f),"superscript",n)
