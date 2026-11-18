# High-Altitude Soldier Safety Project — Evidence Pack v1

**Prepared:** 16 November 2026  
**Stage:** Desk-research evidence; no prototype or user study has been conducted yet.  
**Working project:** Himalayan Soldier Safety & Load Monitor  
**Purpose:** Establish what is documented about high-altitude soldier risks, what existing support already exists, and what the student prototype could responsibly test.

## 1. Short evidence-based problem statement

Indian soldiers posted to Siachen and other super-high-altitude areas face documented environmental and medical hazards, including high-altitude pulmonary illness, cold injury, hypothermia, snow blindness, avalanches, crevasses, and other weather-related threats. Government and peer-reviewed sources also document that India already uses preventive measures such as acclimatization, medical cover, specialized clothing, shelter, training, and rescue/evacuation capabilities.

The evidence supports researching whether an additional **offline, non-diagnostic check-in and load-awareness prototype** can help make selected signals and pack-load information easier to review. The sources do **not** establish that soldiers lack all monitoring, that a wearable can diagnose organ damage, or that this proposed device would reduce illness or deaths. Those are questions for later validation.

## 2. Evidence ledger

| ID | Documented claim | Source and evidence | What it supports | Limits / careful interpretation |
|---|---|---|---|---|
| E01 | High-altitude soldier deaths were officially reported for 2017–2019; causes included HAPO, pulmonary thrombo-embolism and other causes. | Government of India, Lok Sabha answer to Unstarred Question 684, answered 16 Sep 2020: fatal casualties 6 in 2017, 8 in 2018, and 8 in 2019. [Official answer](https://sansad.in/getFile/loksabhaquestions/annex/174/AU684.pdf?source=pqals) | Establishes official recognition that high-altitude service has serious fatal risks. | These are historical counts for Siachen and other super-high-altitude areas; they are not current rates, not all illness-related, and not Siachen-only counts. Do not present them as current annual deaths. |
| E02 | The Government already describes multiple prevention/support measures. | The same Lok Sabha answer lists pre-induction medical examination, medical cover, acclimatization, specialized training, shelters, clothing, rations, rescue technology, evacuation and advisories. [Official answer](https://sansad.in/getFile/loksabhaquestions/annex/174/AU684.pdf?source=pqals) | Prevents the false claim that no protections or systems exist; defines the project as a possible additional support layer. | Public answer does not provide device-level deployment details or evaluation results for each measure. |
| E03 | Medical literature identifies several Siachen-specific operational health hazards. | Review, *The Highest Battlefield of the World: Medical Problems and Solutions*, Medical Journal Armed Forces India: HAPO, AMS, frostbite/chilblains, hypothermia, snow blindness, avalanches, crevasses, fires and carbon-monoxide risks are among those discussed. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/27408227/) | Supports choosing altitude/cold safety as a meaningful research area. | This is a review article, not a current prevalence dataset. It does not show how common each condition is today or prove the prototype can detect them. |
| E04 | HAPE was recorded among Indian Army soldiers in Ladakh during 2016–2019. | Observational study of hospital records: 838 cases among 141,790 inductions/re-inductions; reported incidence 5.91 per 1,000 over the study period. Breathlessness was the most frequent complaint; cough and headache were also reported. [Open-access study](https://www.ijcmph.com/index.php/ijcmph/article/download/7028/4554/29362) | Provides India-specific evidence for respiratory/altitude risk and candidate symptom prompts. | Covers Ladakh ranges and hospital records, not Siachen alone or all soldiers. The denominator is induction/re-induction events, not a simple person-year risk. Results are from 2016–2019 and are not a wearable validation study. |
| E05 | High-altitude exposure has been associated with measurable changes in cognitive task performance in soldiers. | Study at 4,111 m compared 20 Indian and 20 Kyrgyz soldiers over time using learning, memory, reaction-time and related tests. Indian soldiers showed some cognitive-task deterioration at day 7 followed by improvement toward baseline by day 21. [Journal study](https://journals.sagepub.com/doi/full/10.1089/ham.2018.0139) | Supports researching fatigue/cognition check-ins as a separate, carefully scoped feature. | Small study, specific altitude and acclimatization period. It measured task performance; it does not establish widespread clinical memory loss or permanent brain injury among Siachen soldiers. |
| E06 | A study assessed psychological health before and after extreme high-altitude deployment. | Longitudinal study of 334 troops; screening-tool scores increased after deployment, while the reported average GHQ-12 score remained below the stated “caseness” level. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/34594071/) | Supports keeping optional, private well-being check-ins in the research scope. | Screening-score change is not a diagnosis. This does not justify covert emotion inference or an AI mental-illness detector. |
| E07 | Indian Army research has explored HAPE assessment with symptoms and measurements together. | Study involving Indian soldiers at 2,700–3,500 m reported that a combination of symptoms, heart rate, respiratory rate and SpO2 was suggestive in its specific study setting. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/26663962/) | Shows why health-risk assessment is contextual and should be reviewed by qualified medical staff. | Published criteria from that altitude and study population must not be copied as universal thresholds for our prototype or for Siachen. |
| E08 | Frostbite can damage tissue and may lead to tissue loss in severe cases; numbness can delay recognition. | CDC frostbite guidance and WHO public-health information describe numbness, tissue injury, and possible amputation in severe cases. [CDC](https://www.cdc.gov/winter-weather/prevention/preventing-frostbite.html), [WHO](https://www.who.int/europe/news-room/questions-and-answers/item/public-health-advice-in-the-aftermath-of-an-earthquake) | Supports a future glove/boot temperature and exposure-reminder research module. | Skin/ambient temperature sensors cannot diagnose frostbite or guarantee that tissue is safe. A torso-only sensor cannot directly monitor toes or fingers. |
| E09 | India has publicly reported an earlier DRDO wearable physiological-monitoring technology demonstration. | Ministry of Defence/PIB stated in 2017 that DRDO’s WPMS could wirelessly transmit vital parameters up to 60 m line-of-sight and was to be inducted after Army field trials. [PIB release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1484113&lang=2&reg=48) | Establishes relevant Indian prior art; our project must be differentiated from existing work. | This 2017 release does not confirm the system’s present induction/deployment status. Do not claim that India has no soldier wearable monitoring. |
| E10 | DRDO has publicly described an ergonomic 70 L backpack for soldier load carriage. | DRDO describes adjustable fit, cushioning, load distribution, hydration and modular attachments. [DRDO backpack page](https://drdo.gov.in/drdo/en/offerings/transfer-of-technologies/ergonomically-designed-backpack-70-lt) | Our pack component should be framed as electronic load measurement/checklist research, not a claim that we invented the first ergonomic soldier backpack. | Public product description does not evaluate our proposed sensorized pack or prove comparative comfort/performance. |
| E11 | Cold and movement can distort pulse-oximetry measurements. | NATO high-altitude medical guidance cautions that cold hands and movement artifact can produce aberrant SpO2 readings. [Guidance PDF](https://www.coemed.org/files/stanags/02_AJMEDP/AJMedP-4-3_SRD_EDA_V1_E_2561.pdf) | Makes signal-quality detection and “reading unreliable” prompts core engineering requirements. | A prototype SpO2 reading is not a medical diagnosis or an all-clear signal. |

## 3. What this evidence does and does not prove

### Supported by the sources
- High-altitude and cold-related risks are documented for Indian military settings, including Ladakh and Siachen.
- HAPE and cold injury are legitimate problem areas to investigate.
- Cognitive and psychological measures have been studied in soldiers at altitude.
- India already has medical, acclimatization, clothing, rescue, wearable-monitoring and load-carriage work; our project must acknowledge it.

### Not established yet
- Current Siachen-only rates for frostbite, HAPE, cognitive impairment, organ injury or amputations.
- That a soldier often fails to notice a specific condition before it becomes serious.
- That our chosen wearable sensors can detect impending HAPE, HACE, frostbite, organ damage or memory loss.
- That integrating a wearable and a smart-load module improves health outcomes.
- That soldiers want this exact device or would wear it during duty.

## 4. Evidence-based project hypothesis

**Research hypothesis:** A low-cost prototype that checks signal quality, records selected physiological/activity trends, offers an optional wearer check-in, and separately measures backpack load may provide useful non-diagnostic prompts in controlled testing. Whether those prompts are accurate, comfortable and operationally useful remains to be tested.

**Initial prototype outputs:** “Sensor reading unreliable,” “please re-check / self-check,” and “consider reporting to medical staff.” No disease labels, treatment instructions, or guarantee of safety.

## 5. Recommended next evidence steps

1. Complete a prior-art comparison of DRDO WPMS, LifeLens, AMS-alert research, DRDO load-carriage products, and other documented systems.
2. Convert the evidence into a short needs statement and a requirements list; do not claim a specific unmet need until supported by user/medical input.
3. Collect no soldier or sensitive operational data without appropriate permission. Early prototype work can use bench tests and non-clinical signal-quality experiments.
4. When available, seek feedback from a high-altitude medical professional, ergonomics specialist, or retired service member. Record consent and distinguish opinion from measured evidence.
5. Test each engineering claim separately: sensor signal quality, false-alert behavior, offline operation, battery performance, pack measurement error, comfort and device weight.

## References

- Ministry of Defence, Government of India. Lok Sabha Unstarred Question 684, “Casualties of Soldiers,” 16 September 2020. [PDF](https://sansad.in/getFile/loksabhaquestions/annex/174/AU684.pdf?source=pqals)
- Khanna et al. “The Highest Battlefield of the World: Medical Problems and Solutions.” *Medical Journal Armed Forces India*. [PubMed](https://pubmed.ncbi.nlm.nih.gov/27408227/)
- Adhya et al. “Clinico-epidemiological profile of high altitude pulmonary edema.” *International Journal of Community Medicine and Public Health*, 2021. [Full text PDF](https://www.ijcmph.com/index.php/ijcmph/article/download/7028/4554/29362)
- Ray et al. “A Temporal Study on Learning and Memory at High Altitude in Two Ethnic Groups.” *High Altitude Medicine & Biology*, 2019. [Journal page](https://journals.sagepub.com/doi/full/10.1089/ham.2018.0139)
- Rajesh et al. “Study of psychological effects of deployment at extreme high altitude area on soldiers.” *Medical Journal Armed Forces India*, 2021. [PubMed](https://pubmed.ncbi.nlm.nih.gov/34594071/)
- Chawla & Tripathi. “Objective criteria for diagnosing high altitude pulmonary edema…” *Medical Journal Armed Forces India*, 2015. [PubMed](https://pubmed.ncbi.nlm.nih.gov/26663962/)
- Ministry of Defence/PIB. DRDO Wearable Physiological Monitoring System update, 10 March 2017. [PIB release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1484113&lang=2&reg=48)
- DRDO. “Ergonomically Designed Backpack (70 Lt).” [Official product page](https://drdo.gov.in/drdo/en/offerings/transfer-of-technologies/ergonomically-designed-backpack-70-lt)
- CDC. “Preventing Frostbite.” [Guidance](https://www.cdc.gov/winter-weather/prevention/preventing-frostbite.html)
- NATO Centre of Excellence for Military Medicine. High-altitude medical guidance. [PDF](https://www.coemed.org/files/stanags/02_AJMEDP/AJMedP-4-3_SRD_EDA_V1_E_2561.pdf)

