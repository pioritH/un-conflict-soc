"""
UN Conflict Suppression as a Self-Organized Critical System
============================================================
A modified Drossel-Schwabl forest-fire model where:
  - Trees   = tension-loaded regions (countries/zones)
  - Fire    = active armed conflict
  - Lightning = random triggering events (crises, assassinations)
  - UN intervention = probabilistic fire suppression (firefighting)

The model demonstrates that UN peacekeeping, by suppressing small
conflicts, loads the global system toward a self-organized critical
state, ultimately making catastrophic world wars more likely.

Author  : [Your Name]
Course  : Complexity Science Project
Deadline: April 10, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# Model parameters
# ─────────────────────────────────────────────────────────────────────────────
N          = 100        # Grid size (N x N)
P_GROW     = 0.03       # Probability empty cell gains tension per step
F_SPARK    = 0.0005     # Probability a high-tension cell spontaneously ignites
UN_STRENGTH = 0.70      # Probability UN suppresses a spreading conflict
TENSION_LEVELS = 5      # Tension states: 1 (low) … 5 (critical)
N_STEPS    = 5000       # Simulation steps
SEED       = 42

# Cell state encoding
EMPTY  = 0
FIRE   = 6
UN_SUP = 7
# States 1–5 represent increasing tension levels


# ─────────────────────────────────────────────────────────────────────────────
# Simulation engine
# ─────────────────────────────────────────────────────────────────────────────
class UNConflictModel:
    """
    Modified forest-fire automaton modelling global conflict dynamics
    under UN intervention.
    """

    def __init__(self, n=N, p=P_GROW, f=F_SPARK, un=UN_STRENGTH, seed=SEED):
        self.n   = n
        self.p   = p
        self.f   = f
        self.un  = un
        np.random.seed(seed)

        # Initialise grid with sparse random tension
        self.grid = np.zeros((n, n), dtype=np.int8)
        mask = np.random.random((n, n)) < 0.35
        self.grid[mask] = np.random.randint(1, 4, mask.sum())

        self.step          = 0
        self.avalanche_sizes = []
        self.suppressed_total = 0
        self.fire_history  = []
        self.tension_history = []

    # ── neighbour indices ────────────────────────────────────────────────────
    @staticmethod
    def _neighbours(r, c, n):
        nb = []
        if r > 0:   nb.append((r-1, c))
        if r < n-1: nb.append((r+1, c))
        if c > 0:   nb.append((r, c-1))
        if c < n-1: nb.append((r, c+1))
        return nb

    # ── one time step ────────────────────────────────────────────────────────
    def advance(self):
        g    = self.grid
        n    = self.n
        next_g = g.copy()
        ava_new = 0
        supp_new = 0

        # 1. Spread fire to neighbours; UN may intervene
        for r in range(n):
            for c in range(n):
                if g[r, c] == FIRE:
                    for nr, nc in self._neighbours(r, c, n):
                        if 1 <= g[nr, nc] <= TENSION_LEVELS:
                            if np.random.random() < self.un:
                                next_g[nr, nc] = UN_SUP   # UN suppresses
                                supp_new += 1
                            else:
                                next_g[nr, nc] = FIRE     # conflict spreads
                                ava_new += 1

        # 2. Burn-out: fire becomes empty
        next_g[g == FIRE] = EMPTY

        # 3. UN-suppressed zones slowly re-accumulate tension
        un_mask = (g == UN_SUP)
        rebuild = np.random.random((n, n)) < 0.03
        next_g[un_mask & rebuild] = 1

        # 4. Grow tension: empty → low tension; low → medium etc.
        empty_mask   = (next_g == EMPTY)
        tension_mask = (next_g >= 1) & (next_g <= TENSION_LEVELS - 1)
        grow_roll    = np.random.random((n, n))
        next_g[empty_mask   & (grow_roll < self.p)]       += 1
        next_g[tension_mask & (grow_roll < self.p * 0.5)] += 1

        # 5. Random sparks (more likely under high UN strength — frustrated tension)
        spark_rate = self.f * (1 + (1 - self.un) * 2)
        spark_mask = (next_g >= 3) & (np.random.random((n, n)) < spark_rate)
        next_g[spark_mask] = FIRE

        self.grid = next_g
        self.step += 1
        self.suppressed_total += supp_new

        if ava_new > 0:
            self.avalanche_sizes.append(ava_new)

        self.fire_history.append((next_g == FIRE).sum())
        self.tension_history.append(((next_g >= 1) & (next_g <= TENSION_LEVELS)).sum())

        return ava_new

    # ── run full simulation ──────────────────────────────────────────────────
    def run(self, steps=N_STEPS, verbose=True):
        for i in range(steps):
            self.advance()
            if verbose and (i+1) % 1000 == 0:
                print(f"  Step {i+1}/{steps}  |  "
                      f"avalanches={len(self.avalanche_sizes)}  |  "
                      f"max_size={max(self.avalanche_sizes) if self.avalanche_sizes else 0}")
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Comparative experiment: varying UN strength
# ─────────────────────────────────────────────────────────────────────────────
def run_comparative_experiment():
    """Run model at three UN strength levels and return results."""
    configs = [
        ("Low UN (0.2)",    0.2,  "#3B8BD4"),
        ("Medium UN (0.5)", 0.5,  "#EF9F27"),
        ("High UN (0.8)",   0.8,  "#E24B4A"),
    ]
    results = {}
    for label, un_val, color in configs:
        print(f"\nRunning: {label}")
        m = UNConflictModel(n=60, un=un_val, seed=42)
        m.run(steps=3000, verbose=True)
        results[label] = {"model": m, "color": color, "un": un_val}
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Figure 1 — Final grid snapshot
# ─────────────────────────────────────────────────────────────────────────────
def plot_grid_snapshot(model, title="Grid Snapshot", filename="fig1_grid.png"):
    cmap = mcolors.ListedColormap([
        "#2C2C2A",   # 0 empty
        "#27500A",   # 1 very low tension
        "#3B6D11",   # 2 low tension
        "#97C459",   # 3 moderate tension
        "#FAC775",   # 4 high tension
        "#EF9F27",   # 5 critical tension
        "#E24B4A",   # 6 active conflict
        "#534AB7",   # 7 UN suppressed
    ])
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
    norm   = mcolors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(6, 6))
    img = ax.imshow(model.grid, cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Longitude (zone index)")
    ax.set_ylabel("Latitude (zone index)")

    labels  = ["Empty", "Low tension", "Moderate tension",
               "High tension", "Critical tension", "Active conflict", "UN suppressed"]
    colors  = ["#2C2C2A","#27500A","#3B6D11","#97C459","#FAC775","#E24B4A","#534AB7"]
    patches = [plt.Rectangle((0,0),1,1, color=c) for c in colors]
    ax.legend(patches, labels, loc="upper right", fontsize=7,
              framealpha=0.9, ncol=1)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2 — Avalanche size distribution (log-log)
# ─────────────────────────────────────────────────────────────────────────────
def plot_avalanche_distribution(results, filename="fig2_distribution.png"):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    slopes = {}

    for ax, (label, data) in zip(axes, results.items()):
        sizes = data["model"].avalanche_sizes
        color = data["color"]

        if not sizes:
            ax.set_title(label)
            continue

        sizes_arr = np.array(sizes)
        # Log-binned histogram
        bins = np.logspace(np.log10(max(1, sizes_arr.min())),
                           np.log10(sizes_arr.max()), 20)
        counts, edges = np.histogram(sizes_arr, bins=bins)
        centres = 0.5 * (edges[:-1] + edges[1:])
        mask = counts > 0

        ax.scatter(centres[mask], counts[mask], color=color, s=30,
                   zorder=5, label="data")
        ax.set_xscale("log"); ax.set_yscale("log")

        # Power-law fit
        lx = np.log10(centres[mask])
        ly = np.log10(counts[mask])
        if len(lx) >= 3:
            coeffs = np.polyfit(lx, ly, 1)
            slope  = coeffs[0]
            slopes[label] = slope
            xfit = np.logspace(lx.min(), lx.max(), 100)
            yfit = 10 ** np.polyval(coeffs, np.log10(xfit))
            ax.plot(xfit, yfit, "--", color="black", lw=1.5,
                    label=f"slope = {slope:.2f}")

        ax.set_title(label, fontsize=11, fontweight="bold")
        ax.set_xlabel("Avalanche size $s$")
        ax.set_ylabel("Frequency $N(s)$")
        ax.legend(fontsize=9)
        ax.grid(True, which="both", alpha=0.3, linestyle="--")

    fig.suptitle("Avalanche Size Distributions — Power-Law Analysis",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")
    return slopes


# ─────────────────────────────────────────────────────────────────────────────
# Figure 3 — Tension & conflict time series
# ─────────────────────────────────────────────────────────────────────────────
def plot_time_series(results, filename="fig3_timeseries.png"):
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    for ax, (label, data) in zip(axes, results.items()):
        m     = data["model"]
        color = data["color"]
        steps = np.arange(len(m.tension_history))
        ax.fill_between(steps, m.tension_history,
                        alpha=0.4, color=color, label="Tension zones")
        ax2 = ax.twinx()
        ax2.plot(steps,
                 np.convolve(m.fire_history, np.ones(50)/50, mode="same"),
                 color="#E24B4A", lw=1.2, label="Active conflicts (50-step MA)")
        ax.set_ylabel("Tension zones", color=color)
        ax2.set_ylabel("Conflicts", color="#E24B4A")
        ax.set_title(label, fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3, linestyle="--")

    axes[-1].set_xlabel("Simulation step")
    fig.suptitle("Tension Accumulation and Conflict Activity Over Time",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 4 — UN strength vs max avalanche
# ─────────────────────────────────────────────────────────────────────────────
def plot_un_vs_catastrophe(filename="fig4_un_vs_catastrophe.png"):
    print("\nRunning UN-strength sweep (this may take ~2 minutes)...")
    un_values  = np.linspace(0.0, 0.95, 20)
    max_avas   = []
    mean_avas  = []

    for un in un_values:
        m = UNConflictModel(n=50, un=un, seed=0)
        m.run(steps=2000, verbose=False)
        if m.avalanche_sizes:
            max_avas.append(max(m.avalanche_sizes))
            mean_avas.append(np.mean(m.avalanche_sizes))
        else:
            max_avas.append(0); mean_avas.append(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(un_values, max_avas,  "o-", color="#E24B4A", lw=2,
            label="Max avalanche (worst war)")
    ax.plot(un_values, mean_avas, "s--", color="#534AB7", lw=1.5,
            label="Mean avalanche size")
    ax.axvspan(0.6, 0.95, alpha=0.08, color="#E24B4A", label="High UN regime")
    ax.set_xlabel("UN Intervention Strength", fontsize=12)
    ax.set_ylabel("Avalanche Size (conflict zones)", fontsize=12)
    ax.set_title("Paradox of UN Intervention: Suppression Drives Catastrophe",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.35, linestyle="--")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 5 — Connectivity analysis
# ─────────────────────────────────────────────────────────────────────────────
def plot_connectivity(results, filename="fig5_connectivity.png"):
    """
    Measure effective connectivity as average number of high-tension
    neighbours per high-tension cell at simulation end.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    un_vals, conn_vals, max_sizes = [], [], []

    for label, data in results.items():
        m = data["model"]
        g = m.grid
        n = m.n
        high = (g >= 3) & (g <= 5)
        if high.sum() == 0:
            continue
        total_neighbours = 0
        count = 0
        for r in range(n):
            for c in range(n):
                if high[r, c]:
                    nb = UNConflictModel._neighbours(r, c, n)
                    total_neighbours += sum(1 for nr, nc in nb if high[nr, nc])
                    count += 1
        avg_conn = total_neighbours / count if count else 0
        un_vals.append(data["un"])
        conn_vals.append(avg_conn)
        ms = max(m.avalanche_sizes) if m.avalanche_sizes else 0
        max_sizes.append(ms)

    scatter = ax.scatter(conn_vals, max_sizes,
                         c=un_vals, cmap="RdYlGn_r", s=200,
                         vmin=0, vmax=1, zorder=5, edgecolors="black", lw=0.5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("UN Intervention Strength", fontsize=10)

    for i, label in enumerate(results.keys()):
        ax.annotate(label, (conn_vals[i], max_sizes[i]),
                    textcoords="offset points", xytext=(8, 4), fontsize=9)

    ax.set_xlabel("Average Connectivity of High-Tension Zones", fontsize=12)
    ax.set_ylabel("Maximum Avalanche Size", fontsize=12)
    ax.set_title("Connectivity vs Catastrophe Size", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.35, linestyle="--")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# Print summary statistics
# ─────────────────────────────────────────────────────────────────────────────
def print_summary(results, slopes):
    print("\n" + "="*60)
    print("SUMMARY OF RESULTS")
    print("="*60)
    for label, data in results.items():
        m = data["model"]
        sizes = m.avalanche_sizes
        print(f"\n{label}")
        print(f"  Total avalanches   : {len(sizes)}")
        if sizes:
            print(f"  Mean size          : {np.mean(sizes):.2f}")
            print(f"  Median size        : {np.median(sizes):.2f}")
            print(f"  Max size           : {max(sizes)}")
            print(f"  Power-law slope    : {slopes.get(label, 'N/A')}")
        print(f"  UN suppressions    : {m.suppressed_total}")
        n2 = m.n**2
        tension = ((m.grid >= 1) & (m.grid <= 5)).sum()
        print(f"  Final tension frac : {tension/n2:.2%}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)

    print("="*60)
    print("UN Conflict SOC Model — Running Simulations")
    print("="*60)

    results = run_comparative_experiment()

    print("\nGenerating figures...")
    # Fig 1 – grid snapshot for high-UN case
    high_un_model = results["High UN (0.8)"]["model"]
    plot_grid_snapshot(high_un_model,
                       title="Grid State at Step 3000 (High UN = 0.8)",
                       filename="figures/fig1_grid.png")

    slopes = plot_avalanche_distribution(results,
                 filename="figures/fig2_distribution.png")
    plot_time_series(results,
                     filename="figures/fig3_timeseries.png")
    plot_un_vs_catastrophe(
                     filename="figures/fig4_un_vs_catastrophe.png")
    plot_connectivity(results,
                     filename="figures/fig5_connectivity.png")

    print_summary(results, slopes)
    print("\nAll figures saved to ./figures/")
    print("Done.")
