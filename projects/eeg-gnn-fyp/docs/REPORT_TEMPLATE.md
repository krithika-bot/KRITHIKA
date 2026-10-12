# Electrode-graph neural networks for cross-subject EEG motor-imagery decoding
Krithika K · VISTAS, Chennai · [date]

How to use: run the experiments, open `results/summary.md`, and replace every `[[...]]` with the real value.
Do not write a sentence whose claim your numbers do not support. 4–5 pages.

## Abstract  (150–200 words, written LAST)
[[Problem in one sentence. Method in one sentence. Data + protocol (public EEGMMIDB, N subjects, subject-wise CV).
Main result with CI. Honest one-line limitation.]]

## 1. Introduction
* Why decode motor imagery (rehabilitation, BCI) and why cross-subject generalisation is the bottleneck.
* Why electrode geometry might help (EEG is a spatial sampling of a cortical field) — and why it might not.
* The three hypotheses H1–H3 exactly as in the README. Contributions: (a) a leakage-controlled cross-subject protocol,
  (b) a graph ablation with identical parameter counts, (c) open, reproducible code.

## 2. Related work  (half a page)
[[CSP (Ramoser 2000); EEGNet (Lawhern 2018); GCN (Kipf & Welling 2017); 2–4 papers on graph/GNN EEG that YOU have read.
State how this work differs: protocol and controls, not "novel architecture".]]

## 3. Data
EEGMMIDB, runs 4/8/12, [[N]] subjects after exclusions ([[list skipped]]), [[n_trials]] trials, 64 ch, 160 Hz, 8–30 Hz band-pass,
0–4 s epochs. Figure: `figures/erd_sanity.png` (expected contralateral mu suppression in [[x%]] of subjects).

## 4. Methods
4.1 Baselines (CSP+LDA, band-power+LR, EEGNet). 4.2 Graph network (diagram + equations: H' = ELU(LN(Â H W))).
4.3 Graphs: identity / uniform / random / distance / corr — what each controls for. Figure: `graph_*.png`.
4.4 Training: AdamW, lr, epochs, early stopping on validation subjects. 4.5 Protocol: subject-wise CV, seeds,
metrics, bootstrap CI over subjects, Wilcoxon + Holm.

## 5. Results
Table 1 (paste from `results/summary.md`): method | subject acc [CI] | AUC.
Figure `method_comparison.png`. Table 2: paired comparisons (mean difference, CI, Holm-p).
Controls: permuted-label accuracy = [[x]] (≈ 0.50 expected). Learning curves: `learning_curves.png`.

Wording guide — pick the sentence your data supports:
* Graph > no-graph with CI excluding 0 and Holm-p < 0.05: "A distance graph improved accuracy by [[d]] (95% CI [[..]])."
* Difference small / CI includes 0: "We found no reliable benefit of the electrode graph under this protocol."
* Graph < baseline: report it plainly and discuss why (capacity, small data, subject variability).

## 6. Discussion
What the ablation says about *where* any gain comes from; per-subject variability (scatter plots);
failure cases; relation to the literature; what would change your conclusion.

## 7. Limitations
Single dataset, healthy subjects, 2 classes, ~45 trials/subject, limited tuning, volume conduction in `corr`, no clinical claim.

## 8. Conclusion and future work  (3–4 sentences)
[[One-sentence answer to the research question. Next step: additional datasets, within-subject fine-tuning, my clinical EEG data
(only with approval and de-identification).]]

## References
See README.
