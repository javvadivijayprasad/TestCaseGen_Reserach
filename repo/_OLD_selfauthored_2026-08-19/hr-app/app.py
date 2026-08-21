"""Minimal HR reference application used as a mutation-testing target.

Intentionally small but semantically rich so that mutations land on
branches that the generated tests are expected to cover.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Employee:
    id: int
    email: str
    full_name: str
    employment_type: str = "full_time"
    role: str = "employee"


@dataclass
class LeaveRequest:
    id: int
    employee_id: int
    start_date: str  # ISO date
    end_date: str
    days: int
    state: str = "pending"


@dataclass
class Timesheet:
    id: int
    employee_id: int
    week_start: str
    per_day_hours: list[float]  # length 7
    state: str = "draft"


class HRApp:
    """In-memory reference HR service."""

    def __init__(self) -> None:
        self.employees: dict[int, Employee] = {}
        self.leave_requests: dict[int, LeaveRequest] = {}
        self.timesheets: dict[int, Timesheet] = {}
        self.audit: list[dict[str, Any]] = []
        self._next_id = 1

    # ---------- Employees ----------
    def create_employee(self, email: str, full_name: str,
                        employment_type: str = "full_time",
                        role: str = "employee") -> Employee:
        if not email or "@" not in email:
            raise ValueError("invalid email")
        if not full_name:
            raise ValueError("full_name required")
        if employment_type not in ("full_time", "part_time", "contractor"):
            raise ValueError("invalid employment_type")
        emp = Employee(id=self._next_id, email=email, full_name=full_name,
                       employment_type=employment_type, role=role)
        self.employees[emp.id] = emp
        self._next_id += 1
        self.audit.append({"action": "employee.create", "id": emp.id})
        return emp

    def delete_employee(self, employee_id: int, actor_role: str) -> bool:
        if actor_role not in ("hr-admin", "admin"):
            raise PermissionError("role forbidden")
        if employee_id not in self.employees:
            return False
        del self.employees[employee_id]
        self.audit.append({"action": "employee.delete", "id": employee_id})
        return True

    # ---------- Leave requests ----------
    def submit_leave(self, employee_id: int, start_date: str, end_date: str,
                     days: int) -> LeaveRequest:
        if employee_id not in self.employees:
            raise ValueError("unknown employee")
        if start_date > end_date:
            raise ValueError("start_date after end_date")
        if days < 1:
            raise ValueError("days must be >= 1")
        if days > 30:
            raise ValueError("days > 30 requires hr-admin approval path")
        # overlap detection
        for lr in self.leave_requests.values():
            if lr.employee_id != employee_id or lr.state == "rejected":
                continue
            if not (end_date < lr.start_date or start_date > lr.end_date):
                raise ValueError("overlapping existing leave")
        lr = LeaveRequest(id=self._next_id, employee_id=employee_id,
                          start_date=start_date, end_date=end_date, days=days)
        self.leave_requests[lr.id] = lr
        self._next_id += 1
        self.audit.append({"action": "leave.submit", "id": lr.id})
        return lr

    def approve_leave(self, request_id: int, manager_id: int) -> LeaveRequest:
        if request_id not in self.leave_requests:
            raise KeyError("unknown request")
        lr = self.leave_requests[request_id]
        if lr.state != "pending":
            raise ValueError("already actioned")
        lr.state = "approved"
        self.audit.append({"action": "leave.approve", "id": request_id,
                           "by": manager_id})
        return lr

    # ---------- Timesheets ----------
    def submit_timesheet(self, employee_id: int, week_start: str,
                         per_day_hours: list[float]) -> Timesheet:
        if len(per_day_hours) != 7:
            raise ValueError("expected 7 day entries")
        for h in per_day_hours:
            if h < 0 or h > 24:
                raise ValueError("per-day hours outside 0..24")
        total = sum(per_day_hours)
        if total < 0 or total > 80:
            raise ValueError("weekly total outside 0..80")
        ts = Timesheet(id=self._next_id, employee_id=employee_id,
                       week_start=week_start, per_day_hours=list(per_day_hours),
                       state="submitted")
        self.timesheets[ts.id] = ts
        self._next_id += 1
        self.audit.append({"action": "timesheet.submit", "id": ts.id})
        return ts

    # ---------- Password policy (pure function, exercised by tests) ----------
    @staticmethod
    def password_ok(pw: str) -> bool:
        if len(pw) < 10:
            return False
        if not any(c.isupper() for c in pw):
            return False
        if not any(c.isdigit() for c in pw):
            return False
        if not any(c in "!@#$%^&*()_-+=[]{}" for c in pw):
            return False
        return True
