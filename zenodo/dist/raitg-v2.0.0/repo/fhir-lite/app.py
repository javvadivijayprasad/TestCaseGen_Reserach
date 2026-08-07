"""Minimal FHIR-lite reference app used as a mutation-testing target."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Patient:
    id: int
    family_name: str
    given_name: str
    birth_date: str  # ISO YYYY-MM-DD
    deleted: bool = False
    history: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Encounter:
    id: int
    patient_id: int
    start_iso: str
    end_iso: str | None = None
    status: str = "in-progress"  # in-progress | finished


@dataclass
class Observation:
    id: int
    patient_id: int
    code: str  # LOINC
    value: float
    flagged: bool = False


class FHIRLite:
    """Tiny in-memory FHIR-shaped service."""

    def __init__(self) -> None:
        self.patients: dict[int, Patient] = {}
        self.encounters: dict[int, Encounter] = {}
        self.observations: dict[int, Observation] = {}
        self.audit: list[dict[str, Any]] = []
        self._next_id = 1

    # ---------- Patient ----------
    def create_patient(self, family_name: str, given_name: str,
                       birth_date: str, role: str) -> Patient:
        if role not in ("clinician", "admin"):
            raise PermissionError("role forbidden")
        if not family_name or not given_name:
            raise ValueError("name required")
        try:
            datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError("invalid birth_date") from e
        p = Patient(id=self._next_id, family_name=family_name,
                    given_name=given_name, birth_date=birth_date)
        self.patients[p.id] = p
        self._next_id += 1
        self._audit("Patient.create", p.id, role)
        return p

    def read_patient(self, patient_id: int, role: str,
                     assigned_patient_ids: set[int]) -> Patient:
        if role != "clinician":
            raise PermissionError("only clinicians")
        if patient_id not in assigned_patient_ids:
            raise PermissionError("not assigned")
        p = self.patients.get(patient_id)
        if not p or p.deleted:
            raise KeyError("not found")
        self._audit("Patient.read", patient_id, role)
        return p

    def soft_delete_patient(self, patient_id: int, role: str) -> bool:
        if role != "admin":
            raise PermissionError("admin only")
        p = self.patients.get(patient_id)
        if not p:
            return False
        p.deleted = True
        self._audit("Patient.delete", patient_id, role)
        return True

    # ---------- Encounter ----------
    def create_encounter(self, patient_id: int, start_iso: str,
                         end_iso: str | None, role: str) -> Encounter:
        if role != "clinician":
            raise PermissionError("only clinicians")
        if patient_id not in self.patients:
            raise KeyError("unknown patient")
        if end_iso is not None and end_iso < start_iso:
            raise ValueError("end before start")
        e = Encounter(id=self._next_id, patient_id=patient_id,
                      start_iso=start_iso, end_iso=end_iso)
        self.encounters[e.id] = e
        self._next_id += 1
        return e

    def close_encounter(self, encounter_id: int) -> Encounter:
        e = self.encounters.get(encounter_id)
        if not e:
            raise KeyError("unknown encounter")
        if e.status == "finished":
            raise ValueError("already finished")
        e.status = "finished"
        return e

    # ---------- Observation ----------
    def create_observation(self, patient_id: int, code: str, value: float,
                           role: str) -> Observation:
        if role != "clinician":
            raise PermissionError("only clinicians")
        if patient_id not in self.patients:
            raise KeyError("unknown patient")
        if not code:
            raise ValueError("code required")
        flagged = self._is_out_of_range(code, value)
        o = Observation(id=self._next_id, patient_id=patient_id, code=code,
                        value=value, flagged=flagged)
        self.observations[o.id] = o
        self._next_id += 1
        return o

    @staticmethod
    def _is_out_of_range(code: str, value: float) -> bool:
        # Simple plausibility ranges for a few common LOINC codes
        ranges = {
            "8867-4": (30.0, 220.0),    # heart rate
            "8480-6": (70.0, 200.0),    # systolic BP
            "8462-4": (40.0, 130.0),    # diastolic BP
            "29463-7": (1.0, 400.0),    # body weight kg
            "8310-5": (32.0, 42.0),     # body temperature °C
        }
        lo, hi = ranges.get(code, (-1e18, 1e18))
        return value < lo or value > hi

    def _audit(self, action: str, resource_id: int, actor: str) -> None:
        self.audit.append({
            "action": action,
            "resource_id": resource_id,
            "actor": actor,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
