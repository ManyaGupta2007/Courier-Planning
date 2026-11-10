"""Command-line entry point.

Examples:
    python main.py
    python main.py --dataset data/medium.json --table --plot results/route_medium.png
    python main.py --dataset data/large.json --trips 3
"""

from __future__ import annotations

import argparse
import sys

from courier.dataset import load_dataset
from courier.planner import plan_trips
from courier.report import format_trip


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart courier planning prototype")
    parser.add_argument("--dataset", default="data/small.json", help="path to a JSON dataset")
    parser.add_argument("--capacity", type=int, help="override the vehicle capacity (kg)")
    parser.add_argument("--trips", type=int, default=1, help="maximum number of trips to plan")
    parser.add_argument("--speed", type=float, default=20.0, help="average speed in km/h")
    parser.add_argument("--service", type=float, default=0.1, help="service time per stop (h)")
    parser.add_argument("--table", action="store_true", help="print the knapsack DP table")
    parser.add_argument("--plot", metavar="PNG", help="save a route picture of the first trip")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    dataset = load_dataset(args.dataset)
    trips = plan_trips(dataset, args.trips, args.capacity, args.speed, args.service)

    print(f"Dataset: {dataset.name} | parcels: {len(dataset.parcels)} | "
          f"nodes: {len(dataset.coordinates)} | capacity: {args.capacity or dataset.vehicle_capacity} kg")
    for trip in trips:
        print(format_trip(trip, show_table=args.table))

    if args.plot and trips:
        from courier.visualization import plot_route
        plot_route(dataset, trips[0], args.plot)
        print(f"\nRoute picture saved to {args.plot}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
