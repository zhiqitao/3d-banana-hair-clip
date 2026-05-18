# Print Failure Report

**Printer:** Bambu Lab P1S
**Material:** PETG, generic brand
**Nozzle:** 0.4 mm hardened steel
**Layer height:** 0.20 mm
**Walls:** 3
**Infill:** 40% gyroid
**Bed temp:** 70°C, nozzle 240°C
**Orientation:** Arms flat (spine down), pin upright, cotter flat

---

## Problem 1 — Pin cannot be inserted

The nominal pin (`hinge_pin.stl`) cannot be inserted into the hinge barrels by hand.
Significant force with a mallet was needed, and even then the pin only went halfway.
The pin tip is visibly bulging the barrel walls.

**Measurement:** Barrel bore measured with digital caliper: 3.72 mm.
Pin outside diameter measured: 3.84 mm.
Interference: ~0.12 mm, making hand insertion impossible.

**Impact:** The clip is currently non-functional. The loose pin variant was substituted
and inserts with moderate thumb pressure, but wobbles noticeably.

---

## Problem 2 — Teeth scrape against opposite arm on close

When the arms are brought together, the teeth on the left arm scrape audibly against
the right arm body (not the slots). The teeth are catching on the slot-side face
rather than dropping cleanly into the slots.

**Observation:** The scrape is worst in the first 5 mm of closing travel. After
forcing past it, the arms close but the scraping leaves visible scratch marks.

**Measurement:** Slot mouth measured at 0.71 mm. Tooth width measured at 0.84 mm.
The tooth root is slightly wider than the slot mouth.

**Impact:** Cannot close the clip smoothly. Fine PETG stringing inside slots may
be making this worse, but the root clearance geometry appears insufficient.

---

## Problem 3 — Hinge wobbles after 20 cycles

After approximately 20 open/close cycles, the hinge developed lateral play of
roughly 1 mm when the arms are loaded sideways. The cotter and pin are still in
place and intact.

**Observation:** The barrel axial gap appears to have worn. Under light finger
pressure, the left arm shifts ~1 mm in the Y-direction relative to the right arm.

**Hypothesis:** The knuckle gap between barrel faces was tight enough to bind
initially, causing micro-wear. The barrels are now too loose for a stable hinge.

**Impact:** The clip still opens and closes, but the lateral wobble is noticeable
during wear and makes the clip feel cheap.

---

## Problem 4 — Hook ends do not catch reliably

The hook at the tip of each arm is intended to interlock with the opposite arm's
hook when closed, providing a positive closing latch.

In practice, the hooks slide past each other roughly 40% of the time, requiring
a deliberate squeeze-and-twist motion to engage them. The clip will not stay
closed under the elastic tension of a hair bun without the hooks engaged.

**Observation:** The hook sweep angle appears too shallow — the hook tip does not
curl far enough inward to catch the opposite arm.

**Measurement:** The hook opens outward at the tip instead of pointing inward.
The hook inner radius appears larger than expected.

---

## Summary table

| # | Problem | Severity | Currently printable? |
|---|---|---|---|
| 1 | Pin cannot insert | Critical | No (substituted loose pin) |
| 2 | Teeth scrape on close | High | Functional but damaged |
| 3 | Hinge wobble after 20 cycles | Medium | Functional but poor feel |
| 4 | Hook does not latch reliably | High | Functional with care |
