import docx, copy, os
R1="/mnt/user-data/outputs/R1"
def allp(d):
    for p in d.paragraphs: yield p
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs: yield p
def settext(p,t):
    p.runs[0].text=t
    for r in p.runs[1:]: r.text=""
def rep(d,a,b):
    n=0
    for p in allp(d):
        if a in p.text:
            done=False
            for r in p.runs:
                if a in r.text: r.text=r.text.replace(a,b); done=True; break
            if not done: settext(p,p.text.replace(a,b))
            n+=1
    return n
REPL=[
("0.16-0.21, a reduction of roughly 2.3- to 3.4-fold depending on which range endpoints are compared","0.16-0.23, a reduction of roughly 2.1- to 3.4-fold depending on which range endpoints are compared (Kaushik et al. reported 0.55 versus 0.16 between group means, i.e. 3.3-fold)"),
("(Kaushik et al., 2014; Hahn et al., 2022)","(Kaushik et al., 2014; Robertson et al., 2017; Hahn et al., 2022)"),
("The IPF range (0.16-0.21) comes from earlier studies, and because","The IPF range (0.16-0.23) comes from earlier 1.5 T studies (Kaushik et al., 2014; Robertson et al., 2017; Hahn et al., 2022), and because"),
("(0.18, the midpoint of the 0.16-0.21 range)","(0.18, a representative value within the 0.16-0.23 range)"),
("is 2.3-3.4 times the IPF range (0.16-0.21)","is 2.1-3.4 times the IPF range (0.16-0.23)"),
("0.16 +/- 0.03 to 0.21 +/- 0.07","0.16 +/- 0.03 to 0.23 +/- 0.07"),
("The published subject-level data follow a continuous power law (NMAE = 61.5 x SNR^-0.85; Pilgrim-Morris et al., 2025, Figure S2A) with no threshold or inflection; our cohort-mean refit is shown for illustration only and differs from it. The shallower empirical exponent is consistent with additional reconstruction error sources absent from the noise-limited simulation.",
 "Pilgrim-Morris et al. (2025) report that NMAE increased sharply when the gridding RBC SNR fell below about 5, with RBC:M errors above 15% below that SNR, and describe the overall relationship as a power law (NMAE = a x SNR^k; fitted parameters in their Figure S2); our refit to cohort means is shown for illustration only and is not a reproduction of their subject-level fit."),
("within the ranges reported at 1.5 T.","within the ranges reported at 1.5 T. Using the larger spreads of Robertson et al. (2017; 12 healthy and 12 IPF subjects, 1.5 T; RBC linewidth CV 5-7%, barrier linewidth CV 7-8%, RBC-barrier shift SD 0.6-0.9 ppm) gave similarly narrow bands (healthy: 7.7%, 5-95% range 7.3-8.1%; IPF: 15.1%, 14.5-15.8%)."),
("(Kammerman et al., 2020, 1.5 T),","(Kammerman et al., 2020, 1.5 T) and, as a second source, from whole-lung spectroscopy in 12 healthy and 12 IPF subjects (Robertson et al., 2017, 1.5 T),"),
("Finally, the gas-phase compartment","Sixth, a third dissolved-phase resonance described by Robertson et al. (2017), whose inclusion changes the fitted RBC:M ratio, is not modeled. Finally, the gas-phase compartment"),
(" The 2025 multisite 3 T study reports global T2*"," Reported ratio values also depend on the method: healthy values are 0.38 +/- 0.11 with one-point Dixon imaging (Hahn et al., 2022) and 0.44 +/- 0.07 with three-peak spectral fitting (Robertson et al., 2017), and the three-peak fit lowers the healthy ratio while changing the IPF ratio little; our two-compartment model does not include this third resonance. The 2025 multisite 3 T study reports global T2*"),
]
REF="Robertson, S. H., Virgincar, R. S., Bier, E. A., He, M., Schrank, G. M., Smigla, R. M., Rackley, C., McAdams, H. P., & Driehuys, B. (2017). Uncovering a third dissolved-phase 129Xe resonance in the human lung: Quantifying spectroscopic features in healthy subjects and patients with idiopathic pulmonary fibrosis. Magnetic Resonance in Medicine, 78(4), 1306-1315. https://doi.org/10.1002/mrm.26533"
def addrow(d):
    for t in d.tables:
        if t.cell(0,0).text.strip()=="RBC:M" and "SNR for 15%" in t.cell(0,1).text:
            for i,r in enumerate(t.rows):
                if r.cells[0].text.startswith("0.18"):
                    new=copy.deepcopy(r._tr); r._tr.addnext(new)
                    row=docx.table._Row(new,t)
                    for c,v in zip(row.cells,["0.23 (IPF, Hahn et al., 2022)","17.2","25.9","51.7"]):
                        p=c.paragraphs[0]; settext(p,v)
                    return 1
    return 0
for fn in ("00_Manuscript_FULL_Combined.docx","01_Main_Manuscript.docx","03_Tables.docx"):
    d=docx.Document(os.path.join(R1,fn)); log=[]
    for a,b in REPL: log.append(rep(d,a,b))
    log.append(addrow(d))
    if fn!="03_Tables.docx":
        tay=[p for p in d.paragraphs if p.text.startswith("Taylor, Y.")]
        if tay and not any(p.text.startswith("Robertson, S. H.") for p in d.paragraphs):
            new=copy.deepcopy(tay[0]._p); tay[0]._p.addprevious(new); p=docx.text.paragraph.Paragraph(new,tay[0]._parent)
            for r in p.runs[1:]: r.text=""
            r0=p.runs[0]; i=REF.find("129Xe"); r0.text=REF[:i]
            s=copy.deepcopy(r0._r); r0._r.addnext(s); sr=docx.text.run.Run(s,p); sr.text="129"; sr.font.superscript=True
            rest=copy.deepcopy(r0._r); s.addnext(rest); rr=docx.text.run.Run(rest,p); rr.text=REF[i+3:]; rr.font.superscript=False
    d.save(os.path.join(R1,fn)); print(fn,log)
