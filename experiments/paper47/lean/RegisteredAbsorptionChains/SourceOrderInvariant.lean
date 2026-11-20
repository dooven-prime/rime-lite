import RegisteredAbsorptionChains.CyclicOrderAdmission
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def sourceFiber (f : ZMod n → ZMod n) (q : ZMod n) : Finset (ZMod n) :=
  Finset.univ.filter (fun a => f a = q)

def placementOfMap (f : ZMod n → ZMod n) :
    Placement n (Finset (ZMod n)) :=
  fun q => let block := sourceFiber f q
    if block.Nonempty then some block else none

@[simp] theorem mem_sourceFiber (f : ZMod n → ZMod n)
    (a q : ZMod n) : a ∈ sourceFiber f q ↔ f a = q := by
  simp [sourceFiber]

@[simp] theorem placementOfMap_none_iff (f : ZMod n → ZMod n)
    (q : ZMod n) : placementOfMap f q = none ↔ sourceFiber f q = ∅ := by
  simp only [placementOfMap]
  by_cases h : (sourceFiber f q).Nonempty
  · simp [h, Finset.nonempty_iff_ne_empty.mp h]
  · simp [Finset.not_nonempty_iff_eq_empty.mp h]

theorem placementOfMap_some_iff (f : ZMod n → ZMod n)
    (q : ZMod n) (B : Finset (ZMod n)) :
    placementOfMap f q = some B ↔ sourceFiber f q = B ∧ B.Nonempty := by
  simp only [placementOfMap]
  by_cases h : (sourceFiber f q).Nonempty
  · simp only [if_pos h, Option.some.injEq]
    constructor
    · intro eq
      subst B
      exact ⟨rfl, h⟩
    · exact fun ⟨eq, _⟩ => eq
  · simp only [if_neg h, reduceCtorEq, false_iff]
    intro ⟨eq, hb⟩
    exact h (eq.symm ▸ hb)

theorem sourceFiber_rotate (f : ZMod n → ZMod n) (q : ZMod n) :
    sourceFiber (fun a => f a + 1) q = sourceFiber f (q - 1) := by
  ext a
  simp only [mem_sourceFiber]
  constructor
  · intro h
    calc
      f a = (f a + 1) - 1 := by abel
      _ = q - 1 := congrArg (· - 1) h
  · intro h
    calc
      f a + 1 = (q - 1) + 1 := by rw [h]
      _ = q := by abel

theorem placementOfMap_rotate (f : ZMod n → ZMod n) :
    placementOfMap (fun a => f a + 1) = rotate 1 (placementOfMap f) := by
  funext q
  simp only [placementOfMap, rotate, sourceFiber_rotate]

def collapsePosition (q : ZMod n) : ZMod n :=
  if q = 1 then 0 else q

theorem sourceFiber_collapse_zero (f : ZMod n → ZMod n) :
    sourceFiber (collapsePosition ∘ f) 0 =
      sourceFiber f 0 ∪ sourceFiber f 1 := by
  ext a
  simp only [mem_sourceFiber, Finset.mem_union, Function.comp_apply]
  unfold collapsePosition
  by_cases h : f a = 1 <;> simp [h]

theorem sourceFiber_collapse_one (f : ZMod n → ZMod n) (hn : 2 ≤ n) :
    sourceFiber (collapsePosition ∘ f) 1 = ∅ := by
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h.symm
    omega
  ext a
  simp only [mem_sourceFiber, Function.comp_apply]
  by_cases h : f a = 1 <;> simp [collapsePosition, h, h01]

theorem sourceFiber_collapse_other (f : ZMod n → ZMod n)
    (q : ZMod n) (hq0 : q ≠ 0) (hq1 : q ≠ 1) :
    sourceFiber (collapsePosition ∘ f) q = sourceFiber f q := by
  ext a
  simp only [mem_sourceFiber, Function.comp_apply]
  unfold collapsePosition
  by_cases h : f a = 1 <;> simp [h, hq0.symm, hq1.symm]

theorem placementOfMap_defect (f : ZMod n → ZMod n) (hn : 2 ≤ n) :
    placementOfMap (collapsePosition ∘ f) =
      fusionPlacement (placementOfMap f) := by
  funext q
  by_cases hq0 : q = 0
  · subst q
    change (if (sourceFiber (collapsePosition ∘ f) 0).Nonempty then
        some (sourceFiber (collapsePosition ∘ f) 0) else none) =
      fusionPlacement (placementOfMap f) 0
    rw [sourceFiber_collapse_zero f]
    simp only [fusionPlacement, ite_true]
    by_cases h0 : (sourceFiber f 0).Nonempty
    · by_cases h1 : (sourceFiber f 1).Nonempty
      · simp [placementOfMap, h0, h1]
      · simp [placementOfMap, h0,
          Finset.not_nonempty_iff_eq_empty.mp h1]
    · by_cases h1 : (sourceFiber f 1).Nonempty
      · simp [placementOfMap, h1,
          Finset.not_nonempty_iff_eq_empty.mp h0]
      · simp [placementOfMap,
          Finset.not_nonempty_iff_eq_empty.mp h0,
          Finset.not_nonempty_iff_eq_empty.mp h1]
  by_cases hq1 : q = 1
  · subst q
    change (if (sourceFiber (collapsePosition ∘ f) 1).Nonempty then
        some (sourceFiber (collapsePosition ∘ f) 1) else none) =
      fusionPlacement (placementOfMap f) 1
    rw [sourceFiber_collapse_one f hn]
    simp [fusionPlacement, hq0]
  · change (if (sourceFiber (collapsePosition ∘ f) q).Nonempty then
        some (sourceFiber (collapsePosition ∘ f) q) else none) =
      fusionPlacement (placementOfMap f) q
    rw [sourceFiber_collapse_other f q hq0 hq1]
    simp [placementOfMap, fusionPlacement, hq0, hq1]

/-- A degree-one monotone lift of the source-to-position map. This is a
genuine order certificate: it contains no execution history. -/
structure SourceOrderLift (n : ℕ) where
  map : ℤ → ℤ
  monotone : Monotone map
  periodic : ∀ x k : ℤ, map (x + k * n) = map x + k * n

def SourceOrderLift.position (lift : SourceOrderLift n) (a : ZMod n) : ZMod n :=
  (lift.map a.val : ZMod n)

omit [NeZero n] in
theorem SourceOrderLift.fiber_convex (lift : SourceOrderLift n)
    {x y z : ℤ} (hxy : x ≤ y) (hyz : y ≤ z)
    (hends : lift.map x = lift.map z) : lift.map y = lift.map x := by
  have hleft := lift.monotone hxy
  have hright := lift.monotone hyz
  omega

def SourceOrderLift.seed (n : ℕ) : SourceOrderLift n where
  map := id
  monotone := monotone_id
  periodic := by intro x k; rfl

def SourceOrderLift.rotate (lift : SourceOrderLift n) : SourceOrderLift n where
  map := fun x => lift.map x + 1
  monotone := by intro x y h; have := lift.monotone h; dsimp; omega
  periodic := by intro x k; rw [lift.periodic]; omega

/-- The lift of the idempotent adjacent collapse `d(1)=0`. -/
def sourceDefectLift (x : ℤ) : ℤ :=
  if (x : ZMod n) = 1 then x - 1 else x

omit [NeZero n] in
theorem sourceDefectLift_monotone : Monotone (sourceDefectLift (n := n)) := by
  intro x y hxy
  by_cases heq : x = y
  · simp [heq]
  have hlt : x + 1 ≤ y := by omega
  unfold sourceDefectLift
  split_ifs <;> omega

omit [NeZero n] in
theorem sourceDefectLift_periodic (x k : ℤ) :
    sourceDefectLift (n := n) (x + k * n) =
      sourceDefectLift (n := n) x + k * n := by
  have hcast : ((x + k * n : ℤ) : ZMod n) = (x : ZMod n) := by simp
  simp only [sourceDefectLift, hcast]
  split_ifs <;> omega

def SourceOrderLift.defect (lift : SourceOrderLift n) : SourceOrderLift n where
  map := sourceDefectLift ∘ lift.map
  monotone := sourceDefectLift_monotone.comp lift.monotone
  periodic := by
    intro x k
    change sourceDefectLift (lift.map (x + k * n)) =
      sourceDefectLift (lift.map x) + k * n
    rw [lift.periodic, sourceDefectLift_periodic]

@[simp] theorem SourceOrderLift.seed_position (a : ZMod n) :
    (SourceOrderLift.seed n).position a = a := by
  simp [SourceOrderLift.seed, SourceOrderLift.position]

@[simp] theorem SourceOrderLift.rotate_position (lift : SourceOrderLift n)
    (a : ZMod n) :
    lift.rotate.position a = lift.position a + 1 := by
  simp [SourceOrderLift.rotate, SourceOrderLift.position]

omit [NeZero n] in
@[simp] theorem SourceOrderLift.defect_position (lift : SourceOrderLift n)
    (a : ZMod n) :
    lift.defect.position a =
      if lift.position a = 1 then 0 else lift.position a := by
  have hcore (x : ℤ) :
      (sourceDefectLift (n := n) x : ZMod n) =
        if (x : ZMod n) = 1 then 0 else (x : ZMod n) := by
    by_cases h : (x : ZMod n) = 1 <;> simp [sourceDefectLift, h]
  exact hcore (lift.map a.val)

/-- A source-order certificate for a concrete placed partition. -/
def SourceOrdered (placed : Placement n (Finset (ZMod n))) : Prop :=
  ∃ lift : SourceOrderLift n, placed = placementOfMap lift.position

def singletonExecution (n : ℕ) [NeZero n] : Execution n (ZMod n) :=
  { placed := fun q => some {q}
    origin := none
    chain := [] }

theorem singletonExecution_ordered :
    SourceOrdered (singletonExecution n).placed := by
  refine ⟨SourceOrderLift.seed n, ?_⟩
  funext q
  have hfiber : sourceFiber (SourceOrderLift.seed n).position q = {q} := by
    ext a
    simp [sourceFiber]
  simp [singletonExecution, placementOfMap, hfiber]

omit [NeZero n] in
theorem stepDefect_placed (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) :
    (stepDefect F s).placed = fusionPlacement s.placed := by
  unfold stepDefect
  cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;> simp

theorem step_ordered (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (a : Letter) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed) :
    SourceOrdered (step F s a).placed := by
  obtain ⟨lift, hplaced⟩ := ordered
  cases a with
  | p =>
      refine ⟨lift.rotate, ?_⟩
      simp only [step, hplaced]
      rw [show lift.rotate.position = (fun a => lift.position a + 1) by
        funext a
        exact SourceOrderLift.rotate_position lift a]
      exact (placementOfMap_rotate lift.position).symm
  | d =>
      refine ⟨lift.defect, ?_⟩
      rw [show (step F s .d).placed = fusionPlacement s.placed from
        stepDefect_placed F s, hplaced]
      rw [show lift.defect.position = collapsePosition ∘ lift.position by
        funext a
        simp [SourceOrderLift.defect_position, collapsePosition]]
      exact (placementOfMap_defect lift.position hn).symm

theorem run_ordered (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed) :
    SourceOrdered (run F s word).placed := by
  induction word generalizing s with
  | nil => simpa [run] using ordered
  | cons a rest ih =>
      change SourceOrdered (run F (step F s a) rest).placed
      exact ih (step F s a) (step_ordered F s a hn ordered)

def ReachableFromSingleton (F : Finset (ZMod n))
    (placed : Placement n (Finset (ZMod n))) : Prop :=
  ∃ word : List Letter, (run F (singletonExecution n) word).placed = placed

theorem reachable_source_ordered (F : Finset (ZMod n))
    (placed : Placement n (Finset (ZMod n))) (hn : 2 ≤ n)
    (reachable : ReachableFromSingleton F placed) : SourceOrdered placed := by
  obtain ⟨word, hword⟩ := reachable
  rw [← hword]
  exact run_ordered F (singletonExecution n) word hn singletonExecution_ordered

omit [NeZero n] in
/-- Occupied adjacent target ports have consecutive integer-lift values.
Consequently no third source packet occurs between the two lifted fibers. -/
theorem SourceOrderLift.adjacent_port_fibers (lift : SourceOrderLift n)
    (a b : ZMod n) (ha : lift.position a = 0)
    (hb : lift.position b = 1) :
    ∃ k : ℤ,
      (a.val : ℤ) < (b.val : ℤ) + k * n ∧
      lift.map ((b.val : ℤ) + k * n) = lift.map (a.val : ℤ) + 1 ∧
      ∀ x : ℤ, (a.val : ℤ) ≤ x → x ≤ (b.val : ℤ) + k * n →
        lift.map x = lift.map (a.val : ℤ) ∨
          lift.map x = lift.map (a.val : ℤ) + 1 := by
  have hcast :
      ((lift.map (a.val : ℤ) + 1 - lift.map (b.val : ℤ) : ℤ) : ZMod n) = 0 := by
    push_cast
    change lift.position a + 1 - lift.position b = 0
    rw [ha, hb]
    ring
  obtain ⟨k, hk⟩ :=
    (ZMod.intCast_zmod_eq_zero_iff_dvd _ n).mp hcast
  have hend : lift.map ((b.val : ℤ) + k * n) =
      lift.map (a.val : ℤ) + 1 := by
    rw [lift.periodic]
    nlinarith [hk]
  have hlt : (a.val : ℤ) < (b.val : ℤ) + k * n := by
    by_contra h
    have hreverse : (b.val : ℤ) + k * n ≤ (a.val : ℤ) := by omega
    have hmono := lift.monotone hreverse
    omega
  refine ⟨k, hlt, hend, ?_⟩
  intro x hleft hright
  have hlo := lift.monotone hleft
  have hhi := lift.monotone hright
  rw [hend] at hhi
  omega

/-- At an actual two-port fusion, the parent blocks have source atoms whose
positive integer lift has no intervening third output fiber. -/
theorem fusion_ports_source_adjacent
    (s : Execution n (ZMod n)) (u v : Finset (ZMod n))
    (ordered : SourceOrdered s.placed)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v) :
    ∃ (lift : SourceOrderLift n) (a b : ZMod n) (k : ℤ),
      s.placed = placementOfMap lift.position ∧
      a ∈ u ∧ b ∈ v ∧
      (a.val : ℤ) < (b.val : ℤ) + k * n ∧
      lift.map ((b.val : ℤ) + k * n) = lift.map (a.val : ℤ) + 1 ∧
      ∀ x : ℤ, (a.val : ℤ) ≤ x → x ≤ (b.val : ℤ) + k * n →
        lift.map x = lift.map (a.val : ℤ) ∨
          lift.map x = lift.map (a.val : ℤ) + 1 := by
  obtain ⟨lift, hplaced⟩ := ordered
  have h0fiber : sourceFiber lift.position 0 = u ∧ u.Nonempty :=
    (placementOfMap_some_iff lift.position 0 u).mp (hplaced ▸ h0)
  have h1fiber : sourceFiber lift.position 1 = v ∧ v.Nonempty :=
    (placementOfMap_some_iff lift.position 1 v).mp (hplaced ▸ h1)
  obtain ⟨a, ha⟩ := h0fiber.2
  obtain ⟨b, hb⟩ := h1fiber.2
  have ha0 : lift.position a = 0 := by
    apply (mem_sourceFiber lift.position a 0).mp
    rw [h0fiber.1]
    exact ha
  have hb1 : lift.position b = 1 := by
    apply (mem_sourceFiber lift.position b 1).mp
    rw [h1fiber.1]
    exact hb
  obtain ⟨k, hlt, hend, hbetween⟩ :=
    lift.adjacent_port_fibers a b ha0 hb1
  exact ⟨lift, a, b, k, hplaced, ha, hb, hlt, hend, hbetween⟩

/-- The fusion case of the word induction: the updated partition remains
source-ordered and the two actual parents have no intervening third fiber. -/
theorem fusion_step_ordered_and_adjacent
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (u v : Finset (ZMod n)) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v) :
    SourceOrdered (step F s .d).placed ∧
    ∃ (lift : SourceOrderLift n) (a b : ZMod n) (k : ℤ),
      s.placed = placementOfMap lift.position ∧
      a ∈ u ∧ b ∈ v ∧
      (a.val : ℤ) < (b.val : ℤ) + k * n ∧
      lift.map ((b.val : ℤ) + k * n) = lift.map (a.val : ℤ) + 1 ∧
      ∀ x : ℤ, (a.val : ℤ) ≤ x → x ≤ (b.val : ℤ) + k * n →
        lift.map x = lift.map (a.val : ℤ) ∨
          lift.map x = lift.map (a.val : ℤ) + 1 := by
  exact ⟨step_ordered F s .d hn ordered,
    fusion_ports_source_adjacent s u v ordered h0 h1⟩

end RegisteredAbsorptionChains
