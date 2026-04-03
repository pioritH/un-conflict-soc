# UN Conflict Suppression as a Self-Organized Critical System

> **Complexity Science — Individual Project**  
> Author: Harshit Bhatt | Entry No: 2023CH10471  
> Email: ch1230471@iitd.ac.in  
> Department of Chemical Engineering, IIT Delhi  
> Submitted: April 10, 2026 | Course instructor: Prof. Rajesh

---

## Overview

This project applies **Self-Organized Criticality (SOC)** theory to model
the global conflict landscape, treating the United Nations (UN) peacekeeping
apparatus as a fire-suppression mechanism analogous to the Drossel–Schwabl
forest-fire model.

**Core thesis:** By suppressing small conflicts, UN peacekeeping prevents the
natural dissipation of geopolitical tension. This loads the global system toward
a maximally critical state in which a single spark can trigger a catastrophic
world-war avalanche — the *peacekeeping paradox*.

---

## Repository Structure

```
un-conflict-soc/
├── python/
│   └── un_conflict_soc.py     # Main simulation + all figure generation
├── latex/
│   ├── main.tex               # Full manuscript (journal format)
│   ├── references.bib         # BibTeX bibliography
│   └── figures/               # Generated figures (auto-populated by script)
│       ├── fig1_grid.png
│       ├── fig2_distribution.png
│       ├── fig3_timeseries.png
│       ├── fig4_un_vs_catastrophe.png
│       └── fig5_connectivity.png
├── main.pdf                   # Compiled manuscript
└── README.md
```

---

## Model Description

The model is a modified Drossel–Schwabl cellular automaton on an N×N lattice.

| Cell State | Code | Meaning |
|---|---|---|
| Empty | 0 | Post-conflict, peaceful |
| Low tension | 1 | Minor grievances |
| Moderate tension | 2 | Active diplomatic disputes |
| High tension | 3 | Arms races, proxy conflicts |
| Critical tension | 4 | Open mobilization |
| Maximum tension | 5 | Pre-war brinkmanship |
| Active conflict | 6 | Ongoing war (fire) |
| UN-suppressed | 7 | Conflict quenched by peacekeeping |

### Update Rules (each time step)

1. **Fire spreads** to tension-loaded neighbours; UN intervenes with probability α
2. **Burn-out** — active conflicts become empty
3. **UN-suppressed zones** slowly recover tension (rate 0.03/step)
4. **Tension growth** — empty zones and tension zones grow stochastically (rate p)
5. **Random spark** — critical zones ignite spontaneously (rate f)

---

## How to Run

### Requirements

```bash
pip install numpy matplotlib scipy powerlaw
```

### Run full simulation + generate all figures

```bash
cd python
python un_conflict_soc.py
```

This will:
- Run the model at 3 UN strength levels (0.2, 0.5, 0.8) for 3000 steps each
- Run a 20-point UN strength sweep (≈ 2 minutes)
- Generate all 5 figures in `figures/`
- Print summary statistics to console

### Compile LaTeX

```bash
cd latex
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## Key Results

| Regime | Total avalanches | Mean size | Max size | Power-law τ | Tension fraction |
|---|---|---|---|---|---|
| Low UN (α=0.2) | 2999 | 53.9 | 160 | 1.26 | 57.3% |
| Medium UN (α=0.5) | 2992 | 16.0 | 48 | 0.64 | 74.4% |
| High UN (α=0.8) | 2377 | 2.6 | 12 | −2.52 | 89.3% |

The power-law exponent τ ≈ 1.26 (low UN regime) is consistent with
Richardson's (1948) empirical finding for war casualty distributions.

---

## Figures

**Fig 1** — Spatial grid at T=3000 (high UN). 89% of world loaded with tension.

**Fig 2** — Avalanche size distributions (log-log). Power-law signature of SOC.

**Fig 3** — Time series of tension zones and active conflicts.

**Fig 4** — The peacekeeping paradox: UN strength vs. max avalanche size.

**Fig 5** — Connectivity of high-tension zones vs. catastrophe magnitude.

---

## Acknowledgements

- Conceptual analogy (UN as fire suppression) — original idea of the author
- Interactive browser simulation and Python code — generated with Claude (Anthropic, April 2026)
- LaTeX manuscript — generated with Claude (Anthropic, April 2026), reviewed and approved by author
- Prof. Rajesh — course instructor and project brief

**AI Prompts used:**
1. *"I need to complete this project... model similar to forest fire model... UN as a system controlling smaller conflicts... sudden big war emerges as catastrophe"*
2. *"What does it show?"* (on simulation screenshot)
3. *"Gen entire project for me — everything that is required for submission"*

---

## References

- Bak, Tang & Wiesenfeld (1987) — Self-organized criticality
- Drossel & Schwabl (1992) — Forest-fire model
- Richardson (1948) — Variation of frequency of fatal quarrels
- Cederman (2003) — Modeling the size of wars
- Clauset, Shalizi & Newman (2009) — Power-law distributions in empirical data

---

## License

MIT License — free to use, modify, and distribute with attribution.
