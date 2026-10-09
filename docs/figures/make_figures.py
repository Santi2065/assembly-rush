"""Regenerates the figures and numbers shown in the README.

    pip install numpy matplotlib
    python docs/figures/make_figures.py

Figure 1 and the sprites in Figure 4 are the game's own images. Figures 2-4 are
derived from the project files: the scene order in ProjectSettings/EditorBuildSettings.asset,
the silhouette grids in Assets/Puzzle/Shadows/ShadowsArrays/*.cs and the runner
constants in Assets/Scripts/GameManager.cs, John.cs and Assets/Scenes/Dia1.unity.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for f in Path("/usr/share/fonts/lm").glob("lm*10-*.otf"):  # Latin Modern, if installed
    font_manager.fontManager.addfont(str(f))
plt.style.use(HERE / "paper.mplstyle")
C = plt.rcParams["axes.prop_cycle"].by_key()["color"]
INK, GRAY = "#1a1a1a", "#8c8c8c"
A = ROOT / "Assets"


def save(fig, name, **kw):
    fig.savefig(HERE / name, metadata={"Date": None} if name.endswith(".svg") else {}, **kw)
    plt.close(fig)


def img(path):
    return np.asarray(Image.open(path).convert("RGBA"))


# ---- Figure 1: the three story cards, in build order (TextScene0, 1, 2)
story = ["_dfc5aef3-9cd1-472c-9ddf-be536d7db99c.jpg", "_f781a3bd-a2b8-4d4d-812b-50efcb29bf4d.jpg",
         "_0ff08fd4-64eb-448e-ba1a-b5863231a376.jpg"]
titles = ["(a) TextScene0", "(b) TextScene1", "(c) TextScene2"]
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.62))
for ax, s, t in zip(axes, story, titles):
    ax.imshow(img(A / "Files/TextSceneBackGround" / s), interpolation="lanczos")
    ax.set_title(t)
    ax.axis("off")
fig.tight_layout(w_pad=0.6)
save(fig, "fig1-story.png", dpi=220)
im = Image.open(HERE / "fig1-story.png").convert("RGB")
im.quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(HERE / "fig1-story.png",
                                                                                         optimize=True)


# ---- Figure 2: scene flow
def node(ax, x, y, name, sub, color, dashed=False, w=15.0, h=5.6):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.1,rounding_size=0.8",
                                fc="white", ec=color, lw=0.9, ls="--" if dashed else "-"))
    ax.text(x, y + 0.9, name, ha="center", va="center", fontsize=8, family="monospace", color=INK)
    ax.text(x, y - 1.2, sub, ha="center", va="center", fontsize=7, color="#4d4d4d")


def arrow(ax, a, b, label=None, rad=0.0, color=INK, lo=(0, 1.0)):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->,head_length=0.5,head_width=0.25", ec=color,
                                                    lw=0.8, shrinkA=0, shrinkB=0,
                                                    connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((a[0] + b[0]) / 2 + lo[0], (a[1] + b[1]) / 2 + lo[1], label, ha="center", fontsize=6.5,
                color="#4d4d4d")


fig = plt.figure(figsize=(7.2, 2.7))
ax = fig.add_axes((0, 0, 1, 1))
ax.set_xlim(0, 72)
ax.set_ylim(-3.2, 25.2)
ax.axis("off")
row1 = [("0 Menu", "title screen", C[5]), ("1 TextScene0", "story card", C[3]),
        ("2 Puzzle_Lv1", "4 silhouettes", C[0]), ("3 TextScene1", "story card", C[3])]
row2 = [("4 TransitionToRunner", "assemble 4 parts", C[2]), ("5 TextScene2", "story card", C[3]),
        ("6 Dia1", "runner, 111 s", C[1]), ("8 WinScene", "you win", C[5])]
xs = [8.5, 26.5, 45.5, 63.5]
for x, (n, s, c) in zip(xs, row1):
    node(ax, x, 21.5, n, s, c)
for x, (n, s, c) in zip(xs, row2):
    node(ax, x, 8.5, n, s, c, w=17.0 if n.startswith("4") else 15.0)
for i in range(3):
    arrow(ax, (xs[i] + 7.6, 21.5), (xs[i + 1] - 7.6, 21.5))
arrow(ax, (63.5, 18.6), (8.5, 11.4), rad=0.0)
arrow(ax, (xs[0] + 8.6, 8.5), (xs[1] - 7.6, 8.5))
arrow(ax, (xs[1] + 7.6, 8.5), (xs[2] - 7.6, 8.5))
arrow(ax, (xs[2] + 7.6, 8.5), (xs[3] - 7.6, 8.5), "distance done", lo=(0, 3.4))
arrow(ax, (xs[2] + 1.5, 11.4), (xs[2] + 1.5, 18.6), "time up:\nLoadScene(2)", lo=(4.2, -1.3), color=C[1])
node(ax, xs[3], -0.2, "7 EndScene", "not loaded by any script", GRAY, dashed=True, w=17.0, h=4.6)
ax.text(1.0, -0.2, "scene number = build index; story cards advance on Enter, click or after 10 s", fontsize=6.5,
        color=GRAY, va="center")
save(fig, "fig2-scene-flow.svg")

# ---- Figure 3: the four puzzle silhouettes (int[x, y]; 0 = cell to fill, -1 = outside the shape)


def container():
    return np.zeros((12, 6), int)


def chip():
    g = np.zeros((8, 8), int)
    for i in range(8):
        if i not in (2, 5):
            g[i, 0] = g[i, 7] = g[0, i] = g[7, i] = -1
    return g


def oxygen():
    g = np.zeros((10, 8), int)
    for i in (0, 9):
        g[i, [0, 1, 6, 7]] = -1
    for i in (4, 5):
        g[i, [j for j in range(8) if j not in (3, 4)]] = -1
    return g


def timer():
    g = np.zeros((10, 12), int)
    for x, y in ((1, 1), (6, 1), (1, 7), (6, 7)):
        for dx, dy in ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (1, 3), (0, 3), (0, 2), (0, 1)):
            g[x + dx, y + dy] = -1
    return g


shapes = [("(a) Container", container()), ("(b) Chip", chip()), ("(c) Oxygen", oxygen()), ("(d) Timer", timer())]
fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.35), gridspec_kw={"width_ratios": [12, 8, 10, 10]})
for ax, (t, g) in zip(axes, shapes):
    m = g.T  # rows = y (downwards), columns = x
    ny, nx = m.shape
    for y in range(ny):
        for x in range(nx):
            if m[y, x] == 0:
                ax.add_patch(plt.Rectangle((x, y), 1, 1, fc="#e3eaf3", ec=C[0], lw=0.5))
    ax.add_patch(plt.Rectangle((0, 0), nx, ny, fc="none", ec=GRAY, lw=0.5, ls=":"))
    ax.set_xlim(-0.3, nx + 0.3)
    ax.set_ylim(12.3, -0.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(t, fontsize=9)
    ax.text(nx / 2, ny + 1.1, f"{nx} x {ny} grid, {int((g == 0).sum())} cells", ha="center", va="center",
            fontsize=7, color="#4d4d4d")
fig.tight_layout(w_pad=1.0)
save(fig, "fig3-silhouettes.svg")
for t, g in shapes:
    print(f"{t}: grid {g.shape[0]}x{g.shape[1]}, cells to fill {(g == 0).sum()}")

# ---- Figure 4: runner obstacles and the distance budget
# GameManager.cs: speed = min(2.5 + t_hype / 8, 10), metres/s = 3 + speed / 2, bomb timer 111 s,
# distance to run = 7 * puzzle score; John.cs: a collision multiplies t_hype by a per-obstacle factor.
SPEED0, BOMB, FPS = 2.5, 111.0, 60


def run(score, hits=(), factor=0.5):
    """Frame-by-frame replay of GameManager.Update; returns times, metres covered, finish time."""
    hype, left, t, ts, ds, done = 0.0, 7.0 * score, 0.0, [0.0], [0.0], None
    hits = sorted(hits)
    while t < BOMB:
        dt = 1 / FPS
        speed = min(SPEED0 + hype / 8, 10.0)
        hype += dt
        t += dt
        left -= dt * (3 + speed / 2)
        while hits and t >= hits[0]:
            hype *= factor
            hits.pop(0)
        ts.append(t)
        ds.append(7.0 * score - left)
        if done is None and left <= 0:
            done = t
    return np.array(ts), np.array(ds), done


fig = plt.figure(figsize=(7.2, 2.9))
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.25], wspace=0.25)
sub = gs[0].subgridspec(2, 4, hspace=1.0, wspace=0.45)
sprites = [("Files/run_cycle_48x48.png", "John", "Space: jump", (0, 48)),
           ("Files/WoodenBox (1).png", "Box", "$\\times$0.5", None), ("Files/Tuberia.png", "Pipes", "$\\times$0.3", None),
           ("Files/DownPipe (1).png", "Down", "$\\times$0.1", None),
           ("Files/bulkhead-walls-platform.png", "Stairs", "$\\times$0.05", None),
           ("Files/LargeDownPipes.png", "HighPipe", "removed", None),
           ("Files/bulkhead-walls-platform (1).png", "HighChains", "removed", None)]
for k, (p, name, eff, crop) in enumerate(sprites):
    ax = fig.add_subplot(sub[k // 4, k % 4])
    a = img(A / p)
    if crop:
        a = a[:, crop[0]:crop[1]]
    ys, xs_ = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs_.min():xs_.max() + 1]
    ax.imshow(a, interpolation="nearest")
    ax.axis("off")
    ax.set_title(name, fontsize=7.5, pad=2)
    ax.text(0.5, -0.12, eff, transform=ax.transAxes, ha="center", va="top", fontsize=7,
            color=C[1] if eff.startswith("$") else "#4d4d4d")
fig.text(0.02, 0.97, "(a) Player and obstacles", fontsize=10, va="top")

ax = fig.add_subplot(gs[1])
t0, d0, _ = run(100)
t1, d1, _ = run(100, hits=np.arange(10, BOMB, 10))
ax.plot(t0, d0, color=C[0], label="no collisions")
ax.plot(t1, d1, color=C[0], ls="--", lw=1, label="a Box every 10 s")
for s, c in ((25, C[2]), (50, C[4]), (75, C[3]), (100, C[1])):
    ax.axhline(7 * s, color=c, lw=0.7, ls=":")
    ax.text(3, 7 * s + 12, f"score {s}: {7 * s} m", fontsize=7, color=c)
ax.axvline(BOMB, color=INK, lw=0.7)
ax.text(BOMB + 1.2, 400, "bomb timer, 111 s", rotation=90, ha="left", va="center", fontsize=7)
ax.set_xlim(0, 119)
ax.set_ylim(0, 820)
ax.set_xlabel("time in the runner [s]")
ax.set_ylabel("distance covered [m]")
ax.set_title("(b) Distance budget")
ax.legend(loc="lower right", bbox_to_anchor=(0.9, 0.02))
save(fig, "fig4-runner.svg")

print(f"max distance in {BOMB:.0f} s without collisions: {d0[-1]:.1f} m; with a Box every 10 s: {d1[-1]:.1f} m")
for s in (25, 50, 75, 100):
    print(f"score {s:3d}: {7 * s} m, finished at {run(s)[2]:.1f} s (no collisions), "
          f"{run(s, hits=np.arange(10, BOMB, 10))[2] or float('nan'):.1f} s (Box every 10 s)")
