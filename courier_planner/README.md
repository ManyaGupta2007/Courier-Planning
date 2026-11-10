# Smart Courier Planner

An integrated Python prototype that, given a list of parcels and delivery points,
produces an **ordered delivery route** and an **optimised packing plan**.

| Stage | Algorithm | Module | Complexity |
|-------|-----------|--------|------------|
| Prioritise parcels | Merge sort (deadline -> priority -> weight) | `courier/sorting.py` | O(n log n) |
| Choose parcels for one trip | 0/1 knapsack, dynamic programming | `courier/knapsack.py` | O(n x W) |
| Shortest paths | Dijkstra with a binary heap | `courier/graph.py` | O((V+E) log V) |
| Order the stops | Nearest-neighbour TSP approximation | `courier/routing.py` | O(k (V+E) log V) |

## Pipeline

```
parcels.json --> merge sort --> knapsack DP --> delivery points --> Dijkstra distances
                 (urgency)      (what to load)   (unique stops)     + nearest-neighbour order
                                                                        |
                                                  route, ETA per parcel, runtimes, charts
```

## Project structure

```
courier_planner/
├── main.py                 # command-line application
├── benchmark.py            # Phase 4: runtime tests + charts
├── generate_datasets.py    # recreates data/medium.json and data/large.json
├── courier/
│   ├── models.py           # Parcel, Dataset
│   ├── dataset.py          # load / save / validate / generate datasets
│   ├── sorting.py          # merge, quick, insertion sort
│   ├── knapsack.py         # DP table + back-tracking
│   ├── graph.py            # Graph, Dijkstra, path reconstruction
│   ├── routing.py          # nearest-neighbour route
│   ├── planner.py          # integrates all stages, multi-trip planning
│   ├── report.py           # text report
│   └── visualization.py    # route picture
├── data/                   # small (10 parcels), medium (60), large (1000)
├── tests/                  # 18 unit tests
├── results/                # saved outputs, route pictures, runtime charts, CSV
└── docs/                   # design diagram and the PDF report
```

## Execution steps

```bash
pip install -r requirements.txt            # only matplotlib (for pictures/charts)

python main.py                             # small dataset, prints the full plan
python main.py --table --plot results/route_small.png
python main.py --dataset data/medium.json --plot results/route_medium.png
python main.py --dataset data/large.json --trips 3     # several trips until parcels run out

python benchmark.py                        # Phase 4 runtimes + charts in results/
python -m unittest discover -s tests -t .  # run the 18 tests
```

Options: `--capacity KG`, `--trips N`, `--speed KMH` (default 20), `--service HOURS` (default 0.1),
`--table` (print DP table), `--plot FILE.png`.

## Dataset format (JSON)

```json
{
  "name": "small", "depot": "Depot", "vehicle_capacity": 20,
  "nodes":   {"Depot": [50, 35], "A": [20, 72]},
  "edges":   [["Depot", "A", 4.0]],
  "parcels": [{"parcel_id": "P001", "destination": "A", "weight": 5,
               "value": 40, "deadline": 2.0, "priority": 3}]
}
```

`weight` is a positive integer (kg), `value` is the benefit score used by the knapsack,
`deadline` is in hours after departure, `priority` is 1-3, edge weights are km.

## Result on the small dataset (capacity 20 kg)

* Loaded: **P001, P003, P004** (20/20 kg, value 120)
* Stop order: **Depot -> A -> C -> D -> Depot**, full path `Depot > A > C > D > C > J > Depot`
* Route length **24.0 km**, 1.50 h, all three parcels on time

## Design decisions and limitations

* **Why merge sort?** Stable and O(n log n) worst case, so ties on deadline keep a predictable
  order. Quick sort and insertion sort are implemented only for the Phase 4 comparison.
* **Knapsack ignores route length.** The value is a fixed score; the loaded set is chosen by
  weight and value, then routed. A parcel can therefore be late if its stop is far away
  (visible in the medium/large outputs). Combining both objectives is future work.
* **Nearest neighbour is a heuristic**, not optimal. 2-opt improvement would shorten routes.
* **Dijkstra** assumes non-negative weights and re-runs once per stop (k runs); caching or
  all-pairs preprocessing would help for many trips.
* The DP table uses O(n x W) memory; a 1-D table is possible if the table is not needed as evidence.
