"""
Generate all five candidate figures for the P3.1 slide
(Parameter -> Safe-Strategy Map). Each option is rendered as both
SVG (for the slide deck) and PDF (for the writeup).

Run from the figure directory:
    python3 generate_p3_1_options.py
"""

import os
from typing import Sequence

import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42  # avoid Type 3 fonts per project policy
mpl.rcParams['ps.fonttype'] = 42

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.colors import ListedColormap, to_rgba
import numpy as np
from scipy.spatial import Voronoi


# Repo's tc3 (Thrust III) family colours
TC3_DEEP = '#1f4e7a'      # deep blue, primary
TC3_MID  = '#3a78b3'
TC3_LIGHT = '#bfd6ec'
TC3_FILL = '#e6eef7'

STRATEGY_COLORS = ['#1f4e7a',  # deep navy blue (anchors Thrust III palette)
                   '#e07a3c',  # rich orange — opposite end of the wheel
                   '#3d8e5f',  # forest green — orthogonal hue family
                   '#8e44ad',  # purple — fourth visually distinct hue
                   '#c0a236',  # warm gold (legacy 5th slot, kept for option 2)
                   '#5598c8']  # mid-blue (legacy 6th slot, kept for option 2)
UNCOVERED_GREY = '#d6d6d6'
INK = '#1a2433'
LIGHT = '#9aa3ad'

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
# Production destination for the chosen option (option 1). Other options
# stay in the bake-off folder.
P3_DIR = os.path.normpath(os.path.join(OUT_DIR, '..', 'p3'))


def _save(fig, stem: str, out_dir: str = OUT_DIR) -> None:
    os.makedirs(out_dir, exist_ok=True)
    svg = os.path.join(out_dir, f'{stem}.svg')
    pdf = os.path.join(out_dir, f'{stem}.pdf')
    fig.savefig(svg, bbox_inches='tight')
    fig.savefig(pdf, bbox_inches='tight')
    plt.close(fig)
    print(f'  saved {os.path.basename(svg)} + .pdf  →  {out_dir}')


# -------------------------------------------------------------------------
# Option 1 — Two-panel pipeline (offline build → runtime lookup)
# -------------------------------------------------------------------------

def option_1_pipeline():
    # width_ratios gives the offline panel more horizontal real estate
    # than the runtime panel — exchanges the previously-empty gap between
    # the two panels for breathing room inside the offline columns.
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4),
                             gridspec_kw=dict(wspace=0.10,
                                              width_ratios=[1.18, 1.0]))
    ax_off, ax_run = axes

    # --- Offline panel ---
    # Compress vertical extent so the matplotlib panel title "Offline
    # Build" sits close to the column headers below — no wasted band of
    # whitespace at the top. anchor='N' glues the axes to the TOP of its
    # gridspec cell so the aspect-equal slack falls below instead of being
    # split top/bottom — this lifts the title to the same baseline as
    # Runtime's title (whose axes already hug the cell top vertically).
    ax_off.set_xlim(0, 10); ax_off.set_ylim(0.6, 7.6)
    ax_off.set_aspect('equal'); ax_off.set_anchor('N'); ax_off.axis('off')
    ax_off.set_title('Offline Build', fontsize=12, weight='bold',
                     loc='left', color=INK, pad=4)

    # Layout (offline panel, x in 0–10) — wider fault→grid gap so the
    # altitude axis label and the horizontal flow arrow occupy *different*
    # x-strips even though they share y=Y_MID. Fault boxes start at x=0.10
    # (not 0.0) so the FancyBboxPatch's rounded-corner padding doesn't get
    # clipped by the axes left edge.
    #   fault-class column   x ∈ [0.10, 2.5]   centre 1.30
    #   parameter grid        x ∈ [4.0, 6.7]   centre 5.35
    #   strategy library      x ∈ [7.5, 9.95]  centre 8.70

    # Common vertical centre for all three columns: matches grid mid-height
    # (g_y0 + ny*cell/2 = 3.4 + 1.35 = 4.75). Each column's content is
    # symmetric around this y-line so arrows between columns are short
    # horizontal segments rather than diagonal swoops.
    Y_MID = 4.75

    # Column headers sit roughly midway between the matplotlib panel title
    # ("Offline Build", just above ylim_high=7.6) and the top of the column
    # content (~y=6.13). Centring the headers in that band keeps them
    # closer to the content they label rather than crowding the title.
    HDR_Y = 6.85

    # Fault-class column (left) — boxes pulled inward from the axes left
    # edge so the rounded-corner padding doesn't get clipped.
    ax_off.text(1.30, HDR_Y, 'fault classes', fontsize=10, color=INK,
                weight='bold', ha='center')
    fault_labels = ['$f_1$: motor-1 fail',
                    '$f_2$: GPS loss',
                    '$f_3$: wind > 12 m/s']
    for i, lbl in enumerate(fault_labels):
        y = Y_MID + (1 - i) * 1.04   # i=0 → 5.79, i=1 → 4.75, i=2 → 3.71
        ax_off.add_patch(FancyBboxPatch((0.10, y - 0.34), 2.4, 0.62,
                                        boxstyle='round,pad=0.04,rounding_size=0.10',
                                        facecolor=TC3_FILL, edgecolor=TC3_DEEP,
                                        linewidth=1.0))
        ax_off.text(1.30, y - 0.02, lbl, ha='center', va='center',
                    fontsize=9, color=INK)

    # Parameter grid (middle) — shifted right by 0.3 to widen the gap
    # between fault classes and grid, leaving a clean lane for the
    # altitude label and y-axis arrow without crowding the flow arrow.
    ax_off.text(5.35, HDR_Y, 'parameters $\\mathcal{P}$',
                fontsize=10, color=INK, weight='bold', ha='center')
    g_x0, g_y0 = 4.0, 3.4
    cell = 0.54
    nx, ny = 5, 5
    for i in range(nx):
        for j in range(ny):
            if (i + j) <= 2 or (i == 0 and j >= 3):
                color = UNCOVERED_GREY
            else:
                idx = (i + 2 * j) % 4
                color = STRATEGY_COLORS[idx]
            ax_off.add_patch(Rectangle((g_x0 + i * cell, g_y0 + j * cell),
                                       cell, cell,
                                       facecolor=color, edgecolor='white',
                                       linewidth=0.8))
    # Axis labels on grid. With the wider fault→grid gap, the altitude
    # label can sit at its conventional centred position (y=Y_MID) without
    # colliding with the horizontal flow arrow that now terminates well
    # to the LEFT of the altitude label.
    ax_off.annotate('', xy=(g_x0 - 0.18, g_y0 + ny * cell + 0.05),
                    xytext=(g_x0 - 0.18, g_y0),
                    arrowprops=dict(arrowstyle='->', color=LIGHT, lw=0.9))
    ax_off.text(g_x0 - 0.50, Y_MID, 'altitude',
                rotation=90, ha='center', va='center',
                fontsize=8.5, color=LIGHT)
    ax_off.annotate('', xy=(g_x0 + nx * cell + 0.05, g_y0 - 0.18),
                    xytext=(g_x0, g_y0 - 0.18),
                    arrowprops=dict(arrowstyle='->', color=LIGHT, lw=0.9))
    ax_off.text(g_x0 + nx * cell / 2, g_y0 - 0.50, 'speed',
                ha='center', va='center', fontsize=8.5, color=LIGHT)

    # Strategy library (right) — generic A/B/C/D names + Unrecoverable.
    # Each row's swatch+label combo is centred around the column's x-axis
    # so the whole stack reads as a horizontally-aligned column;
    # vertically the stack is centred around Y_MID.
    ax_off.text(8.70, HDR_Y, 'strategies $\\Sigma_f$',
                fontsize=10, color=INK, weight='bold', ha='center')
    sw_w = 0.45     # swatch width
    sw_x = 7.50     # swatch left edge — combo runs ~7.50 → 9.40, centred on 8.45
    txt_x = sw_x + sw_w + 0.20   # text left edge
    n_rows = 5      # 4 strategies + 1 Unrecoverable
    spacing = 0.72  # row spacing
    # Centre the whole 5-row stack vertically around Y_MID.
    y_top = Y_MID + (n_rows - 1) * spacing / 2
    for i in range(4):
        y = y_top - i * spacing
        ax_off.add_patch(Rectangle((sw_x, y - 0.25), sw_w, 0.50,
                                   facecolor=STRATEGY_COLORS[i], edgecolor='none'))
        ax_off.text(txt_x, y, f'Strategy {chr(ord("A") + i)}',
                    ha='left', va='center', fontsize=9.5, color=INK)
    # Fifth entry: grey swatch labelled "Unrecoverable"
    y_unr = y_top - 4 * spacing
    ax_off.add_patch(Rectangle((sw_x, y_unr - 0.25), sw_w, 0.50,
                               facecolor=UNCOVERED_GREY, edgecolor='none'))
    ax_off.text(txt_x, y_unr, 'Unrecoverable',
                ha='left', va='center', fontsize=9.5, color=INK,
                style='italic')

    # Connecting arrows — both short horizontal segments at Y_MID.
    # Fault→grid arrow stops at x=3.30 (well LEFT of the altitude label
    # at g_x0-0.50=3.50) so the two glyphs occupy disjoint x-strips.
    ax_off.annotate('', xy=(3.30, Y_MID),
                    xytext=(2.55, Y_MID),
                    arrowprops=dict(arrowstyle='->', color=TC3_MID, lw=1.4))
    ax_off.annotate('', xy=(sw_x - 0.05, Y_MID),
                    xytext=(g_x0 + nx * cell + 0.05, Y_MID),
                    arrowprops=dict(arrowstyle='->', color=TC3_MID, lw=1.4))
    # "verify each cell" sits ABOVE the grid (visible) rather than inside it.
    ax_off.text(g_x0 + nx * cell / 2, g_y0 + ny * cell + 0.30,
                'verify each cell',
                ha='center', fontsize=9, color=TC3_DEEP, style='italic',
                weight='bold')

    # Compact caption: just the formula (matches the slide).
    ax_off.text(5.35, 1.6, r'$\sigma_f \;:\; \mathcal{P} \to \Sigma_f$',
                ha='center', fontsize=14, color=INK)

    # --- Runtime panel ---
    ax_run.set_xlim(0, 10); ax_run.set_ylim(0, 10)
    ax_run.set_aspect('equal'); ax_run.axis('off')
    ax_run.set_title('Runtime', fontsize=12, weight='bold',
                     loc='left', color=INK, pad=8)

    # Trigger box at top
    trig_box = FancyBboxPatch((1.0, 8.0), 8.0, 1.4,
                              boxstyle='round,pad=0.10,rounding_size=0.18',
                              facecolor='#fff3e0', edgecolor='#c0392b',
                              linewidth=1.2)
    ax_run.add_patch(trig_box)
    ax_run.text(5.0, 8.95, '⚠ fault $f_2$ detected', ha='center', va='center',
                fontsize=10.5, color='#7a1f16', weight='bold')
    ax_run.text(5.0, 8.30,
                'state readout: $p = (h{=}5\\,\\mathrm{m},\\;'
                'v{=}3\\,\\mathrm{m/s},\\;b{=}72\\%)$',
                ha='center', va='center', fontsize=8.6, color=INK)

    # The table with one cell highlighted — centred at x=5.0 so the
    # lookup arrow above lands flush against the grid's top edge.
    cell = 0.55
    nx_run, ny_run = 5, 5
    g_x0 = 5.0 - nx_run * cell / 2.0   # = 3.625
    g_y0 = 3.5

    # Arrow down — endpoint sits just above the grid's top edge so the
    # arrow visibly points AT the grid, not into empty space above it.
    grid_top = g_y0 + ny_run * cell    # = 6.25
    ax_run.annotate('', xy=(5.0, grid_top + 0.05),
                    xytext=(5.0, 7.95),
                    arrowprops=dict(arrowstyle='->', color=TC3_DEEP, lw=1.6))
    ax_run.text(5.20, 7.05, 'lookup', ha='left', va='center',
                fontsize=9.5, color=TC3_DEEP, style='italic')
    for i in range(5):
        for j in range(5):
            if (i + j) <= 2 or (i == 0 and j >= 3):
                color = UNCOVERED_GREY
            else:
                idx = (i + 2 * j) % 4
                color = STRATEGY_COLORS[idx]
            ax_run.add_patch(Rectangle((g_x0 + i * cell, g_y0 + j * cell),
                                       cell, cell, facecolor=color,
                                       edgecolor='white', linewidth=0.8))
    # Highlighted lookup cell: draw a red border AFTER all cells so that
    # adjacent cells' white edges don't overwrite the right/top sides of
    # the highlight. zorder boosts it above the grid layer.
    hi_i, hi_j = 2, 1
    ax_run.add_patch(Rectangle(
        (g_x0 + hi_i * cell, g_y0 + hi_j * cell), cell, cell,
        facecolor='none', edgecolor='#c0392b', linewidth=2.4,
        zorder=10,
    ))
    # Mark the lookup cell
    ax_run.text(g_x0 + (hi_i + 0.5) * cell, g_y0 + (hi_j + 0.5) * cell, '✓',
                ha='center', va='center', fontsize=14, color='white',
                weight='bold', zorder=11)

    # Arrow to "execute"
    ax_run.annotate('', xy=(8.5, g_y0 + 1.5 * cell),
                    xytext=(g_x0 + 5 * cell + 0.05, g_y0 + 1.5 * cell),
                    arrowprops=dict(arrowstyle='->', color=TC3_DEEP, lw=1.6))
    ax_run.add_patch(FancyBboxPatch((7.8, g_y0 + 1.5 * cell - 0.45),
                                    1.6, 0.9,
                                    boxstyle='round,pad=0.05,rounding_size=0.10',
                                    facecolor=TC3_DEEP, edgecolor='none'))
    ax_run.text(8.6, g_y0 + 1.5 * cell, 'execute\n$\\sigma_{f_2}(p)$',
                ha='center', va='center', fontsize=8.7, color='white',
                weight='bold')

    # Single concise caption at the bottom of the runtime panel.
    ax_run.text(5.0, 1.4,
                'cache miss → online diagnosis/recovery pipeline',
                ha='center', fontsize=8.5, color=LIGHT, style='italic')

    # Chosen option — save to the production directory under figures/p3/
    # so the slide can reference a stable, content-descriptive path.
    _save(fig, 'strategy_map', out_dir=P3_DIR)


# -------------------------------------------------------------------------
# Option 2 — Parameter-space heatmap, colored by strategy
# -------------------------------------------------------------------------

def option_2_heatmap():
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.0),
                             gridspec_kw=dict(wspace=0.25))
    battery_levels = ['battery $= 80\\%$', 'battery $= 60\\%$', 'battery $= 40\\%$']

    # Build three grids of strategy assignments — coverage shrinks with battery.
    n = 8
    rng = np.random.default_rng(2)
    base = rng.integers(0, 4, size=(n, n))
    # Mask out uncovered region; gets bigger with lower battery.
    masks = []
    for k, frac in enumerate([0.10, 0.25, 0.45]):
        threshold = int(frac * n * n)
        # Distance from upper-right corner; fewer cells covered for low battery.
        ii, jj = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
        d = (n - 1 - ii) + (n - 1 - jj)
        order = np.argsort(d.ravel())
        m = np.zeros(n * n, dtype=bool)
        m[order[:threshold]] = True
        masks.append(m.reshape(n, n))

    cmap = ListedColormap(STRATEGY_COLORS[:4] + [UNCOVERED_GREY])
    for ax, batt, mask in zip(axes, battery_levels, masks):
        grid = base.copy()
        grid[mask] = 4  # gray
        ax.imshow(grid.T, cmap=cmap, vmin=0, vmax=4, origin='lower',
                  extent=(0, n, 0, n))
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(LIGHT); spine.set_linewidth(0.8)
        ax.set_title(batt, fontsize=10, color=INK)
        ax.set_xlabel('altitude →', fontsize=9, color=LIGHT)
        ax.set_ylabel('speed →', fontsize=9, color=LIGHT)

    # Legend
    handles = [Rectangle((0, 0), 1, 1, facecolor=c) for c in STRATEGY_COLORS[:4]] + \
              [Rectangle((0, 0), 1, 1, facecolor=UNCOVERED_GREY)]
    labels = ['aggressive descent', 'inertial RTL',
              'min-effort glide', 'hover & reroute',
              'no certified strategy → online inoc.']
    fig.legend(handles, labels, loc='lower center', ncol=5,
               fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Parameter-space slices for fault $f$: '
                 'each cell colored by its certified backup strategy. '
                 'Gray = uncovered.',
                 fontsize=10.5, y=1.02, color=INK)
    _save(fig, 'option_2_heatmap')


# -------------------------------------------------------------------------
# Option 3 — 3-D parameter cube with the certified region highlighted
# -------------------------------------------------------------------------

def option_3_cube():
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure(figsize=(8.0, 6.5))
    ax = fig.add_subplot(111, projection='3d')

    # Cube wireframe
    for x in [0, 1]:
        for y in [0, 1]:
            ax.plot([x, x], [y, y], [0, 1], color=LIGHT, lw=0.8)
        ax.plot([x, x], [0, 1], [0, 0], color=LIGHT, lw=0.8)
        ax.plot([x, x], [0, 1], [1, 1], color=LIGHT, lw=0.8)
        ax.plot([0, 1], [x, x], [0, 0], color=LIGHT, lw=0.8)
        ax.plot([0, 1], [x, x], [1, 1], color=LIGHT, lw=0.8)

    # Certified region: an irregular blob inside the cube, voxel-style
    # Sample a "salvageable" set as cells where (a + b + c) > threshold.
    n = 5
    voxels = np.zeros((n, n, n), dtype=bool)
    colors = np.empty(voxels.shape, dtype=object)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                # Coverage: drone at high alt + moderate speed + decent battery is salvageable
                score = (i / (n - 1)) + (j / (n - 1)) + 0.7 * (k / (n - 1))
                if score > 1.1 and score < 2.4:
                    voxels[i, j, k] = True
                    cidx = (i + 2 * j) % 4
                    colors[i, j, k] = to_rgba(STRATEGY_COLORS[cidx], alpha=0.55)

    # Place voxels in the [0,1]^3 cube with a small inset
    pad = 0.05
    x_grid = np.linspace(pad, 1 - pad, n + 1)
    y_grid = np.linspace(pad, 1 - pad, n + 1)
    z_grid = np.linspace(pad, 1 - pad, n + 1)
    X, Y, Z = np.meshgrid(x_grid, y_grid, z_grid, indexing='ij')
    ax.voxels(X, Y, Z, voxels, facecolors=colors,
              edgecolor=(1, 1, 1, 0.6), linewidth=0.4)

    # Query point: a marker showing "current state lies in certified region"
    ax.scatter([0.65], [0.55], [0.50], color='#c0392b', s=80,
               edgecolor='white', linewidth=1.2, zorder=10)
    ax.text(0.66, 0.55, 0.62, 'current $p$', color='#c0392b',
            fontsize=9, weight='bold')

    # Axis labels
    ax.set_xlabel('altitude', color=INK, fontsize=10, labelpad=8)
    ax.set_ylabel('speed', color=INK, fontsize=10, labelpad=8)
    ax.set_zlabel('battery', color=INK, fontsize=10, labelpad=8)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.view_init(elev=18, azim=-55)

    ax.set_title('Certified region in $\\mathcal{P}$ for fault $f$  —  '
                 'voxel colour = backup strategy assigned',
                 fontsize=10.5, color=INK, pad=10)

    # Legend below
    handles = [Rectangle((0, 0), 1, 1, facecolor=c, alpha=0.6)
               for c in STRATEGY_COLORS[:4]]
    labels = ['aggressive descent', 'inertial RTL',
              'min-effort glide', 'hover & reroute']
    fig.legend(handles, labels, loc='lower center', ncol=4,
               fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, 0.04))
    _save(fig, 'option_3_cube')


# -------------------------------------------------------------------------
# Option 4 — Concrete lookup-table excerpt
# -------------------------------------------------------------------------

def option_4_table():
    fig, ax = plt.subplots(figsize=(10.0, 4.0))
    ax.axis('off')

    rows = [
        ('$f_1$: motor-1 fail',  '5–7 m',  '2–4 m/s', '60–80%',
         'Strategy A', STRATEGY_COLORS[0]),
        ('$f_1$: motor-1 fail',  '0–3 m',  'any',     'any',
         'Strategy C', STRATEGY_COLORS[2]),
        ('$f_2$: GPS loss',      '5–7 m',  '2–4 m/s', '60–80%',
         'Strategy B', STRATEGY_COLORS[1]),
        ('$f_2$: GPS loss',      '8–10 m', 'any',     '60–80%',
         'Strategy D', STRATEGY_COLORS[3]),
        ('$f_3$: wind > 12 m/s', 'any',    'any',     '> 30%',
         'Strategy C', STRATEGY_COLORS[2]),
        ('— uncovered —',        '— ',     '— ',       '— ',
         'fall back to online inoculation', UNCOVERED_GREY),
    ]
    headers = ['fault class $f$', 'altitude', 'speed', 'battery',
               '→ strategy $\\sigma_f(p)$']

    n_rows = len(rows) + 1
    row_h = 0.85 / n_rows
    col_widths = [0.22, 0.13, 0.13, 0.13, 0.39]
    col_x = np.cumsum([0.0] + col_widths[:-1])

    # Header
    y0 = 0.82
    for x, w, h in zip(col_x, col_widths, headers):
        ax.add_patch(Rectangle((x, y0), w, row_h,
                               facecolor=TC3_DEEP, edgecolor='white', lw=1.0))
        ax.text(x + w / 2, y0 + row_h / 2, h, ha='center', va='center',
                fontsize=10, color='white', weight='bold')

    # Body
    for i, (f, alt, spd, batt, strat, col) in enumerate(rows):
        y = y0 - (i + 1) * row_h
        bg = '#f5f7fa' if (i % 2 == 0) else 'white'
        for x, w in zip(col_x, col_widths):
            ax.add_patch(Rectangle((x, y), w, row_h,
                                   facecolor=bg, edgecolor='#dde2e8', lw=0.6))
        ax.text(col_x[0] + 0.012, y + row_h / 2, f, ha='left', va='center',
                fontsize=9.0, color=INK)
        for j, val in enumerate([alt, spd, batt]):
            ax.text(col_x[1 + j] + col_widths[1 + j] / 2, y + row_h / 2, val,
                    ha='center', va='center', fontsize=9.0, color=INK)
        # Strategy cell — accent with color swatch
        ax.add_patch(Rectangle((col_x[4] + 0.008, y + 0.18 * row_h),
                               0.018, 0.64 * row_h,
                               facecolor=col, edgecolor='none'))
        ax.text(col_x[4] + 0.04, y + row_h / 2, strat, ha='left', va='center',
                fontsize=9.0, color=INK)

    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.05, 0.95)

    _save(fig, 'option_4_table')


# -------------------------------------------------------------------------
# Option 5 — Voronoi partition of parameter space
# -------------------------------------------------------------------------

def option_5_voronoi():
    """True 3-D Voronoi tessellation rendered as polyhedral cells.

    The cube is (parameter 1) × (parameter 2) × (fault class). Seeds are
    placed in three z-layers (one per fault class), with z-coordinates
    pre-stretched before the Voronoi computation so cells stay roughly
    layer-aligned. After the Voronoi is computed, vertices are
    un-stretched for display and faces are extracted from the ridge
    structure — each ridge face is rendered exactly once with the colour
    of one adjacent cell, giving smooth polyhedral cells (no voxelization).
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(8.5, 7.2))
    ax = fig.add_subplot(111, projection='3d')

    # 5 seeds: a 2×2 grid on the bottom layer (the four covered strategy
    # regions, A/B/C/D) plus one seed on top centre (the single empty /
    # uncovered region — "no certified strategy → online fallback").
    # The 2×2 grid produces clean rectangular-slab Voronoi cells on the
    # bottom; the top seed produces one large slab on top. Cell shapes
    # are as regular as a Voronoi tessellation gets, and the four
    # strategy cells are clearly separated from each other and from the
    # empty cell.
    seeds = np.array([
        [0.27, 0.27, 0.30],   # Strategy A — front-left bottom
        [0.73, 0.27, 0.30],   # Strategy B — front-right bottom
        [0.27, 0.73, 0.30],   # Strategy C — back-left bottom
        [0.73, 0.73, 0.30],   # Strategy D — back-right bottom
        [0.50, 0.50, 0.85],   # empty / uncovered — top centre
    ])
    # Index 4 maps to the "uncovered grey" colour (rendered separately).
    strat_idx = np.array([0, 1, 2, 3, -1])
    seeds_s = seeds.copy()

    # Ghost generators far outside the unit cube so all "real" cells
    # have bounded boundaries.
    big = 8.0
    ghosts = np.array([[x, y, z]
                       for x in (-big, big)
                       for y in (-big, big)
                       for z in (-big, big)])

    pts = np.vstack([seeds_s, ghosts])
    vor = Voronoi(pts)
    verts_disp = vor.vertices.copy()

    def _order_face(face_pts: np.ndarray) -> np.ndarray:
        """Order vertices of a planar 3-D polygon CCW around its centroid."""
        if face_pts.shape[0] < 3:
            return face_pts
        c = face_pts.mean(axis=0)
        # Approximate face normal via cross of two edges
        v1 = face_pts[1] - face_pts[0]
        v2 = face_pts[2] - face_pts[0]
        n = np.cross(v1, v2)
        nl = np.linalg.norm(n)
        if nl < 1e-12:
            return face_pts
        n /= nl
        # Build orthonormal basis in plane
        ref = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        u = np.cross(n, ref); u /= np.linalg.norm(u)
        w = np.cross(n, u)
        rel = face_pts - c
        ang = np.arctan2(rel @ w, rel @ u)
        return face_pts[np.argsort(ang)]

    # Render each ridge face exactly once. Color by the lower-indexed
    # adjacent generator (so each interior boundary has one definitive
    # colour rather than blending two).
    real_n = len(seeds)
    for ridge_idx, (a, b) in enumerate(vor.ridge_points):
        rv = vor.ridge_vertices[ridge_idx]
        if -1 in rv or len(rv) < 3:
            continue
        # We want ridge faces that bound at least one *real* cell
        if a >= real_n and b >= real_n:
            continue  # ridge between two ghost points — skip
        face_pts = verts_disp[rv]
        # Skip faces that lie almost entirely outside the unit cube
        if np.any(face_pts < -0.05) or np.any(face_pts > 1.05):
            # Naive clip to [0,1] before rendering — produces slightly
            # truncated polygons but keeps the figure inside the cube.
            face_pts = np.clip(face_pts, 0.0, 1.0)
        # Pick the real generator on this ridge
        owner = a if a < real_n else b
        # If both are real, pick the lower index (deterministic)
        if a < real_n and b < real_n:
            owner = min(a, b)
        face_ord = _order_face(face_pts)
        # strat_idx[owner] = -1 means "uncovered" -> grey fallback colour.
        s = strat_idx[owner]
        if s < 0:
            color = UNCOVERED_GREY
        else:
            color = STRATEGY_COLORS[s % len(STRATEGY_COLORS)]
        coll = Poly3DCollection([face_ord],
                                facecolor=color, alpha=0.78,
                                edgecolor='white', linewidth=1.0)
        ax.add_collection3d(coll)

    # Cube-face caps: each of the 6 outer faces of the unit cube is
    # discretised into a fine grid and each grid quad is coloured by its
    # nearest seed. This makes the *cell volumes* visible on the cube
    # exterior — without it, only the interior ridge faces are rendered
    # and the cube edges look "white" in regions where a cell extends
    # to the boundary.
    n_face = 18
    coords = np.linspace(0.0, 1.0, n_face + 1)
    cube_face_specs = [
        (0, 0.0), (0, 1.0),    # x = 0, x = 1
        (1, 0.0), (1, 1.0),    # y = 0, y = 1
        (2, 0.0), (2, 1.0),    # z = 0, z = 1
    ]

    def _nearest_strat(point):
        d = np.linalg.norm(seeds - point, axis=1)
        return strat_idx[int(np.argmin(d))]

    for axis, val in cube_face_specs:
        for i in range(n_face):
            for j in range(n_face):
                u_lo, u_hi = coords[i], coords[i + 1]
                v_lo, v_hi = coords[j], coords[j + 1]
                u_c = 0.5 * (u_lo + u_hi)
                v_c = 0.5 * (v_lo + v_hi)
                if axis == 0:
                    centre = np.array([val, u_c, v_c])
                    quad = [(val, u_lo, v_lo), (val, u_hi, v_lo),
                            (val, u_hi, v_hi), (val, u_lo, v_hi)]
                elif axis == 1:
                    centre = np.array([u_c, val, v_c])
                    quad = [(u_lo, val, v_lo), (u_hi, val, v_lo),
                            (u_hi, val, v_hi), (u_lo, val, v_hi)]
                else:
                    centre = np.array([u_c, v_c, val])
                    quad = [(u_lo, v_lo, val), (u_hi, v_lo, val),
                            (u_hi, v_hi, val), (u_lo, v_hi, val)]
                s = _nearest_strat(centre)
                col = UNCOVERED_GREY if s < 0 else STRATEGY_COLORS[s]
                ax.add_collection3d(Poly3DCollection(
                    [quad], facecolor=col, alpha=0.82,
                    edgecolor='none', zorder=5,
                ))

    # Cube wireframe (keeps the bounding box visually unambiguous)
    cube_edges = [
        ((0, 0, 0), (1, 0, 0)), ((0, 0, 0), (0, 1, 0)), ((0, 0, 0), (0, 0, 1)),
        ((1, 1, 1), (0, 1, 1)), ((1, 1, 1), (1, 0, 1)), ((1, 1, 1), (1, 1, 0)),
        ((1, 0, 0), (1, 1, 0)), ((1, 0, 0), (1, 0, 1)),
        ((0, 1, 0), (1, 1, 0)), ((0, 1, 0), (0, 1, 1)),
        ((0, 0, 1), (1, 0, 1)), ((0, 0, 1), (0, 1, 1)),
    ]
    for (a, b) in cube_edges:
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]],
                color=LIGHT, lw=0.8, alpha=0.7)

    # Seed markers + big strategy labels at each cell centre. The empty
    # (uncovered) cell gets a "—" placeholder rather than a letter.
    for i, s in enumerate(seeds):
        ax.scatter([s[0]], [s[1]], [s[2]], color=INK, s=30,
                   edgecolor='white', linewidth=0.8, zorder=40)
        if strat_idx[i] < 0:
            label = '—'
        else:
            label = chr(ord('A') + strat_idx[i])
        ax.text(s[0] + 0.03, s[1] + 0.03, s[2] + 0.04, label,
                fontsize=14, color=INK, weight='bold', zorder=41)

    # Axis labelling — tight labelpad so the z-axis "fault class" sits
    # close to the box rather than floating off in the margin.
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_zlim(0, 1)
    ax.set_xlabel('parameter 1', fontsize=11, color=INK, labelpad=8)
    ax.set_ylabel('parameter 2', fontsize=11, color=INK, labelpad=8)
    ax.set_zlabel('fault class', fontsize=11, color=INK, labelpad=6)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.view_init(elev=20, azim=-58)

    # Legend below: 4 strategies + 1 uncovered/fallback entry
    handles = [Rectangle((0, 0), 1, 1, facecolor=c, alpha=0.78)
               for c in STRATEGY_COLORS[:4]]
    handles.append(Rectangle((0, 0), 1, 1, facecolor=UNCOVERED_GREY, alpha=0.78))
    labels = [f'Strategy {chr(ord("A") + i)}' for i in range(4)]
    labels.append('uncovered → online fallback')
    fig.legend(handles, labels, loc='lower center', ncol=5,
               fontsize=9.5, frameon=False, bbox_to_anchor=(0.5, 0.04))

    _save(fig, 'option_5_voronoi')


# -------------------------------------------------------------------------
# Driver
# -------------------------------------------------------------------------

def main():
    print(f'Rendering P3.1 figure options into {OUT_DIR}/')
    option_1_pipeline()
    option_2_heatmap()
    option_3_cube()
    option_4_table()
    option_5_voronoi()
    print('done.')


if __name__ == '__main__':
    main()
