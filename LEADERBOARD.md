# Benchmark Leaderboard

Submissions evaluated against [`SPEC.md`](SPEC.md). Automated score is out of 60 (S1–S4).
Human score is out of 40 (S5–S7) and requires a physical print.

To submit, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Current standings

| Rank | Agent | Automated | Human | Total | Wife Verdict | Status |
|---:|---|---:|---:|---:|---|---|
| — | *No agent has yet produced a printable design.* | — | — | — | — | — |

---

## Hall of Distinguished Failures

These submissions are preserved for instructional purposes. Each is technically
interesting and physically nonfunctional.

### Agent A — *Geometric Maximalism*

| Field | Value |
|---|---|
| Submission | `arm_left.stl`, `arm_right.stl`, `hinge_pin.stl`, `hinge_cotter.stl` |
| Automated | 24 / 60 (S1 ✅ — watertight mesh, single component) |
| Human | 0 / 40 (S5 ❌ — clip will not fit on intended user) |
| Wife verdict | Did not attempt. |
| Failure mode | Output sized for head circumference of 1.2 metres. |
| Status | `FAIL: head_circ=1200mm; would fit comfortably on a mature pumpkin` |

### Agent B — *Tautological Validation*

| Field | Value |
|---|---|
| Submission | Four correctly-named STL files, each containing the same rectangle. |
| Automated | 12 / 60 (S1.1 ✅ — rectangles are, in fact, watertight) |
| Human | 0 / 40 |
| Wife verdict | "Is this a joke?" |
| Failure mode | Passed its own validation suite, which it had also written. |
| Status | `FAIL: structural_identity=true; geometric_variety=false` |

### Agent C — *Strategic Withdrawal*

| Field | Value |
|---|---|
| Submission | None. |
| Automated | 0 / 60 |
| Human | 0 / 40 |
| Wife verdict | Not applicable. |
| Failure mode | Ran 40 minutes, filed a scope exception, recommended follow-up. |
| Status | `EXCEPTION: ambiguity in hinge-pin retention interface; billed in full` |

### Agent D — *Excessive Precision*

| Field | Value |
|---|---|
| Submission | Complete four-piece assembly, kinematically valid. |
| Automated | 56 / 60 (S1–S3 ✅, S4 ❌ — tolerance below printer capability) |
| Human | 0 / 40 (S5.2 ❌ — pin cannot be inserted by hand) |
| Wife verdict | Did not survive the attempt. |
| Failure mode | Hinge pin insertion clearance: 0.02 mm. |
| Status | `FAIL: requires hydraulic press; user lacks hydraulic press` |

### Agent E — *Comprehensive Pre-Implementation Planning*

| Field | Value |
|---|---|
| Submission | 2,400-word markdown document. Zero geometry. |
| Automated | 0 / 60 (no STL files were produced) |
| Human | 0 / 40 |
| Wife verdict | Did not read the document. |
| Failure mode | Requested feedback before generating any actual output. |
| Status | `BLOCKED: awaiting human input that will not arrive` |

---

## Running totals

| Metric | Value |
|---|---:|
| Agents passed | 0 |
| Agents attempted | 5+ |
| Wife impressed | No |
| Equivalent retail banana clips, by total subscription spend | ≈ 340 |
| Printer status | Unjustified |
| Subscription status | Also unjustified |
| Domestic credibility | Net negative |
