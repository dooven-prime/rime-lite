import PaperXL.CircularObservation

/-!
# Standard circular-defect interface for the C1 compression bridge

This module identifies the exact raw action required by the C1 fusion-log
compressor. It is deliberately separate from the arbitrary single-defect
`CircularEnvironment`: a rank-`n-1` defect need not fix every non-port site.
The cross-package M4-C representative-word theorem is not instantiated here.
-/

namespace PaperXL

variable {n m : Nat}

/-- The literal C1 defect moves port one into port zero and fixes all other
physical sites. Using the environment's ports avoids an implicit `Fin n`
numeral assumption before its bounds have been introduced. -/
def c1Defect (E : CircularEnvironment n m) (q : Fin n) : Fin n :=
  if q = E.port1 then E.port0 else q

/-- Exact physical-action hypotheses needed to compare a Paper XL environment
with the C1 `p,d` execution. The seed may be any injective placement. -/
structure C1Compatible (E : CircularEnvironment n m) : Prop where
  port0_val : E.port0.val = 0
  port1_val : E.port1.val = 1
  defect_eq : E.defect = c1Defect E

namespace C1Compatible

variable (E : CircularEnvironment n m) (h : C1Compatible E)
include h

omit h in
theorem move_p (q : Fin n) :
    CircularLogState.move E .p q = CircularLogState.rotate E q := rfl

theorem move_d (q : Fin n) :
    CircularLogState.move E .d q = c1Defect E q := by
  simp [CircularLogState.move, h.defect_eq]

omit h in
theorem step_p_site (s : CircularLogState n m) (i : Fin m) :
    (CircularLogState.step E s .p).site i =
      CircularLogState.rotate E (s.site i) := rfl

theorem step_d_site (s : CircularLogState n m) (i : Fin m) :
    (CircularLogState.step E s .d).site i = c1Defect E (s.site i) := by
  simp only [CircularLogState.step, CircularLogState.move, h.defect_eq]
  split_ifs <;> rfl

omit h in
theorem step_p_events (s : CircularLogState n m) :
    (CircularLogState.step E s .p).events = s.events := rfl

omit h in
/-- The log appends exactly one complete ordered port-membership code when
both ports contain atoms, independently of registered/selected policies. -/
theorem step_d_events (s : CircularLogState n m) :
    (CircularLogState.step E s .d).events =
      if CircularLogState.occupied s E.port0 &&
          CircularLogState.occupied s E.port1 then
        s.events ++ [CircularLogState.eventCode E s]
      else s.events := by
  cases h0 : CircularLogState.occupied s E.port0 <;>
    cases h1 : CircularLogState.occupied s E.port1 <;>
    simp [CircularLogState.step, h0, h1]

end C1Compatible

/-- The actual atom sets at the two ordered collision ports. -/
def c1LeftParent (E : CircularEnvironment n m) (s : CircularLogState n m) :
    Finset (Fin m) :=
  Finset.univ.filter (fun i => s.site i = E.port0)

def c1RightParent (E : CircularEnvironment n m) (s : CircularLogState n m) :
    Finset (Fin m) :=
  Finset.univ.filter (fun i => s.site i = E.port1)

theorem eventCode_left_iff (E : CircularEnvironment n m)
    (s : CircularLogState n m) (i : Fin m) :
    CircularLogState.eventCode E s i = 0 ↔ s.site i = E.port0 := by
  by_cases h0 : s.site i = E.port0
  · simp [CircularLogState.eventCode, h0]
  · by_cases h1 : s.site i = E.port1 <;>
      simp [CircularLogState.eventCode, h0, h1]

theorem eventCode_right_iff (E : CircularEnvironment n m)
    (s : CircularLogState n m) (i : Fin m) :
    CircularLogState.eventCode E s i = 1 ↔ s.site i = E.port1 := by
  by_cases h0 : s.site i = E.port0
  · have h1 : s.site i ≠ E.port1 := by
      intro heq
      exact E.ports_ne (h0.symm.trans heq)
    simp [CircularLogState.eventCode, h0, E.ports_ne]
  · by_cases h1 : s.site i = E.port1 <;>
      simp [CircularLogState.eventCode, h0, h1, Ne.symm E.ports_ne]

theorem eventCode_recovers_parents (E : CircularEnvironment n m)
    (s t : CircularLogState n m)
    (h : CircularLogState.eventCode E s = CircularLogState.eventCode E t) :
    c1LeftParent E s = c1LeftParent E t ∧
      c1RightParent E s = c1RightParent E t := by
  constructor
  · ext i
    simp only [c1LeftParent, Finset.mem_filter, Finset.mem_univ, true_and]
    rw [← eventCode_left_iff E s i, ← eventCode_left_iff E t i, h]
  · ext i
    simp only [c1RightParent, Finset.mem_filter, Finset.mem_univ, true_and]
    rw [← eventCode_right_iff E s i, ← eventCode_right_iff E t i, h]

/-- The concrete packet occupying a physical site, recovered from per-atom
positions. It may be empty at a hole. -/
def c1PacketAt (_E : CircularEnvironment n m) (s : CircularLogState n m)
    (q : Fin n) : Finset (Fin m) :=
  Finset.univ.filter (fun i => s.site i = q)

@[simp] theorem mem_c1PacketAt (E : CircularEnvironment n m)
    (s : CircularLogState n m) (q : Fin n) (i : Fin m) :
    i ∈ c1PacketAt E s q ↔ s.site i = q := by
  simp [c1PacketAt]

theorem c1PacketAt_port0 (E : CircularEnvironment n m)
    (s : CircularLogState n m) :
    c1PacketAt E s E.port0 = c1LeftParent E s := rfl

theorem c1PacketAt_port1 (E : CircularEnvironment n m)
    (s : CircularLogState n m) :
    c1PacketAt E s E.port1 = c1RightParent E s := rfl

theorem c1Defect_preimage_port0 (E : CircularEnvironment n m)
    (q : Fin n) :
    c1Defect E q = E.port0 ↔ q = E.port0 ∨ q = E.port1 := by
  by_cases h : q = E.port1
  · simp [c1Defect, h]
  · simp [c1Defect, h]

theorem c1Defect_preimage_port1 (E : CircularEnvironment n m)
    (q : Fin n) : c1Defect E q ≠ E.port1 := by
  by_cases h : q = E.port1
  · simp [c1Defect, h, E.ports_ne]
  · simp [c1Defect, h]

theorem c1Defect_preimage_other (E : CircularEnvironment n m)
    (q target : Fin n) (h0 : target ≠ E.port0) (h1 : target ≠ E.port1) :
    c1Defect E q = target ↔ q = target := by
  by_cases h : q = E.port1
  · subst q
    simp [c1Defect, Ne.symm h0, Ne.symm h1]
  · simp [c1Defect, h]

/-- The standard defect reproduces exactly the ordered two-port packet
fusion, including the emptied right port and unchanged other sites. -/
theorem c1PacketAt_step_d (E : CircularEnvironment n m) (h : C1Compatible E)
    (s : CircularLogState n m) (q : Fin n) :
    c1PacketAt E (CircularLogState.step E s .d) q =
      if q = E.port0 then c1PacketAt E s E.port0 ∪ c1PacketAt E s E.port1
      else if q = E.port1 then ∅ else c1PacketAt E s q := by
  by_cases h0 : q = E.port0
  · subst q
    ext i
    simpa [c1PacketAt, h.step_d_site] using
      (c1Defect_preimage_port0 E (s.site i))
  · by_cases h1 : q = E.port1
    · subst q
      ext i
      have hport : E.port1 ≠ E.port0 := Ne.symm E.ports_ne
      simp [c1PacketAt, h.step_d_site, hport, c1Defect_preimage_port1]
    · simp only [if_neg h0, if_neg h1]
      ext i
      simpa [c1PacketAt, h.step_d_site] using
        (c1Defect_preimage_other E (s.site i) q h0 h1)

end PaperXL
