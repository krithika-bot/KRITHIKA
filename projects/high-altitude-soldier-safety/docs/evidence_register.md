# Project Evidence Register

Keep each claim tied to its evidence. Add a date, version, source/file, and limitation for every new entry. Never replace synthetic data with a real-data label.

| ID | Claim/evidence item | Type | Status | File/source | Limitation / next action |
|---|---|---|---|---|---|
| R01 | India has documented high-altitude soldier risks and existing protections. | Public source | Prepared in desk research | [`research/high_altitude_soldier_evidence_pack_v1.md`](research/high_altitude_soldier_evidence_pack_v1.md) | Older counts and non-Siachen-specific studies have limits; preserve dates/geography. |
| R02 | Related soldier wearables, altitude alerts, fatigue monitoring, cold warnings, and load systems exist. | Prior-art scan | Preliminary | [`research/high_altitude_patent_prior_art_scan_v1.md`](research/high_altitude_patent_prior_art_scan_v1.md) | Not legal advice/FTO; verify official status and claims. |
| R02a | Public comparison of India and selected country disclosures. | Desk comparison | Prepared | [`research/high_altitude_device_comparison_v1.md`](research/high_altitude_device_comparison_v1.md) | Public information gaps do not prove a country lacks a capability. |
| R02b | Non-clinical validation protocol. | Test protocol | Prepared; no physical results | [`research/high_altitude_prototype_validation_plan_v1.md`](research/high_altitude_prototype_validation_plan_v1.md) | Protocol is not a result. |
| R03 | Python software refuses invalid/low signal-quality values as reliable trends. | Software behavior | Implemented; run checks to record | `hssm/monitor.py`, `tests/test_monitor.py` | Unit tests do not validate a physical sensor or medical performance. |
| R04 | Synthetic CSV produces deterministic generic statuses. | Software demonstration | Synthetic only | `data/synthetic_demo.csv` and CLI output | Never present as human/soldier data. |
| R05 | Offline local run works. | Software behavior | Verify in actual environment | README command and local output | Does not establish field connectivity or battery performance. |
| R06 | Sensor signal quality under movement/cold. | Bench result | Not tested | Add to `evidence/` after physical setup | Need calibrated sensor fixture, protocol, repeated runs; no human cold exposure. |
| R07 | Relative shoulder/hip load-share accuracy and repeatability. | Bench result | Not tested; revised Phase-1 hardware scope | Add to `evidence/` after a multi-point load-path rig is calibrated | Use known distributions and independent references; report refit variation, drift, motion failures, mass, and false/missed prompts. |
| R08 | Soldier/medical expert need and usability. | User feedback | Not collected | Add only if authorized and consented | Do not request classified, tactical, or personal medical information. |
| R09 | Project novelty. | Patentability / prior art | Not established; hypothesis narrowed to a cold/motion-aware, uncertainty-gated relative load-share retrofit | [`novelty_research_gap_v2.md`](novelty_research_gap_v2.md) | Shoulder/hip balance sensing is known prior art. Review is scoped, not a comprehensive patentability/FTO opinion; expert claim review and comparative bench evidence still needed. |
| R10 | Award eligibility and current deadline. | Official programme rules | Checked 18 Nov 2026 | [`award_cycle_source_check.md`](award_cycle_source_check.md) | Rules and dates can change; no award outcome can be guaranteed. |
| R11 | NSA application text mapped to project stage and evidence. | Draft application copy | Prepared; applicant review required | [`NSA6_application_copy_draft.md`](NSA6_application_copy_draft.md) | Not submitted; applicant must fill personal details and verify current form. |

