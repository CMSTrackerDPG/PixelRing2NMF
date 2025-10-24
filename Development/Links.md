# NMF development (June-July 2025)

## Acronyms

- **CMS**: Compact Muon Solenoid
- **DQM**: Data Quality Monitoring
- **TkDQM**: Tracker DQM
- **ML**: Machine Learning
- **AE**: Auto-Encoder
- **NMF**: Non-Negative Matrix Factorization (NNMF or NMF)

## Links

- **GitHub**: [NMF on GitHub project](https://github.com/LukaLambrecht/pixelae/tree/main)
- **SWAN**: [CERN Jupiter notebooks](https://swan-k8s.cern.ch/)
- **DIALS**: [GUI for LS plots](https://cmsdials.web.cern.ch/lumisections?ws=tracker)
- **OMS**: [Run report (run 382960)](https://cmsoms.cern.ch/cms/runs/report?cms_run=382960)
- **RunRegistry**: [Collision runs 2025](https://cmsrunregistry.web.cern.ch/offline/datasets/tracker?ofbf%5Brules%5D%5B0%5D%5Bfield%5D=rr_attributes.class&ofbf%5Brules%5D%5B0%5D%5Bvalue%5D=Collisions25&ofbf%5Brules%5D%5B0%5D%5Boperator%5D=%3D&ofbf%5Brules%5D%5B1%5D%5Bfield%5D=name&ofbf%5Brules%5D%5B1%5D%5Bvalue%5D=%2FExpress%2FCollisions2025%2FDQM&ofbf%5Brules%5D%5B1%5D%5Boperator%5D=%3D&ofbf%5Bcombinator%5D=and&ofbf%5Bnot%5D=true&oftf%5Brules%5D%5B0%5D%5Bfield%5D=run_number&oftf%5Brules%5D%5B0%5D%5Bvalue%5D=374522&oftf%5Brules%5D%5B0%5D%5Boperator%5D=%3D&oftf%5Bcombinator%5D=and&oftf%5Bnot%5D=true)
- **CertHelper**: [Certification Helper tool](https://certhelper.web.cern.ch/)

## CMS Tracker and anomalies

- (Pixel Ph1 Paper) [The CMS Phase-1 Pixel Detector Upgrade](https://cds.cern.ch/record/2748381/files/2012.14304.pdf)
- (TkDQM Docs) [Introduction to the CMS Tracking system](https://tkdqm.docs.cern.ch/CMS_Tracker/)
- (TkDQM Docs) [Description of Pixel Short Anomalies](https://tkdqm.docs.cern.ch/PixelShortAnomalies/)
- (TkDQM Docs) [Tool to find Pixel Short Anomalies](https://tkdqm.docs.cern.ch/Tools_PixelShortAnomalies/)
- (Table) [List of anomalies in 2022-23-24-25 data](https://cernbox.cern.ch/s/0fAyFnPvo0V5WXc)
- (Images 2022-24) [Folder with .png of anomalies in 2022-23-24 data](https://tkmaps.web.cern.ch/tkmaps/files/data/users/event_display/pixeLScanner/images/)
- (Images 2025) [Folder with .png of anomalies in 2025 data](https://tkmaps.web.cern.ch/tkmaps/files/data/users/event_display/PixelShortAnomalies/)

## DQM & ML in TkDQM (Tracker)

- (Proc DQM 2018) [The Data Quality Monitoring Software for the CMS experiment at the LHC: past, present and future](https://cds.cern.ch/record/2798183/files/CR2018_228.pdf)
- (Talk DQM LHCP 2025) [Performance highlights from CMS](https://indico.cern.ch/event/1419878/contributions/6445242/attachments/3061002/5412847/CMS_performance_highlights.pdf)
- (DP note TkDQM 2024) [CMS tracker data quality certification with new machine learning tools](https://cds.cern.ch/record/2905834/files/DP2024_070.pdf?version=2)
- (Talk ICHEP 2024) [Tracker Data Quality certification in CMS with new Machine Learning tools](https://indico.cern.ch/event/1291157/contributions/5892372/attachments/2900636/5086600/AP_CMS_TrackerML_Talk_ICHEP_2024_Final.pdf)
- (DP note AE ML 2025) [Anomaly detection for the CMS Pixel Barrel Data Quality with Machine Learning models](https://cds.cern.ch/record/2936313/files/DP2025_030.pdf)


## Talks: Anomalies in Tracker DQM

- (Tracker Week **Nov24**) [Pixel Short Anomalies: part 1](https://indico.cern.ch/event/1455268/contributions/6219127/attachments/2965595/5217442/one-minute-anomalies_2024-runs_Nov24.pdf)
- (PPD Workshop **Nov24**) [Pixel Short Anomalies: part 2.1](https://indico.cern.ch/event/1468895/contributions/6240491/attachments/2973843/5234340/one-minute-anomalies_2024_runs_Nov24-5.pdf)
- (Run Coordination **Jan25**) [Pixel Short Anomalies: part 2.2](https://indico.cern.ch/event/1491578/contributions/6308026/attachments/2999877/5286152/Short-anomalies_Jan25.pdf)
- (TkDQM **May25**) [1 year of Pixel Short Anomalies: Summary](https://indico.cern.ch/event/1505995/contributions/6510562/attachments/3064597/5420427/1-year_of_Short-anomalies_May25.pdf)

## NMF model for TkDQM anomalies

- (NMF Barrel - Part 1 - ML4DQM May 2025) [NMF model of cluster occupancy (Pixel Barrel) 2024 data](https://indico.cern.ch/event/1544743/contributions/6502133/attachments/3062946/5416734/ml4dqm_20250507.pdf)
- (NMF Barrel - Part 2 - TkDQM May 2025) [NMF model of cluster occupancy (Pixel Barrel) 2024 data](https://indico.cern.ch/event/1505987/contributions/6544621/attachments/3077834/5447569/ml4dqm_20250530.pdf)
- (NMF Barrel - Part 3 - TkDQM Jun 2025) [NMF model of cluster occupancy (Pixel Barrel) 2024 data](https://indico.cern.ch/event/1505997/contributions/6556508/attachments/3082636/5456721/ml4dqm_20250606.pdf)
- (NMF Barrel - Part 5 - LPC Jun 2025) [NMF model of cluster occupancy (Pixel Barrel) 2024 data](https://indico.cern.ch/event/1562882/contributions/6583653/attachments/3093189/5479030/ml4dqm_20250625.pdf)
- (NMF Barrel - Part 6 - ML Jul 2025) [NMF model of cluster occupancy (Pixel Barrel) 2024 data](https://indico.cern.ch/event/1566310/contributions/6597695/attachments/3109399/5511510/ml4dqm_20250723_v2.pdf)
- (NMF Endcap - Part 1 - TkDQM Jul 2025) [NMF model of cluster occupancy (Pixel Endcap Ring 1) 2024 data](https://indico.cern.ch/event/1567982/contributions/6606056/attachments/3102761/5498107/Model%20Summary%20Presentation.pdf)
- (NMF Endcap - Part 2 - TkDQM Aug 2025) [NMF model of cluster occupancy (Pixel Endcap Ring 1) 2025 data](https://indico.cern.ch/event/1567133/contributions/6614560/attachments/3113631/5519907/2025%20Summary%20Presentation.pdf)
- (NMF Endcap - Part 3 - TkDQM Sep 2025) [NMF model of cluster occupancy (Pixel Endcap Ring 2) 2024-25 data](https://indico.cern.ch/event/1567989/contributions/6712686/attachments/3143300/5580749/Ale-Jake_NMF_3_Sep25.pdf)

# Extra stuff...

## DIALS platform

- (DIALS overview) [DIALS Overview for Users](https://docs.google.com/presentation/d/1d3-_dLzAnZOzBBNIpRzfVkPlI4HwlnRgQW-r-reWs6o)
- (DIALS examples) [A practical guide to DIALS](https://indico.cern.ch/event/1423761/contributions/5988068/attachments/2881798/5049075/cmsdials_for_users_20240620.pdf)
- (DIALS & TkDQM 2024) [DIALS for ML model building](https://indico.cern.ch/event/1468895/contributions/6240475/attachments/2973776/5234196/DIALS%20PPD%20Workshop%2025%20Nov%202024.pdf)
- (Model deployment on DIALS)  [Pixel Barrel NMF deployment](https://indico.cern.ch/event/1593463/contributions/6717314/attachments/3145087/5583320/ml4dqm_20250930.pdf)

## DQM & ML in TkDQM (2021-22)

- (Talk CHEP 2022) [Machine Learning Tools for the CMS
Tracker Data Quality Monitoring and Certification](https://indico.jlab.org/event/459/contributions/11416/attachments/9584/13910/CMS_TRKDQMML_CHEP23_GBenelli_v2.pdf)
- (DP note 2021) [Tracker DQM Machine Learning
studies for data certification](https://cds.cern.ch/record/2799472/files/DP2021_034.pdf)
- (DP note 2022) [Prospects for computer-assisted data quality monitoring at the CMS pixel detector](https://cds.cern.ch/record/2812026/files/DP2022_013.pdf)

## ML in DQM (Other detectors)

- (Talks at PPDive) [Several talks: ECAL, HCAL, Tracker, JetMET](https://indico.cern.ch/event/1334075/)
- (DP note JetMET) [Machine Learning Techniques for JetMET Data Certification of the CMS Detector](https://cds.cern.ch/record/2860924/files/DP2023_032.pdf)
- (Paper ECAL) [Autoencoder-Based Anomaly Detection System for Online Data Quality Monitoring of the CMS Electromagnetic Calorimeter](https://link.springer.com/article/10.1007/s41781-024-00118-z)
- (Paper HCAL) [Anomaly Detection with Graph Networks for Data Quality Monitoring of the Hadron Calorimeter](https://www.mdpi.com/1424-8220/23/24/9679)
- (IBM Minsky ECAL-HCAL) [Improving data quality monitoring via a partnership between the CMS experiment at CERN and industry](https://cds.cern.ch/record/2702138/files/10.1051_epjconf_201921401007.pdf)
- (DP note CSC) [Machine learning tools for the automatized monitoring of the CSC detector](https://cds.cern.ch/record/2916189/files/DP2024_095.pdf)
- (Talk CSC) [Anomaly detection for data quality monitoring of the Muon system at CMS](https://indico.cern.ch/event/1338689/contributions/6015462/attachments/2952269/5189958/CHEP2024_Buonsante.pdf)
- (Book 2022) [Chapter 5: Data Quality Monitoring Anomaly Detection](https://cernbox.cern.ch/s/Q2q8NyfmOCNFh6q)
- (General 1) [Anomaly detection using Deep Autoencoders for the assessment of the quality of the data acquired by the CMS experiment](https://cds.cern.ch/record/2650715/files/Fulltext.pdf)
- (General 2) [Towards automation of data quality system for CERN CMS experiment](https://iopscience.iop.org/article/10.1088/1742-6596/898/9/092041/pdf)
- (ATLAS 2025) [Autoencoder-based time series anomaly detection for ATLAS Liquid Argon calorimeter data quality monitoring](https://cds.cern.ch/record/2918639/files/ATL-DAPR-PUB-2024-002.pdf)

## Older DQM references

- 2006 "CMS physics TDR: volume I, detector performance and software" CERN-LHCC-2006-001
- 2008 "The CMS dataset bookkeeping service" Journal of Physics: Conference Series vol 119 (IOP Publishing) p072001
- 2010 "CMS data quality monitoring: systems and experiences" Journal of Physics: Conference Series vol 219 (IOP Publishing) p 072020
- 2010 "CMS data quality monitoring web service" Journal of Physics: Conference Series vol 219 (IOP Publishing) p072055
- 2011 "CMS Run Registry: Data certification bookkeeping and publication system" Journal of Physics: Conference Series vol 331 (IOP Publishing) p 042038
- 2013 "The CMS Data Quality Monitoring Software: Experience and future improvements" Nuclear Science Symposium and Medical Imaging Conference (NSS/MIC), 2013 IEEE (IEEE) pp 1–5
- 2015 "The data quality monitoring challenge at CMS experience from first collisions and future plans" Tech. Rep. CMS-CR-2015-329
- 2015 "The Data Quality Monitoring software for the CMS experiment at the LHC" Journal of Physics: Conference Series vol 664 (IOP Publishing) p 072039
- 2017 "The web based monitoring project at the CMS experiment" Journal of Physics: Conference Series vol 898 (IOP Publishing) p 092040
