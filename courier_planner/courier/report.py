"""Plain-text report for the console and for the written submission."""

from __future__ import annotations

from .planner import TripPlan


def format_trip(trip: TripPlan, show_table: bool = False) -> str:
    """Return a readable summary of one trip."""
    ks = trip.knapsack
    lines: list[str] = []
    add = lines.append

    add("=" * 72)
    add(f"TRIP {trip.trip_number}  (departs at t = {trip.start_time:.2f} h)")
    add("=" * 72)

    add("\n[1] Parcels sorted by urgency (deadline -> priority -> weight)")
    add(f"    {'ID':<7}{'Dest':<7}{'Wt':>4}{'Value':>7}{'Deadline':>10}{'Prio':>6}")
    for p in trip.queue:
        add(f"    {p.parcel_id:<7}{p.destination:<7}{p.weight:>4}{p.value:>7}{p.deadline:>10.1f}{p.priority:>6}")

    add(f"\n[2] Knapsack selection (capacity {ks.capacity} kg)")
    add(f"    Loaded : {', '.join(p.parcel_id for p in ks.selected) or '-'}")
    add(f"    Weight : {ks.total_weight} / {ks.capacity} kg")
    add(f"    Value  : {ks.total_value}")

    add("\n[3] Delivery route (Dijkstra legs + nearest-neighbour order)")
    add(f"    Stop order : {' -> '.join([trip.route.depot, *trip.route.stops, trip.route.depot])}")
    for leg in trip.route.legs:
        add(f"    {leg.start:>6} -> {leg.end:<6} {leg.distance:6.1f} km   via {' > '.join(leg.path)}")
    add(f"    Full path  : {' > '.join(trip.route.full_path)}")
    add(f"    Route length: {trip.route.total_distance:.1f} km   Duration: {trip.duration_hours:.2f} h")

    add("\n[4] Expected deliveries")
    add(f"    {'ID':<7}{'Dest':<7}{'ETA (h)':>9}{'Deadline':>10}  Status")
    for d in trip.deliveries:
        status = "on time" if d.on_time else "LATE"
        add(f"    {d.parcel.parcel_id:<7}{d.parcel.destination:<7}{d.arrival_hours:>9.2f}"
            f"{d.parcel.deadline:>10.1f}  {status}")

    add("\n[5] Stage runtimes")
    for stage, seconds in trip.timings.items():
        add(f"    {stage:<10}{seconds * 1000:>10.3f} ms")

    if show_table:
        from .knapsack import format_table
        add("\n[6] Knapsack DP table")
        add(format_table(trip.queue, ks))

    return "\n".join(lines)
