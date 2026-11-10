"""Core data structures shared by every module."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Parcel:
    """A single parcel waiting at the depot.

    Attributes:
        parcel_id:   Unique identifier, e.g. ``"P001"``.
        destination: Name of the delivery point (graph node).
        weight:      Weight in kg (positive integer, needed by the DP table).
        value:       Benefit score of delivering this parcel on this trip
                     (higher = more important / more profitable).
        deadline:    Latest acceptable delivery time, in hours after the start.
        priority:    1 (low), 2 (normal) or 3 (high).
    """

    parcel_id: str
    destination: str
    weight: int
    value: int
    deadline: float
    priority: int = 1

    def __post_init__(self) -> None:
        if self.weight <= 0:
            raise ValueError(f"{self.parcel_id}: weight must be a positive integer")
        if self.value < 0:
            raise ValueError(f"{self.parcel_id}: value must not be negative")
        if self.priority not in (1, 2, 3):
            raise ValueError(f"{self.parcel_id}: priority must be 1, 2 or 3")


@dataclass
class Dataset:
    """Everything needed to run one planning scenario."""

    name: str
    depot: str
    vehicle_capacity: int
    coordinates: dict[str, tuple[float, float]]
    edges: list[tuple[str, str, float]]
    parcels: list[Parcel] = field(default_factory=list)
