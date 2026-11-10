"""Build docs/Capstone_Report.pdf from the saved results (needs reportlab + matplotlib).

Run from the project root:  python docs/build_report.py
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (CondPageBreak, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

R, D = Path("results"), Path("docs")
styles = getSampleStyleSheet()
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10, leading=14)
caption = ParagraphStyle("caption", parent=body, fontSize=8.5, leading=11,
                         textColor=colors.HexColor("#555555"))
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=2)


def terminal_png(lines, path, fontsize=7.2):
    """Render console text as a dark terminal-style picture (output trace)."""
    width = max(len(l) for l in lines)
    fig = plt.figure(figsize=(max(5, width * 0.062), len(lines) * 0.122 + 0.3), facecolor="#1e1e1e")
    fig.text(0.01, 0.99, "\n".join(lines), family="monospace", fontsize=fontsize,
             color="#d4d4d4", va="top", ha="left", linespacing=1.25)
    fig.savefig(path, dpi=200, facecolor="#1e1e1e")
    plt.close(fig)


def pic(path, width_cm):
    from PIL import Image as PILImage
    w, h = PILImage.open(path).size
    return Image(str(path), width=width_cm * cm, height=width_cm * cm * h / w)


def bullets(items):
    return [Paragraph(t, bullet, bulletText="•") for t in items]


def table(data, widths, header=True):
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    style = [("FONTSIZE", (0, 0), (-1, -1), 8.5), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
             ("VALIGN", (0, 0), (-1, -1), "TOP")]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe7f3")),
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


# ---- terminal-style output traces from the real program output -------------------------------
small_out = (R / "output_small.txt").read_text().splitlines()
medium_out = (R / "output_medium.txt").read_text().splitlines()
cut = next(i for i, l in enumerate(small_out) if l.startswith("[6]"))
terminal_png(small_out[:cut], D / "trace_small.png")
terminal_png([l for l in small_out[cut:] if l.strip() and not l.startswith("Route picture")],
             D / "trace_table.png", fontsize=6.4)
m_cut = next(i for i, l in enumerate(medium_out) if l.startswith("[3]"))
terminal_png([l[:96] + (" ..." if len(l) > 96 else "") for l in medium_out[:1] + medium_out[m_cut:m_cut + 6] + ["    ..."] +
             [l for l in medium_out if l.startswith("    Route length")]], D / "trace_medium.png")

story = []
H1, H2 = styles["Heading1"], styles["Heading2"]

# ---- title -----------------------------------------------------------------------------------
story += [Paragraph("Smart Courier Planner", styles["Title"]),
          Paragraph("Capstone Project: Sorting, Dynamic Programming, Graph Algorithms and Approximation",
                    styles["Heading3"]),
          Paragraph("Name: ____________________ &nbsp;&nbsp; Student ID: ____________ &nbsp;&nbsp; "
                    "GitHub: https://github.com/&lt;you&gt;/courier_planner", body),
          Spacer(1, 10),
          Paragraph("This report describes an integrated Python prototype that, given parcels and "
                    "delivery points, produces a prioritised packing plan and an ordered delivery route. "
                    "It combines merge sort, 0/1 knapsack dynamic programming, Dijkstra's algorithm and a "
                    "nearest-neighbour TSP approximation, and compares the runtime of each component.", body),
          Spacer(1, 8)]

# ---- Phase 1 ---------------------------------------------------------------------------------
story += [Paragraph("Phase 1: Courier Problem Design and Planning", H1),
          Paragraph("<b>Problem.</b> A courier vehicle with limited capacity leaves a depot. Many parcels are "
                    "waiting, each with a destination, weight, value, deadline and priority. The system must "
                    "(1) rank parcels by urgency, (2) pick the best set that fits in the vehicle, "
                    "(3) compute shortest distances over the road network and (4) order the stops into a short tour.", body),
          Spacer(1, 6), pic(D / "pipeline.png", 17), Spacer(1, 6),
          Paragraph("Parcel attributes", H2),
          table([["Attribute", "Meaning", "Used by"],
                 ["parcel_id", "Unique identifier", "all stages"],
                 ["destination", "Graph node where it is delivered", "routing"],
                 ["weight (kg, int)", "Space it consumes in the vehicle", "knapsack"],
                 ["value", "Benefit score of delivering it now", "knapsack"],
                 ["deadline (h)", "Latest acceptable delivery time", "sorting, on-time check"],
                 ["priority (1-3)", "Tie-breaker between equal deadlines", "sorting"]],
                [3.6, 8.4, 4.8]),
          Spacer(1, 8), Paragraph("Graph format", H2),
          Paragraph("An undirected weighted graph stored as an adjacency dictionary "
                    "<font face='Courier'>{node: {neighbour: km}}</font>. Datasets are JSON files with "
                    "<font face='Courier'>nodes</font> (coordinates, used only for drawing), "
                    "<font face='Courier'>edges</font> (u, v, km), <font face='Courier'>parcels</font>, "
                    "the <font face='Courier'>depot</font> and the <font face='Courier'>vehicle_capacity</font>. "
                    "Datasets are validated on load (unknown nodes, duplicate ids, bad weights).", body),
          Spacer(1, 6), CondPageBreak(6 * cm), Paragraph("Algorithm selection", H2),
          table([["Task", "Algorithm", "Why it fits", "Complexity"],
                 ["Prioritise parcels", "Merge sort", "Stable, guaranteed O(n log n); ties keep input order", "O(n log n)"],
                 ["Choose load", "0/1 knapsack DP", "Exact optimum; parcels cannot be split", "O(n·W)"],
                 ["Shortest paths", "Dijkstra + heap", "Non-negative road lengths", "O((V+E) log V)"],
                 ["Order stops", "Nearest neighbour", "TSP is NP-hard; fast heuristic", "O(k·(V+E) log V)"]],
                [3.0, 3.3, 7.2, 3.3]),
          PageBreak()]

# ---- Phase 2 ---------------------------------------------------------------------------------
story += [Paragraph("Phase 2: Package Prioritization and Box Filling", H1),
          Paragraph("<b>Sorting.</b> Parcels are sorted with a stable merge sort using the key "
                    "(deadline, -priority, weight): earliest deadline first, then highest priority, then lightest. "
                    "Quick sort and insertion sort are also implemented so the choice can be justified "
                    "experimentally in Phase 4 (merge sort was about 1.5x faster than quick sort and far "
                    "faster than insertion sort at 2000 parcels).", body),
          Paragraph("<b>Dynamic programming.</b> Let <font face='Courier'>T[i][w]</font> be the best value using the first i "
                    "sorted parcels with capacity w. "
                    "<font face='Courier'>T[i][w] = max(T[i-1][w], T[i-1][w-wt_i] + val_i)</font> when the parcel fits, "
                    "otherwise <font face='Courier'>T[i-1][w]</font>. Back-tracking from <font face='Courier'>T[n][W]</font> "
                    "recovers the chosen parcels; on equal values the more urgent parcel is preferred.", body),
          Spacer(1, 6),
          Paragraph("<b>Result (small dataset, capacity 20 kg).</b> Selected parcels: <b>P001, P003, P004</b>; "
                    "total weight 20/20 kg; total value <b>120</b>. Output trace (sorted list, selection, route):", body),
          Spacer(1, 4), pic(D / "trace_small.png", 15.5), Spacer(1, 6),
          Paragraph("DP table evidence (rows = parcels in sorted order, columns = capacity 0-20; "
                    "bottom-right cell = 120 = optimum):", body),
          Spacer(1, 4), pic(D / "trace_table.png", 16.5), PageBreak()]

# ---- Phase 3 ---------------------------------------------------------------------------------
story += [Paragraph("Phase 3: Route Maker and Graph Processing", H1),
          Paragraph("<b>Customer graph.</b> The depot, six delivery points (A-F) and one junction (J) are connected by "
                    "12 roads. Delivery points are not all directly connected, so the distance between two stops is the "
                    "Dijkstra shortest-path distance (for example D to Depot is 11 km via D > C > J > Depot, shorter than any "
                    "direct alternative).", body),
          Paragraph("<b>Nearest-neighbour TSP.</b> Starting at the depot, the vehicle repeatedly drives to the closest "
                    "unvisited stop (distance from Dijkstra), then returns to the depot. Ties are broken by name so "
                    "the result is deterministic.", body),
          Spacer(1, 6),
          table([["Leg", "Distance (km)", "Shortest path"],
                 ["Depot to A", "4.0", "Depot > A"], ["A to C", "6.0", "A > C"],
                 ["C to D", "3.0", "C > D"], ["D to Depot", "11.0", "D > C > J > Depot"],
                 ["<b>Total</b>", "<b>24.0</b>", "Depot > A > C > D > C > J > Depot"]],
                [4, 3.5, 9.3]),
          Spacer(1, 4),
          Paragraph("Expected arrival times use 20 km/h and 0.1 h service per stop: P001 at 0.20 h (deadline 2.0), "
                    "P003 at 0.60 h (2.5), P004 at 0.85 h (4.0); all on time. Total trip duration 1.50 h.", body),
          Spacer(1, 6), pic(R / "route_small.png", 11.5),
          Paragraph("Figure: final route. Green square = depot, numbered orange nodes = stops in visiting order.", caption),
          PageBreak()]

# ---- Phase 4 ---------------------------------------------------------------------------------
with open(R / "benchmark.csv", encoding="utf-8") as handle:
    bench = list(csv.DictReader(handle))
SHOWN = {("sorting", "1000"), ("sorting", "2000"), ("knapsack", "100"), ("knapsack", "800"),
         ("dijkstra", "100"), ("dijkstra", "800")}
runtime_rows = [[r["experiment"], r["algorithm"], r["size"], f"{float(r['seconds']) * 1000:.3f}"]
                for r in bench if (r["experiment"], r["size"]) in SHOWN]
story += [Paragraph("Phase 4: Performance Testing and Optimization", H1),
          Paragraph("<b>Test cases.</b> 18 unit tests (<font face='Courier'>python -m unittest discover -s tests -t .</font>) check "
                    "all sorting algorithms against Python's sorted(), the knapsack against brute force on 30 random "
                    "instances, Dijkstra on a hand-checked graph (including unreachable and invalid nodes), route "
                    "validity, capacity limits, and the known result of the small dataset. All pass.", body),
          Paragraph("<b>Datasets.</b> small (10 parcels, 8 nodes), medium (60 parcels, 30 nodes) and large "
                    "(1000 parcels, 150 nodes), the last two generated reproducibly with fixed random seeds. "
                    "Each measurement is the best of 3 runs.", body),
          Spacer(1, 6),
          pic(R / "chart_sorting.png", 11.5),
          Paragraph("Merge sort and quick sort grow almost linearly (O(n log n)); insertion sort grows quadratically "
                    "(about 97 ms at 2000 parcels vs 4 ms for merge sort). Built-in Timsort is fastest because it is C code.", caption),
          pic(R / "chart_pipeline.png", 12.5),
          Paragraph("Stage runtimes on the three datasets (log scale). On the large dataset the knapsack dominates "
                    "(about 26 ms), then routing (about 7 ms), then sorting (about 2 ms).", caption),
          PageBreak(),
          pic(R / "chart_knapsack.png", 11), pic(R / "chart_dijkstra.png", 11),
          Paragraph("The DP runtime grows linearly with the number of parcels for a fixed capacity (O(n·W)); "
                    "Dijkstra grows slightly more than linearly with the number of nodes, as expected for O((V+E) log V).", caption),
          Spacer(1, 6), Paragraph("Observed runtimes (ms)", H2),
          table([["Experiment", "Algorithm", "Size", "ms"]] + runtime_rows, [3, 6.5, 3.5, 3.2]),
          Spacer(1, 6), Paragraph("Suggested optimizations", H2)]
story += bullets([
    "<b>Knapsack memory/time:</b> use a 1-D table (O(W) memory) when the full table is not needed as evidence, "
    "or NumPy vectorisation to speed up the inner loop.",
    "<b>Dijkstra:</b> cache distances between stops across trips, or precompute all-pairs distances once for repeated planning.",
    "<b>Route quality:</b> apply 2-opt improvement on top of nearest neighbour to remove crossing legs.",
    "<b>Deadlines:</b> the knapsack uses a fixed value and ignores route length, so far-away parcels can be late "
    "(visible on the medium and large datasets). Including deadline penalties in the objective, or re-sorting stops "
    "by deadline, would address this.",
])
story.append(PageBreak())

# ---- Phase 5 ---------------------------------------------------------------------------------
story += [Paragraph("Phase 5: Final Report and Demonstration", H1),
          Paragraph("<b>Demonstration.</b> Run <font face='Courier'>python main.py</font> for the small scenario, or "
                    "<font face='Courier'>python main.py --dataset data/medium.json --plot results/route_medium.png</font>. "
                    "Output trace for the medium dataset (60 parcels, 80 kg vehicle), abbreviated:", body),
          Spacer(1, 4), pic(D / "trace_medium.png", 14), Spacer(1, 6),
          Paragraph("<b>Explanation of results.</b> On the small dataset the DP loads P001, P003 and P004. Although P008 has the "
                    "highest single value (50), taking P001 + P003 + P004 (value 120, 20 kg) beats every other combination "
                    "that fits, which a greedy choice by value would miss. The three loaded stops are A, C and D; Dijkstra finds "
                    "the 11 km return from D through C and J, and the 24 km tour meets every deadline.", body),
          Paragraph("<b>Limitations.</b> The route heuristic is not optimal; the knapsack ignores route length; "
                    "speed is a constant average; the road network is undirected with non-negative weights.", body),
          Paragraph("<b>How the repository is organised.</b>", body)]
story += bullets([
    "<font face='Courier'>courier/</font>: one module per algorithm plus planner, dataset and report helpers.",
    "<font face='Courier'>tests/</font>, <font face='Courier'>data/</font>, <font face='Courier'>results/</font>: unit tests, sample datasets, saved outputs and charts.",
    "<font face='Courier'>README.md</font>: installation, execution steps, dataset format, design decisions.",
])
story += [Spacer(1, 6),
          Paragraph("<b>Originality.</b> The implementation was written for this capstone; all algorithms are coded from scratch "
                    "(no routing or optimisation libraries). The only third-party package is matplotlib, used for charts.", body)]

doc = SimpleDocTemplate(str(D / "Capstone_Report.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Smart Courier Planner - Capstone Report")
doc.build(story)
print("Wrote docs/Capstone_Report.pdf")
