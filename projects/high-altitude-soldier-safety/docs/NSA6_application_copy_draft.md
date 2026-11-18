# NSA 6.0 Student Innovator — Application Copy Draft

**Draft only.** The applicant must verify the live form, fill personal/institution fields, review every sentence, and personally submit the declaration. Application window published by Startup India: 27 October–20 November 2026.

## Applicant fields (fill from official records)

- Applicant name: `[enter legal/preferred application name]`
- School/college/university: `[enter exact institution name]`
- Degree / year: `B.Sc. AI & ML, final year` *(verify exact degree title and current year)*
- Age subcategory: `Emerging Entrepreneurs (18–22)` *(verify against the live form)*
- Team size / role: `Individual student innovator` *(describe any mentor or AI-assisted contribution truthfully if the form asks)*
- Contact details: `[enter privately in the official portal; do not add to public repository]`
- Theme: `Defence Power (Raksha Shakti)` *(select only if this exact theme remains available in the live form)*

## Project title

**Himalayan Soldier Safety & Load Monitor: an Offline, Non-Diagnostic Engineering Demonstrator**

## Problem being explored

High-altitude and cold environments create documented health and operational risks for personnel. India already has acclimatization, medical, clothing, shelter, rescue, and evacuation measures. This student project does not assume that soldiers lack care or that a wearable can diagnose illness. It explores a narrower engineering question: can an offline prototype flag when its own sensor input is too poor to present as a reliable trend, while a separate bench module measures pack load against a user-set limit?

## Proposed solution

The software demonstrator reads timestamped values locally, applies a transparent signal-quality gate, and records a generic re-check or wearer check-in prompt. A separate load-cell fixture converts calibrated raw counts into a mass estimate. The modules are tested separately before any integration. The system does not use disease labels, treatment advice, or duty-fitness decisions.

## What is different / innovation claim

Broad soldier wearables, altitude alerts, fatigue monitoring, cold warnings, and smart backpacks have substantial prior art, including Indian DRDO work. Novelty is therefore not established. The project’s current hypothesis is to test a simple, low-cost offline workflow that makes poor-quality input explicit and keeps load measurement as a separate measurable module. A claim of technical novelty or superiority will be made only if a fuller prior-art comparison and bench results support it.

## Intended users and potential impact

The intended long-term context is personnel operating in high-altitude/cold environments and the medical/support staff who assist them. At the current stage, no soldier, medical professional, or unit has validated the need or the design. Potential impact—better visibility of signal quality and pack load—is a hypothesis, not a measured outcome.

## Current stage and evidence

The project currently has a local Python software demonstrator. Eight software behavior checks passed on Python 3.12.10, and the CLI processed three synthetic example rows offline. These results verify code behavior only. No physical sensor prototype, hardware accuracy test, human/soldier data, clinical validation, cold-field trial, or operational benefit has been demonstrated. The example dataset is synthetic and is not real soldier data.

## Next steps

Build and calibrate a bench load-cell fixture; connect one selected sensor to a local logger; test logging and quality flags with controlled simulated inputs; record raw data, calibration, failures, and device mass; obtain qualified feedback through an appropriate authorized route; then reassess feasibility and novelty. No human or serving-soldier testing is planned without required permission, consent, supervision, and review.

## Evidence attachments to select

- 8-slide pitch deck draft: `evidence/NSA6_pitch_draft_v1.pptx`
- Software code and test record: `hssm/`, `tests/`, `docs/software_validation_record.md`
- Problem research and prior-art scan: `docs/research/`
- System/hardware plan and evidence register: `docs/hardware_and_system_plan.md`, `docs/evidence_register.md`
- Real prototype photos/video: `[not available yet; add only when a prototype exists]`

## Submission checks

- Official form is English-only; re-check the live portal before submitting.
- Replace placeholders with true applicant details; do not post personal contact details in GitHub.
- The current official form permits ideation-stage applications and does not require a working prototype, but the application must still accurately state the development stage.
- Remove any unsupported claim of diagnosis, whole-body monitoring, “first,” novelty, soldier endorsement, injury prevention, or lives saved.
- The applicant must review the truthful-information declaration and submit personally.

Official references: [NSA 6.0 page](https://www.startupindia.gov.in/content/sih/en/nsa2026.html), [student application form](https://www.startupindia.gov.in/content/sih/en/nsa-special-categories.html?category=student-led), [PIB announcement](https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2329132&lang=1&reg=3).

