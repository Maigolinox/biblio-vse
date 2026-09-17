# Test protocol — fines module

| Test Case: | TC-MUL-001 |
|---|---|
| Requirement | RF_08 — Calculate late fine |
| Environment: | Integration server, test database |

**Steps:**
1. Register a loan with due date 2026-03-01.
2. Register the return on 2026-03-04.
3. Look up the fine generated for the loan.

**Expected Result:** the fine is 3 days times the current daily rate and remains in pending status.

| Test Case: | TC-MUL-002 |
|---|---|
| Requirement | RF_08 — Calculate late fine |
| Environment: | Integration server, test database |

**Steps:**
1. Register a loan with due date 2026-03-01.
2. Register the return on 2026-02-28.

**Expected Result:** no fine is generated for the loan.
