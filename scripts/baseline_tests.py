"""Comprehensive baseline tests for the three reference apps.

Self-contained: imports app.py from each repo and calls methods directly.
Used as the test suite for executable mutation testing in
mutation_exec_v2.py.

This version (v2) adds exact-boundary tests for every numeric
threshold in each app, plus per-operand boolean-or coverage, to
kill more mutations during executable mutation testing.
"""
from __future__ import annotations


# --------------------------------------------------------------- banking-api
def run_banking_tests(BankingAPI):
    api = BankingAPI()

    # ---- create_customer
    c1 = api.create_customer(verified=True, tier="standard")
    assert c1.id > 0 and c1.verified is True
    c2 = api.create_customer(verified=False, tier="premium")
    assert c2.tier == "premium" and c2.verified is False
    cP = api.create_customer(verified=True, tier="premium")
    # invalid tier
    try:
        api.create_customer(verified=True, tier="invalid_tier")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    # ---- open_checking: deposit-range BOUNDARIES
    # unverified — Or operand A
    try:
        api.open_checking(owner_id=c2.id, initial_deposit_cents=10000)
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass
    # unverified — Or operand B (unknown customer id)
    try:
        api.open_checking(owner_id=99999, initial_deposit_cents=10000)
        raise AssertionError("expected PermissionError (unknown)")
    except PermissionError:
        pass
    # below min: 2499 fails
    try:
        api.open_checking(owner_id=c1.id, initial_deposit_cents=2499)
        raise AssertionError("expected ValueError (below min)")
    except ValueError:
        pass
    # EXACT min: 2500 succeeds
    a_min = api.open_checking(owner_id=c1.id, initial_deposit_cents=2500)
    assert a_min.balance == 2500
    # EXACT max: 5_000_000 succeeds
    a_max = api.open_checking(owner_id=c1.id, initial_deposit_cents=5_000_000)
    assert a_max.balance == 5_000_000
    # above max: 5_000_001 fails
    try:
        api.open_checking(owner_id=c1.id, initial_deposit_cents=5_000_001)
        raise AssertionError("expected ValueError (above max)")
    except ValueError:
        pass
    a1 = api.open_checking(owner_id=c1.id, initial_deposit_cents=100_000)
    assert a1.kind == "checking" and a1.balance == 100_000

    # ---- open_savings: BOUNDARIES
    try:
        api.open_savings(owner_id=c1.id, initial_deposit_cents=9_999)
        raise AssertionError("expected ValueError (below 10k)")
    except ValueError:
        pass
    # EXACT min: 10_000 succeeds
    a_sav_min = api.open_savings(owner_id=c1.id, initial_deposit_cents=10_000)
    assert a_sav_min.balance == 10_000
    a2 = api.open_savings(owner_id=c1.id, initial_deposit_cents=50_000)
    assert a2.kind == "savings"
    # unverified
    try:
        api.open_savings(owner_id=c2.id, initial_deposit_cents=10_000)
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass
    # unknown customer
    try:
        api.open_savings(owner_id=99999, initial_deposit_cents=10_000)
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass

    # ---- transfer_internal: BOUNDARIES
    # need same-owner accounts; use existing
    src_balance = a1.balance
    a3 = api.open_checking(owner_id=c1.id, initial_deposit_cents=200_000)
    # negative amount
    try:
        api.transfer_internal(source_id=a1.id, target_id=a3.id,
                                amount_cents=-1)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    # ZERO amount fails (must be positive)
    try:
        api.transfer_internal(source_id=a1.id, target_id=a3.id,
                                amount_cents=0)
        raise AssertionError("expected ValueError (zero amount)")
    except ValueError:
        pass
    # positive transfer succeeds
    s, t = api.transfer_internal(source_id=a1.id, target_id=a3.id,
                                    amount_cents=50_000)
    assert s.balance == src_balance - 50_000 and t.balance == 250_000

    # daily limit boundary tests need a fresh customer
    cD = api.create_customer(verified=True, tier="standard")
    aD1 = api.open_checking(owner_id=cD.id, initial_deposit_cents=5_000_000)
    aD2 = api.open_checking(owner_id=cD.id, initial_deposit_cents=2500)
    # Transfer EXACTLY at daily limit = 2_500_000 cents = $25,000 succeeds
    api.transfer_internal(source_id=aD1.id, target_id=aD2.id,
                            amount_cents=2_500_000)
    # Now any additional > 0 should fail (1 cent over)
    try:
        api.transfer_internal(source_id=aD1.id, target_id=aD2.id,
                                amount_cents=1)
        raise AssertionError("expected ValueError (over daily)")
    except ValueError:
        pass

    # cross-owner transfer
    cE = api.create_customer(verified=True, tier="standard")
    aE = api.open_checking(owner_id=cE.id, initial_deposit_cents=10000)
    try:
        api.transfer_internal(source_id=a3.id, target_id=aE.id,
                                amount_cents=100)
        raise AssertionError("expected PermissionError (cross-owner)")
    except PermissionError:
        pass

    # unknown account in transfer
    try:
        api.transfer_internal(source_id=99999, target_id=a3.id,
                                amount_cents=100)
        raise AssertionError("expected KeyError (unknown src)")
    except KeyError:
        pass

    # ---- close_account: BOUNDARIES
    # non-zero balance fails
    try:
        api.close_account(account_id=a3.id)
        raise AssertionError("expected ValueError (nonzero)")
    except ValueError:
        pass
    # unknown account
    try:
        api.close_account(account_id=99999)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
    # close after draining to zero
    a_close = api.open_checking(owner_id=c1.id, initial_deposit_cents=2500)
    # drain
    a4 = api.open_checking(owner_id=c1.id, initial_deposit_cents=100_000)
    # transfer 2500 from a_close to a4
    api.transfer_internal(source_id=a_close.id, target_id=a4.id,
                            amount_cents=2500)
    closed = api.close_account(account_id=a_close.id)
    assert closed.status == "closed"

    # ---- savings_tier_rate_bps: EXACT boundaries
    # rate at 100_000 boundary: <100_000 -> 10; at 100_000 -> 50
    assert BankingAPI.savings_tier_rate_bps(99_999) == 10
    assert BankingAPI.savings_tier_rate_bps(100_000) == 50
    # 1_000_000 boundary
    assert BankingAPI.savings_tier_rate_bps(999_999) == 50
    assert BankingAPI.savings_tier_rate_bps(1_000_000) == 150
    # 10_000_000 boundary
    assert BankingAPI.savings_tier_rate_bps(9_999_999) == 150
    assert BankingAPI.savings_tier_rate_bps(10_000_000) == 250
    # mid-range and high
    assert BankingAPI.savings_tier_rate_bps(50_000) == 10
    assert BankingAPI.savings_tier_rate_bps(500_000) == 50
    assert BankingAPI.savings_tier_rate_bps(5_000_000) == 150
    assert BankingAPI.savings_tier_rate_bps(50_000_000) == 250

    # ---- transfer_recurring_schedule: BOUNDARIES
    # standard cap = 250_000; valid mid
    sched = api.transfer_recurring_schedule(customer_id=c1.id,
                                              amount_cents=100_000,
                                              frequency="monthly")
    assert sched["status"] == "scheduled"
    # EXACT cap standard: 250_000 succeeds, 250_001 fails
    sched_at = api.transfer_recurring_schedule(customer_id=c1.id,
                                                  amount_cents=250_000,
                                                  frequency="weekly")
    assert sched_at["amount_cents"] == 250_000
    try:
        api.transfer_recurring_schedule(customer_id=c1.id,
                                          amount_cents=250_001,
                                          frequency="weekly")
        raise AssertionError("expected ValueError (cap+1)")
    except ValueError:
        pass
    # zero amount fails
    try:
        api.transfer_recurring_schedule(customer_id=c1.id,
                                          amount_cents=0,
                                          frequency="weekly")
        raise AssertionError("expected ValueError (zero)")
    except ValueError:
        pass
    # premium cap = 1_000_000; EXACT
    sched_pcap = api.transfer_recurring_schedule(customer_id=cP.id,
                                                    amount_cents=1_000_000,
                                                    frequency="biweekly")
    assert sched_pcap["amount_cents"] == 1_000_000
    try:
        api.transfer_recurring_schedule(customer_id=cP.id,
                                          amount_cents=1_000_001,
                                          frequency="biweekly")
        raise AssertionError("expected ValueError (premium cap+1)")
    except ValueError:
        pass
    # frequency variants
    for freq in ("weekly", "biweekly", "monthly"):
        s = api.transfer_recurring_schedule(customer_id=c1.id,
                                              amount_cents=1_000,
                                              frequency=freq)
        assert s["frequency"] == freq
    try:
        api.transfer_recurring_schedule(customer_id=c1.id,
                                          amount_cents=10_000,
                                          frequency="annually")
        raise AssertionError("expected ValueError (frequency)")
    except ValueError:
        pass
    # unknown customer
    try:
        api.transfer_recurring_schedule(customer_id=99999,
                                          amount_cents=1_000,
                                          frequency="weekly")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


# --------------------------------------------------------------- fhir-lite
def run_fhir_tests(FHIRLite):
    api = FHIRLite()
    p = api.create_patient(family_name="Smith", given_name="Jane",
                             birth_date="1990-01-15", role="clinician")
    assert p.id > 0 and p.family_name == "Smith"
    # invalid role
    try:
        api.create_patient(family_name="X", given_name="Y",
                             birth_date="2000-01-01", role="patient")
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass
    # missing names: family
    try:
        api.create_patient(family_name="", given_name="Y",
                             birth_date="2000-01-01", role="admin")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    # missing names: given (test Or operand B)
    try:
        api.create_patient(family_name="X", given_name="",
                             birth_date="2000-01-01", role="admin")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    # invalid date
    try:
        api.create_patient(family_name="A", given_name="B",
                             birth_date="not-a-date", role="admin")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    p2 = api.create_patient(family_name="Doe", given_name="John",
                              birth_date="1985-05-10", role="admin")
    got = api.read_patient(patient_id=p2.id, role="clinician",
                             assigned_patient_ids={p2.id})
    assert got.id == p2.id
    try:
        api.read_patient(patient_id=p2.id, role="admin",
                          assigned_patient_ids={p2.id})
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass
    try:
        api.read_patient(patient_id=p2.id, role="clinician",
                          assigned_patient_ids=set())
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass
    # read of deleted patient
    api.soft_delete_patient(patient_id=p2.id, role="admin")
    try:
        api.read_patient(patient_id=p2.id, role="clinician",
                          assigned_patient_ids={p2.id})
        raise AssertionError("expected KeyError (deleted)")
    except KeyError:
        pass

    # soft_delete by non-admin
    try:
        api.soft_delete_patient(patient_id=p.id, role="clinician")
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass
    # soft_delete unknown
    assert api.soft_delete_patient(patient_id=99999, role="admin") is False

    # create_encounter
    e = api.create_encounter(patient_id=p.id, start_iso="2026-01-01T10:00:00",
                                end_iso="2026-01-01T11:00:00", role="clinician")
    assert e.status == "in-progress"
    # encounter end < start
    try:
        api.create_encounter(patient_id=p.id, start_iso="2026-01-02T10:00:00",
                                end_iso="2026-01-01T10:00:00", role="clinician")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    # encounter with end None (allowed)
    e_open = api.create_encounter(patient_id=p.id,
                                      start_iso="2026-01-03T10:00:00",
                                      end_iso=None, role="clinician")
    assert e_open.end_iso is None
    # unknown patient
    try:
        api.create_encounter(patient_id=99999,
                                start_iso="2026-01-01T10:00:00",
                                end_iso=None, role="clinician")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
    # non-clinician
    try:
        api.create_encounter(patient_id=p.id,
                                start_iso="2026-01-01T10:00:00",
                                end_iso=None, role="admin")
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass

    e2 = api.close_encounter(encounter_id=e.id)
    assert e2.status == "finished"
    try:
        api.close_encounter(encounter_id=e.id)
        raise AssertionError("expected ValueError (already finished)")
    except ValueError:
        pass
    try:
        api.close_encounter(encounter_id=99999)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass

    # ---- create_observation: BOUNDARIES
    o = api.create_observation(patient_id=p.id, code="8867-4",
                                  value=80.0, role="clinician")
    assert o.flagged is False
    o2 = api.create_observation(patient_id=p.id, code="8867-4",
                                   value=250.0, role="clinician")
    assert o2.flagged is True
    try:
        api.create_observation(patient_id=p.id, code="",
                                  value=80.0, role="clinician")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    try:
        api.create_observation(patient_id=99999, code="8867-4",
                                  value=80.0, role="clinician")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
    try:
        api.create_observation(patient_id=p.id, code="8867-4",
                                  value=80.0, role="admin")
        raise AssertionError("expected PermissionError")
    except PermissionError:
        pass

    # ---- _is_out_of_range: EXACT BOUNDARIES per code
    # Heart rate 8867-4: 30.0-220.0
    assert FHIRLite._is_out_of_range("8867-4", 30.0) is False
    assert FHIRLite._is_out_of_range("8867-4", 220.0) is False
    assert FHIRLite._is_out_of_range("8867-4", 29.9) is True
    assert FHIRLite._is_out_of_range("8867-4", 220.1) is True
    # Systolic BP 8480-6: 70.0-200.0
    assert FHIRLite._is_out_of_range("8480-6", 70.0) is False
    assert FHIRLite._is_out_of_range("8480-6", 200.0) is False
    assert FHIRLite._is_out_of_range("8480-6", 69.9) is True
    assert FHIRLite._is_out_of_range("8480-6", 200.1) is True
    # Diastolic BP 8462-4: 40.0-130.0
    assert FHIRLite._is_out_of_range("8462-4", 40.0) is False
    assert FHIRLite._is_out_of_range("8462-4", 130.0) is False
    assert FHIRLite._is_out_of_range("8462-4", 39.9) is True
    assert FHIRLite._is_out_of_range("8462-4", 130.1) is True
    # Body weight 29463-7: 1.0-400.0
    assert FHIRLite._is_out_of_range("29463-7", 1.0) is False
    assert FHIRLite._is_out_of_range("29463-7", 400.0) is False
    assert FHIRLite._is_out_of_range("29463-7", 0.9) is True
    assert FHIRLite._is_out_of_range("29463-7", 400.1) is True
    # Body temp 8310-5: 32.0-42.0
    assert FHIRLite._is_out_of_range("8310-5", 32.0) is False
    assert FHIRLite._is_out_of_range("8310-5", 42.0) is False
    assert FHIRLite._is_out_of_range("8310-5", 31.9) is True
    assert FHIRLite._is_out_of_range("8310-5", 42.1) is True
    # Unknown code: returns False
    assert FHIRLite._is_out_of_range("unknown-code", 999.0) is False
    assert FHIRLite._is_out_of_range("unknown-code", -999.0) is False


# --------------------------------------------------------------- hr-app
def run_hr_tests(*classes):
    Employee, LeaveRequest, Timesheet, HRApp = classes
    e = Employee(id=1, email="x@y.com", full_name="A B")
    assert e.id == 1 and e.role == "employee"
    app = HRApp()
    emp = app.create_employee(email="alice@example.com", full_name="Alice")
    assert emp.id > 0
    # invalid email (no @ — covers Or operand B)
    try:
        app.create_employee(email="no-at", full_name="X")
        raise AssertionError("ValueError expected")
    except ValueError:
        pass
    # invalid email (empty — covers Or operand A)
    try:
        app.create_employee(email="", full_name="X")
        raise AssertionError("ValueError expected (empty)")
    except ValueError:
        pass
    # missing full_name
    try:
        app.create_employee(email="x@y.com", full_name="")
        raise AssertionError("ValueError expected (no name)")
    except ValueError:
        pass
    # invalid employment_type
    try:
        app.create_employee(email="x@y", full_name="Y",
                              employment_type="freelance")
        raise AssertionError("ValueError expected")
    except ValueError:
        pass
    # valid employment types
    for et in ("full_time", "part_time", "contractor"):
        e_et = app.create_employee(email=f"u_{et}@y.com",
                                      full_name=f"U {et}",
                                      employment_type=et)
        assert e_et.employment_type == et

    # delete by non-admin
    try:
        app.delete_employee(employee_id=emp.id, actor_role="employee")
        raise AssertionError("PermissionError expected")
    except PermissionError:
        pass
    # delete by admin succeeds
    e_to_del = app.create_employee(email="del@y.com", full_name="ToDel")
    ok = app.delete_employee(employee_id=e_to_del.id, actor_role="admin")
    assert ok is True
    # delete unknown
    assert app.delete_employee(employee_id=99999, actor_role="admin") is False
    # delete by hr-admin (other allowed role)
    e_hr_del = app.create_employee(email="hrdel@y.com", full_name="HRDel")
    assert app.delete_employee(employee_id=e_hr_del.id,
                                  actor_role="hr-admin") is True

    # ---- submit_leave: BOUNDARIES
    lr1 = app.submit_leave(employee_id=emp.id, start_date="2026-02-01",
                              end_date="2026-02-03", days=3)
    # overlap
    try:
        app.submit_leave(employee_id=emp.id, start_date="2026-02-02",
                            end_date="2026-02-04", days=3)
        raise AssertionError("ValueError expected (overlap)")
    except ValueError:
        pass
    # start_date AFTER end_date
    try:
        app.submit_leave(employee_id=emp.id, start_date="2026-05-10",
                            end_date="2026-05-05", days=2)
        raise AssertionError("ValueError expected (start>end)")
    except ValueError:
        pass
    # days < 1
    try:
        app.submit_leave(employee_id=emp.id, start_date="2026-06-01",
                            end_date="2026-06-01", days=0)
        raise AssertionError("ValueError expected (days<1)")
    except ValueError:
        pass
    # days exactly 1 succeeds
    lr_min = app.submit_leave(employee_id=emp.id, start_date="2026-07-01",
                                 end_date="2026-07-01", days=1)
    assert lr_min.days == 1
    # days exactly 30 succeeds
    lr_30 = app.submit_leave(employee_id=emp.id, start_date="2026-08-01",
                                end_date="2026-08-30", days=30)
    assert lr_30.days == 30
    # days 31 fails
    try:
        app.submit_leave(employee_id=emp.id, start_date="2026-09-01",
                            end_date="2026-10-01", days=31)
        raise AssertionError("ValueError expected (>30)")
    except ValueError:
        pass
    # unknown employee
    try:
        app.submit_leave(employee_id=99999, start_date="2026-11-01",
                            end_date="2026-11-02", days=2)
        raise AssertionError("ValueError expected (unknown emp)")
    except ValueError:
        pass

    lr_pending = app.submit_leave(employee_id=emp.id,
                                     start_date="2026-12-01",
                                     end_date="2026-12-02", days=2)
    lr2 = app.approve_leave(request_id=lr_pending.id, manager_id=99)
    assert lr2.state == "approved"
    try:
        app.approve_leave(request_id=lr_pending.id, manager_id=99)
        raise AssertionError("ValueError expected (already actioned)")
    except ValueError:
        pass
    try:
        app.approve_leave(request_id=99999, manager_id=99)
        raise AssertionError("KeyError expected")
    except KeyError:
        pass

    # ---- submit_timesheet: BOUNDARIES
    # wrong length
    try:
        app.submit_timesheet(employee_id=emp.id, week_start="2026-01-01",
                                per_day_hours=[8.0]*6)
        raise AssertionError("ValueError expected (wrong length)")
    except ValueError:
        pass
    # 8 entries also fails
    try:
        app.submit_timesheet(employee_id=emp.id, week_start="2026-01-01",
                                per_day_hours=[8.0]*8)
        raise AssertionError("ValueError expected (>7)")
    except ValueError:
        pass
    # per-day at 24 succeeds
    ts_24 = app.submit_timesheet(employee_id=emp.id,
                                    week_start="2026-04-01",
                                    per_day_hours=[24.0] + [0.0]*6)
    assert ts_24.state == "submitted"
    # per-day at 0 succeeds
    ts_0 = app.submit_timesheet(employee_id=emp.id,
                                   week_start="2026-04-08",
                                   per_day_hours=[0.0]*7)
    assert ts_0.state == "submitted"
    # per-day > 24 fails
    try:
        app.submit_timesheet(employee_id=emp.id, week_start="2026-01-01",
                                per_day_hours=[8.0]*6 + [25.0])
        raise AssertionError("ValueError expected (>24h)")
    except ValueError:
        pass
    # per-day negative fails
    try:
        app.submit_timesheet(employee_id=emp.id, week_start="2026-01-01",
                                per_day_hours=[8.0]*6 + [-1.0])
        raise AssertionError("ValueError expected (negative)")
    except ValueError:
        pass
    # weekly total EXACTLY 80 succeeds
    ts_80 = app.submit_timesheet(employee_id=emp.id,
                                    week_start="2026-05-01",
                                    per_day_hours=[80.0/7]*7)
    assert ts_80.state == "submitted"
    # weekly > 80 fails
    try:
        app.submit_timesheet(employee_id=emp.id, week_start="2026-01-01",
                                per_day_hours=[15.0]*7)
        raise AssertionError("ValueError expected (>80h)")
    except ValueError:
        pass
    ts2 = app.submit_timesheet(employee_id=emp.id, week_start="2026-01-01",
                                 per_day_hours=[8.0]*5 + [0.0, 0.0])
    assert ts2.state == "submitted"

    # ---- password_ok: BOUNDARIES (length=10 exactly)
    assert HRApp.password_ok("Short1!Pw") is False   # 9 chars
    assert HRApp.password_ok("Exact10P1!") is True   # exactly 10
    assert HRApp.password_ok("longenoughpw1!") is False  # no upper
    assert HRApp.password_ok("LongEnoughPwNoSym1") is False  # no symbol
    assert HRApp.password_ok("LongEnoughPwNoDigit!") is False  # no digit
    assert HRApp.password_ok("ValidPassword1!") is True
    # Each symbol from the allowed set kills boolean-set mutations
    for s in "!@#$%^&*()_-+=[]{}":
        assert HRApp.password_ok(f"ValidPw1{s}") is True


def run_app(app_name, src_text):
    namespace = {}
    try:
        compile(src_text, "app.py", "exec")
    except SyntaxError:
        return False
    try:
        exec(src_text, namespace)
    except Exception:
        return False
    try:
        if app_name == "banking-api":
            run_banking_tests(namespace["BankingAPI"])
        elif app_name == "fhir-lite":
            run_fhir_tests(namespace["FHIRLite"])
        elif app_name == "hr-app":
            run_hr_tests(namespace["Employee"], namespace["LeaveRequest"],
                          namespace["Timesheet"], namespace["HRApp"])
        else:
            return False
        return True
    except Exception:
        return False


if __name__ == "__main__":
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent.parent
    for app in ["banking-api", "fhir-lite", "hr-app"]:
        src = (ROOT / "repo" / app / "app.py").read_text()
        ok = run_app(app, src)
        print(f"  {app:14s}: baseline {'PASS' if ok else 'FAIL'}")
