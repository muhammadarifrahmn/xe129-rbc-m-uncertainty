import docx
from docx.shared import Pt, RGBColor
d=docx.Document()
st=d.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(11)
def H(t,l=1): d.add_heading(t,level=l)
def para(t,b=False,i=False,color=None):
    p=d.add_paragraph(); r=p.add_run(t); r.bold=b; r.italic=i
    if color: r.font.color.rgb=RGBColor(*color)
    return p
def item(comment,resp,chg):
    p=d.add_paragraph(); r=p.add_run("Comment: "); r.bold=True; r2=p.add_run(comment); r2.italic=True
    p=d.add_paragraph(); r=p.add_run("Response: "); r.bold=True; p.add_run(resp)
    p=d.add_paragraph(); r=p.add_run("Changes: "); r.bold=True; p.add_run(chg)
    d.add_paragraph()
d.add_heading("Response to Reviewers",0)
para("Manuscript ID: 7081852",b=True)
para("Monte Carlo Uncertainty Quantification of the RBC:M Ratio in Hyperpolarized 129Xe Gas-Exchange MRI: Effects of Time-Domain SNR and Acquisition Averaging")
para("Dear Editor and Reviewers,")
para("Thank you for the detailed and constructive reports. They led to substantial changes: the main conclusion is now framed as a noise-limited lower bound under idealized conditions, the claim of a shared SNR threshold and the 'external validation' framing have been removed, and three new analyses were added (continuous RBC:M sweep with minimum SNR and detectable change; physiological-variability bands; nonlinear free-parameter fitting with model misspecification). Section numbers below refer to the revised manuscript; reviewer comments are abbreviated.")
para("Summary of the main changes",b=True)
for t in ["New Sections 3.5-3.7 and 2.9: SNR required for 15%, 10% and 5% relative uncertainty over RBC:M 0.10-0.60 (Figure 4, Table 6), minimum detectable change, uncertainty bands from T2* and chemical-shift variation (Figure 5), and nonlinear/misspecified fits (Table 7).",
 "Bias and absolute RMSE are now reported (Table 5, Figure 7); the 'comparable absolute RMSE' statement is corrected (IPF is about 30% lower).",
 "The comparison with Pilgrim-Morris et al. (2025) is now explicitly qualitative; the shared-threshold claim is removed throughout.",
 "Terminology (RBC:M; time-domain SNR), FDA statement, references, placeholders, code-availability wording, figure legibility and 129Xe formatting are corrected. A schematic spectrum (Figure 6) and a CRLB explanation were added."]: d.add_paragraph(t,style='List Bullet')
H("Reviewer 1",1)
H("Major comments",2)
item("1. Fixed spectral parameters; sensitivity to T2*/linewidth and chemical-shift variation, report bands; state how IPF amplitudes were set.",
 "We agree that results depend on the design matrix. We propagated the inter-subject spreads of T2* (RBC 4.0%, barrier 3.2-3.5%) and of the RBC-barrier chemical shift (SD 0.89 ppm healthy, 0.76 ppm IPF) reported by Kammerman et al. (2020; 8 healthy, 16 IPF subjects, 1.5 T) through the analytical bound by sampling (2000 draws). The resulting 5-95% bands are narrow (at SNR of approximately 21: 7.7% [7.5-7.9%] healthy and 15.1% [14.7-15.6%] IPF). Shifting the IPF mean T2* by the healthy-to-IPF difference reported by Kammerman et al. changes the relative uncertainty by only -2.7%. The healthy-IPF difference therefore reflects the RBC:M ratio in this model. We also tested the 3 T multisite T2* values (membrane 0.99 ms, RBC 1.04 ms; Leewiwatwong et al., 2025): the SNR needed for 15% uncertainty rises from 10.6 to 11.8 (healthy) and 20.8 to 22.3 (IPF). Amplitudes: SNR is defined on |S(0)|, the sum of the compartment amplitudes, and held fixed across scenarios, i.e. constant total signal with a lower RBC fraction; this is now stated in Section 2.4. We also used the spreads reported by Robertson et al. (2017; 12 healthy and 12 IPF subjects, 1.5 T; RBC linewidth CV 5-7%, barrier linewidth CV 7-8%, RBC-barrier shift SD 0.6-0.9 ppm); the bands were similarly narrow (healthy 7.7%, 5-95% range 7.3-8.1%; IPF 15.1%, 14.5-15.8%). Robertson et al. also show that a third dissolved-phase resonance changes the fitted ratio (healthy 0.44 +/- 0.07 with three peaks); our two-compartment model does not include it, and this is now listed as a limitation.",
 "Sections 2.2, 2.4, 2.9, 3.6, 4.1, Figure 5; Kammerman et al. (2020) and Robertson et al. (2017) are now cited.")
item("2. Parameters are estimated in practice; MC/CRLB agreement is expected by construction; what does MC add? Add a nonlinear, gas-phase and/or misspecified scenario.",
 "We agree that the agreement is expected for a linear estimator under Gaussian noise and now say so (Section 2.5, Discussion). We added nonlinear least-squares fits with free amplitudes, frequencies, phases and all T2* components (2000 repetitions), and a misspecified Lorentzian-barrier fit to Voigt-generated data. Free fitting raised the relative RMSE 2.5-3-fold at SNR 20-40 (e.g. healthy SNR 20: 22.4% vs 8.3% linear; IPF 48.1% vs 15.9%). The Lorentzian-barrier fit produced a negative bias of about 21-23% (healthy) and 32-40% (IPF) that does not decrease with SNR. At SNR 10, 33% (healthy) and 45% (IPF) of free fits ended on parameter bounds, so we do not report these as reliable. The gas-phase peak is not modeled and is listed as a limitation.",
 "Sections 3.7 and 2.9, Table 7, Discussion, Limitations.")
item("3. Provide acquisition guidance as a function of RBC:M (0.1-0.6), target levels justified, foreground in Abstract/Conclusions as minimum requirements; add minimum detectable change.",
 "Done. For RBC:M 0.10 to 0.60, the single-acquisition SNR for 15%, 10% and 5% relative uncertainty is 34, 51 and 103 at 0.10; 21, 31 and 62 at 0.18; and 11, 16 and 32 at 0.50 (Table 6, Figure 4). Published imaging-based repeatability of the RBC:M ratio is a CV of 11.5% between visits about one month apart (Hahn et al., 2019; 13 healthy volunteers, 1.5 T) and 7.2% within a session (Garrison et al., 2023). A 15% target is therefore similar to or somewhat above between-visit repeatability, 10% is comparable to it, and 5% is below even within-session repeatability. The ranges of 11-20% and 7-13% cited in the report span several metrics (RBC:gas, barrier:gas and RBC:barrier), not the ratio alone, so we cite the ratio-specific values. At SNR 20 the 95% minimum detectable change is about 0.11 (healthy) and 0.08 (IPF). All values are presented as minimum requirements under idealized conditions in the Abstract, Results, Discussion and Conclusions. The illustrative 15% line in Figure 2 is now labelled as a justified target.",
 "Abstract, Sections 3.5, Discussion, Conclusions; Figures 2 and 4; Table 6.")
item("4. The claimed shared SNR threshold of 5 is not supported (direction, SNR definitions, NMAE metric, refit exponent); consider comparing with repeatability.",
 "We agree and removed the claim everywhere. The text now states that, in the published data, NMAE rose sharply and exceeded 15% when the gridding RBC SNR fell below about 5 (that is, below, not above, an SNR of 5), that the SNR definitions (image-domain RBC gridding SNR vs. time-domain |S(0)|/sigma) and error metrics differ, and that the authors describe the overall relationship as a power law. We did not have access to the fitted parameters in their Figure S2, so we no longer quote an exponent; our cohort-mean refit is shown for illustration only. The comparison is presented as qualitative. Simulated noise-limited uncertainty is related to published repeatability in Section 3.5.",
 "Abstract, Sections 2.7, 3.4, Discussion, Conclusions, Figure 3 and graphical abstract.")
H("Specific comments",2)
rows=[
("1. FDA statement and citation.","Revised to state FDA approval in December 2022 for lung ventilation evaluation, and that gas-exchange imaging is not part of that indication. The citation was replaced (Polarean press release; Niedbalski et al. 2021 retained for consortium protocols).","Introduction; references."),
("2. Role of the ratio in Dixon decomposition; implications for calibration-spectrum SNR.","Added. The ratio sets the Dixon phase, errors leak signal between RBC and membrane images, proportionally more at low RBC signal, and the SNR requirements of Section 3.5 apply to the calibration spectrum.","Introduction; Discussion."),
("3. '3.3-fold' reduction.","Kaushik et al. (2014) themselves report a 3.3-fold difference between group means (0.55 vs. 0.16). With the corrected ranges (healthy 0.49-0.55; IPF 0.16-0.23) the fold difference is 2.1-3.4 depending on endpoints; the simulated reference values (0.50 and 0.18) differ by a factor of 2.8. The text now says so.","Introduction; Section 3.2."),
("4. Field strength of Kaushik et al.; source of Voigt T2*; recent multisite values.","The healthy range is consistent with the 3 T multisite reference (0.49 +/- 0.11; Leewiwatwong et al., 2025). The IPF values come from 1.5 T studies (Kaushik et al., 2014, confirmed 1.5 T: 0.16 +/- 0.03; Robertson et al., 2017: 0.23 +/- 0.07; Hahn et al., 2022: 0.23 +/- 0.07) and the IPF range is now stated as 0.16-0.23 (the earlier upper value of 0.21 was not supported by whole-lung data). The ratio may differ at 3 T because it is field dependent (Wang et al., 2018), which the continuous sweep addresses (Table 6 now includes RBC:M = 0.23: 17.2, 25.9 and 51.7 for 15%, 10% and 5%). Reported values also depend on the method (healthy 0.38 with one-point Dixon imaging, 0.44 with three-peak fitting). The Voigt T2* values are representative values (1/e time 1.5 ms), not a single published measurement; this is now stated. The 2025 3 T T2* and chemical-shift values were tested (see Major 1).","Section 2.2; Table 1; references."),
("5. Sampling parameters; TR 15 ms.","The simulation used 512 points at a 125 us dwell (8 kHz), not the 32 us dwell listed for the reference protocol; this discrepancy was ours and is now stated in Section 2.3 and Table 1. A 32 us dwell would roughly halve the uncertainty at the same per-point SNR (healthy SNR 10: 8.2% vs 15.9%). The consortium TR of 15 ms is acknowledged; TR does not enter this noise-only model.","Section 2.3; Table 1."),
("6. Consistent SNR terminology; report frequency-domain SNR.","'Spectral SNR' was replaced by 'time-domain SNR' (including the title). At time-domain SNR 10 the per-resonance frequency-domain SNR (peak height / noise SD) is about 3.5 (barrier) and 1.6 (RBC) in the healthy scenario and 4.3 and 0.9 in the IPF scenario.","Title; Section 2.4."),
("7. Averaging within a breath-hold is not equivalent to independent averaging.","Added to Section 2.4 and the Limitations (cardiac oscillation and magnetization depletion).","Sections 2.4, 4.1."),
("8. Magnitude-based ratio bias; report bias; CRLB applies to unbiased estimators.","Bias is reported (Table 5, Figure 7): at SNR 5, +6.6% (healthy) and +24.5% (IPF), below 2% and 7% at SNR 10. The CRLB statement was added.","Sections 2.5, 3.2."),
("9. Quantify absolute RMSE.","IPF absolute RMSE is 0.67-0.71 of healthy at every SNR; the text was corrected.","Section 3.2; Table 5."),
("10. 'Triple jeopardy'.","Removed and replaced by a plain description.","Section 3.4."),
("11. Rician noise limitation.","Replaced by the magnitude-based ratio bias limitation.","Section 4.1."),
("12. Code availability.","The wording now states that the code will be deposited in a public repository. [AUTHOR: insert Zenodo/GitHub DOI before resubmission.]","Data Availability."),
("13. Incomplete references; Kammerman not cited.","Bier, Taylor and Larson were completed. The Radiology paper previously attributed to 'Rankine et al. (2021)' is Hahn et al. (2022), Radiology 305(3):688-696, and was corrected; Hahn et al. (2019), Garrison et al. (2023), Robertson et al. (2017) and Leewiwatwong et al. (2025) were added. Kammerman et al. is now cited.","References; Sections 2.9, 3.6."),
("14. Graphical abstract placeholder.","Removed; the abstract text was updated to the revised findings.","Graphical abstract file."),
("15. Figure legibility; superscript 129Xe.","Figures 1-3 were regenerated with larger text; 129Xe is superscripted throughout.","Figures; whole text."),
("16. Representative spectrum.","Added Figure 6 (FID, envelopes, spectrum and resonances, with added noise).","Section 2.4; Figure 6."),
("17. RBC:M terminology.","Changed throughout.","Whole manuscript.")]
for c,r,ch in rows: item(c,r,ch)
H("Reviewer 2",1)
rows2=[
("External validation (Section 2.8): the power-law fit to simulations is not validation; exponents differ.","Agreed. Section 2.7 now describes the power-law fit as a description of the simulation output and the comparison with Pilgrim-Morris et al. as qualitative; the text no longer uses 'validation'.","Sections 2.7, 3.4, Discussion, Abstract."),
("Agreement with empirical data (Figure 3): SNR ranges do not overlap; points not between curves.","Agreed. The claim was removed; Figure 3 is presented as a qualitative consistency check and its caption states that the SNR definitions and metrics differ. Lower-RBC:M cohorts show lower SNR and higher NMAE, the same direction as in the simulation.","Section 3.4; Figure 3."),
("SNR = 5: unclear origin of the threshold.","The threshold came from the source paper's description and is not supported by our analysis; it was removed (see Reviewer 1, Major 4).","Whole manuscript."),
("Nomenclature: membrane.","RBC:M used throughout.","Whole manuscript."),
("RBC/M should not be called quantitative.","'Quantitative' was removed from the descriptions of the ratio.","Abstract; Introduction."),
("Simulation figure with noise, time and frequency domains.","Added Figure 6.","Section 2.4."),
("Justify metrics.","A justification of bias, SD, absolute RMSE and relative RMSE, and of the use of relative RMSE to compare scenarios, was added.","Section 2.6."),
("Report bias, e.g. a distribution plot.","Bias is reported in Table 5 and the distributions of the estimates are shown in Figure 7.","Section 3.2."),
("Explain the CRLB.","A short explanatory paragraph was added.","Section 2.5."),
("Merge Sections 2.6 and 2.7.","Merged into Section 2.6, which first defines the healthy and IPF ground-truth ratios and then the Monte Carlo procedure and metrics.","Section 2.6.")]
for c,r,ch in rows2: item(c,r,ch)
para("Sincerely,")
para("Muhammad Arif Rahman")
d.save("/mnt/user-data/outputs/R1/08_Response_to_Reviewers.docx")
