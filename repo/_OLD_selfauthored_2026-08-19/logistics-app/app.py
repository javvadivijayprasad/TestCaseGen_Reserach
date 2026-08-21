"""Minimal last-mile logistics reference application used as a mutation-testing target.

Intentionally small but semantically rich so that mutations land on
branches that the generated tests are expected to cover.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Shipment:
    id: int
    origin: str
    destination: str
    weight_kg: float
    length_cm: float
    width_cm: float
    height_cm: float
    hazmat: bool = False
    status: str = "created"
    driver_id: int | None = None


@dataclass
class Driver:
    id: int
    full_name: str
    license_class: str  # e.g. "B", "C", "C+haz"
    capacity_kg: float
    status: str = "available"


@dataclass
class DeliveryAttempt:
    id: int
    shipment_id: int
    timestamp: str  # ISO datetime
    outcome: str   # delivered | refused | damaged | wrong_address | no_response
    signature: str | None = None


class LogisticsApp:
    """In-memory reference logistics service."""

    _STATUS_TRANSITIONS = {
        "created": ("assigned", "cancelled"),
        "assigned": ("in_transit", "cancelled"),
        "in_transit": ("delivered", "failed"),
    }

    def __init__(self) -> None:
        self.shipments: dict[int, Shipment] = {}
        self.drivers: dict[int, Driver] = {}
        self.attempts: dict[int, DeliveryAttempt] = {}
        self.audit: list[dict[str, Any]] = []
        self._next_id = 1

    # ---------- Shipments ----------
    def create_shipment(self, origin: str, destination: str, weight_kg: float,
                        length_cm: float, width_cm: float, height_cm: float,
                        hazmat: bool = False) -> Shipment:
        if not origin or not destination:
            raise ValueError("origin and destination required")
        if origin == destination:
            raise ValueError("origin equals destination")
        if weight_kg <= 0 or weight_kg > 50:
            raise ValueError("weight_kg outside (0, 50]")
        for d in (length_cm, width_cm, height_cm):
            if d <= 0 or d > 200:
                raise ValueError("dimension outside (0, 200]")
        sh = Shipment(id=self._next_id, origin=origin, destination=destination,
                      weight_kg=weight_kg, length_cm=length_cm,
                      width_cm=width_cm, height_cm=height_cm, hazmat=hazmat)
        self.shipments[sh.id] = sh
        self._next_id += 1
        self.audit.append({"action": "shipment.create", "id": sh.id})
        return sh

    def cancel_shipment(self, shipment_id: int, actor_role: str) -> bool:
        if actor_role not in ("dispatcher", "admin"):
            raise PermissionError("role forbidden")
        if shipment_id not in self.shipments:
            return False
        sh = self.shipments[shipment_id]
        if sh.status not in ("created", "assigned"):
            raise ValueError("cannot cancel after in_transit")
        sh.status = "cancelled"
        self.audit.append({"action": "shipment.cancel", "id": shipment_id})
        return True

    # ---------- Drivers ----------
    def register_driver(self, full_name: str, license_class: str,
                        capacity_kg: float) -> Driver:
        if not full_name:
            raise ValueError("full_name required")
        if license_class not in ("B", "C", "C+haz"):
            raise ValueError("invalid license_class")
        if capacity_kg <= 0 or capacity_kg > 1000:
            raise ValueError("capacity_kg outside (0, 1000]")
        dr = Driver(id=self._next_id, full_name=full_name,
                    license_class=license_class, capacity_kg=capacity_kg)
        self.drivers[dr.id] = dr
        self._next_id += 1
        self.audit.append({"action": "driver.register", "id": dr.id})
        return dr

    def assign_driver(self, shipment_id: int, driver_id: int) -> Shipment:
        if shipment_id not in self.shipments:
            raise KeyError("unknown shipment")
        if driver_id not in self.drivers:
            raise KeyError("unknown driver")
        sh = self.shipments[shipment_id]
        dr = self.drivers[driver_id]
        if sh.status != "created":
            raise ValueError("shipment not in 'created' state")
        if dr.status != "available":
            raise ValueError("driver not available")
        if sh.weight_kg > dr.capacity_kg:
            raise ValueError("driver capacity insufficient")
        if sh.hazmat and dr.license_class != "C+haz":
            raise ValueError("hazmat requires C+haz license")
        sh.driver_id = driver_id
        sh.status = "assigned"
        dr.status = "engaged"
        self.audit.append({"action": "shipment.assign", "id": shipment_id,
                           "driver": driver_id})
        return sh

    # ---------- Delivery ----------
    def confirm_delivery(self, shipment_id: int, timestamp: str,
                         signature: str) -> DeliveryAttempt:
        if shipment_id not in self.shipments:
            raise KeyError("unknown shipment")
        sh = self.shipments[shipment_id]
        if sh.status != "in_transit":
            raise ValueError("shipment not in_transit")
        if not signature or len(signature) < 2:
            raise ValueError("signature required (>=2 chars)")
        att = DeliveryAttempt(id=self._next_id, shipment_id=shipment_id,
                              timestamp=timestamp, outcome="delivered",
                              signature=signature)
        self.attempts[att.id] = att
        sh.status = "delivered"
        if sh.driver_id is not None:
            self.drivers[sh.driver_id].status = "available"
        self._next_id += 1
        self.audit.append({"action": "delivery.confirm", "id": att.id})
        return att

    def report_exception(self, shipment_id: int, timestamp: str,
                         outcome: str) -> DeliveryAttempt:
        if outcome not in ("refused", "damaged", "wrong_address",
                           "no_response"):
            raise ValueError("invalid exception outcome")
        if shipment_id not in self.shipments:
            raise KeyError("unknown shipment")
        sh = self.shipments[shipment_id]
        if sh.status != "in_transit":
            raise ValueError("shipment not in_transit")
        att = DeliveryAttempt(id=self._next_id, shipment_id=shipment_id,
                              timestamp=timestamp, outcome=outcome)
        self.attempts[att.id] = att
        sh.status = "failed"
        if sh.driver_id is not None:
            self.drivers[sh.driver_id].status = "available"
        self._next_id += 1
        self.audit.append({"action": "delivery.exception", "id": att.id,
                           "outcome": outcome})
        return att

    # ---------- Pure helpers (exercised by tests) ----------
    @staticmethod
    def is_dimension_ok(length_cm: float, width_cm: float,
                        height_cm: float) -> bool:
        for d in (length_cm, width_cm, height_cm):
            if d <= 0 or d > 200:
                return False
        return True

    @staticmethod
    def shipping_fee(weight_kg: float, hazmat: bool = False) -> float:
        if weight_kg <= 0:
            raise ValueError("weight_kg must be positive")
        base = 5.0
        per_kg = 2.5
        fee = base + per_kg * weight_kg
        if hazmat:
            fee += 15.0
        return round(fee, 2)
