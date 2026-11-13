import FusionLogAllR.AllROptimality
import RegisteredAbsorptionChains.NoSplitting

namespace FusionLogAllR

open RegisteredAbsorptionChains

/-! # Rotation bounds extracted from actual chronological execution

An atom's nonnegative height follows the literal letters: `p` adds one;
`d` subtracts one exactly at site 1. This also follows an atom through
effective fusions. In an all-R inter-fusion interval every such downward
step is a nonfusion carrier backslide, but that restriction is not needed
for the local bounds below.
-/

def carrierHeightStep (n z : ℕ) : Letter → ℕ
  | .p => z + 1
  | .d => if (z : ZMod n) = 1 then z - 1 else z

def carrierHeightRun (n z : ℕ) (word : List Letter) : ℕ :=
  word.foldl (carrierHeightStep n) z

def carrierDownSteps (n z : ℕ) : List Letter → ℕ
  | [] => 0
  | .p :: rest => carrierDownSteps n (z + 1) rest
  | .d :: rest => (if (z : ZMod n) = 1 then 1 else 0) +
      carrierDownSteps n (carrierHeightStep n z .d) rest

private theorem height_pos_of_site_one {n z : ℕ} (hn : 2 ≤ n)
    (h : (z : ZMod n) = 1) : 0 < z := by
  by_contra hz
  have : z = 0 := by omega
  subst z
  have hone : (1 : ZMod n) = 0 := by simpa using h.symm
  have := ZMod.one_eq_zero_iff.mp hone
  omega

theorem carrierHeightRun_balance (n z : ℕ) (hn : 2 ≤ n)
    (word : List Letter) :
    carrierHeightRun n z word + carrierDownSteps n z word =
      z + word.count .p := by
  induction word generalizing z with
  | nil => simp [carrierHeightRun, carrierDownSteps]
  | cons a rest ih =>
      cases a with
      | p =>
          have h := ih (z + 1)
          simpa [carrierHeightRun, carrierDownSteps, carrierHeightStep,
            List.count_cons, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using h
      | d =>
          have h := ih (carrierHeightStep n z .d)
          by_cases hz : (z : ZMod n) = 1
          · have hp := height_pos_of_site_one hn hz
            simp [carrierHeightRun, carrierDownSteps,
              carrierHeightStep, hz] at h ⊢
            omega
          · simpa [carrierHeightRun, carrierDownSteps, carrierHeightStep,
              hz, List.count_cons] using h

theorem carrierHeightStep_cast (n z : ℕ) (hn : 2 ≤ n) (a : Letter) :
    (carrierHeightStep n z a : ZMod n) =
      forwardMapStep (fun _ : ZMod n => (z : ZMod n)) a 0 := by
  cases a with
  | p => simp [carrierHeightStep, forwardMapStep]
  | d =>
      by_cases hz : (z : ZMod n) = 1
      · have hp := height_pos_of_site_one hn hz
        have hsub : z - 1 + 1 = z := Nat.sub_add_cancel hp
        have hcast : ((z - 1 : ℕ) : ZMod n) + 1 = (z : ZMod n) := by
          simpa only [Nat.cast_add, Nat.cast_one] using
            congrArg (fun k : ℕ => (k : ZMod n)) hsub
        simp only [carrierHeightStep, hz, if_true, forwardMapStep,
          Function.comp_apply, collapsePosition]
        rw [hz] at hcast
        linear_combination hcast
      · simp [carrierHeightStep, forwardMapStep, collapsePosition, hz]

theorem carrierHeightRun_cast {n : ℕ} [NeZero n]
    (f : ZMod n → ZMod n) (a : ZMod n) (z : ℕ)
    (hn : 2 ≤ n) (hsite : f a = (z : ZMod n)) (word : List Letter) :
    forwardMapRun f word a = (carrierHeightRun n z word : ZMod n) := by
  induction word generalizing f z with
  | nil => simpa [forwardMapRun, carrierHeightRun] using hsite
  | cons l rest ih =>
      change forwardMapRun (forwardMapStep f l) rest a =
        (carrierHeightRun n (carrierHeightStep n z l) rest : ZMod n)
      apply ih
      have hstep := carrierHeightStep_cast n z hn l
      cases l <;> simpa [forwardMapStep, hsite] using hstep.symm

theorem carrierHeightRun_site {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (a q : ZMod n) (z : ℕ)
    (word : List Letter) (B : Finset (ZMod n)) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f) (hstart : f a = (z : ZMod n))
    (hpacket : (run F s word).placed q = some B) (ha : a ∈ B) :
    (carrierHeightRun n z word : ZMod n) = q := by
  rw [run_placementOfMap F s f word hn hplaced] at hpacket
  obtain ⟨hf, _⟩ := (placementOfMap_some_iff _ q B).mp hpacket
  have hpos := (mem_sourceFiber _ a q).mp (hf.symm ▸ ha)
  rw [carrierHeightRun_cast f a z hn hstart word] at hpos
  exact hpos

/-- A `d` can never populate port 1, including when it is an effective fusion. -/
theorem defect_port_one_empty {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (hn : 2 ≤ n) :
    (step F s .d).placed 1 = none := by
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  rw [show (step F s .d).placed = fusionPlacement s.placed from
    stepDefect_placed F s]
  simp [fusionPlacement, h10]

/-- If the lifted carrier is still at height zero, port 1 is still empty.
This proves the positive-turn fact without choosing a last backslide. -/
theorem carrierHeightRun_zero_hole {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (z : ℕ)
    (hn : 2 ≤ n) (hzero : z = 0 → s.placed 1 = none)
    (word : List Letter) :
    carrierHeightRun n z word = 0 → (run F s word).placed 1 = none := by
  induction word generalizing s z with
  | nil => simpa [carrierHeightRun, run] using hzero
  | cons a rest ih =>
      change carrierHeightRun n (carrierHeightStep n z a) rest = 0 →
        (run F (step F s a) rest).placed 1 = none
      apply ih
      cases a with
      | p => simp [carrierHeightStep]
      | d => exact fun _ => defect_port_one_empty F s hn

theorem interFusion_rotation_lower_bound {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (word : List Letter)
    (hn : 2 ≤ n) (hstartHole : s.placed 1 = none)
    (hendSite : (carrierHeightRun n 0 word : ZMod n) = 0)
    (hendOccupied : (run F s word).placed 1 ≠ none) :
    n + carrierDownSteps n 0 word ≤ word.count .p := by
  have hpos : 0 < carrierHeightRun n 0 word := by
    by_contra h
    have hz : carrierHeightRun n 0 word = 0 := by omega
    exact hendOccupied (carrierHeightRun_zero_hole F s 0 hn
      (fun _ => hstartHole) word hz)
  have hdiv := (ZMod.natCast_eq_zero_iff _ n).mp hendSite
  have hturn := Nat.le_of_dvd hpos hdiv
  have hbalance := carrierHeightRun_balance n 0 hn word
  omega

theorem tail_rotation_lower_bound {n : ℕ} [NeZero n]
    (word : List Letter) (hn : 2 ≤ n)
    (hendSite : (carrierHeightRun n 0 word : ZMod n) = (n - 1 : ℕ)) :
    n - 1 + carrierDownSteps n 0 word ≤ word.count .p := by
  have hmod := congrArg ZMod.val hendSite
  simp only [ZMod.val_natCast] at hmod
  rw [Nat.mod_eq_of_lt (by omega : n - 1 < n)] at hmod
  have hheight := Nat.mod_le (carrierHeightRun n 0 word) n
  have hbalance := carrierHeightRun_balance n 0 hn word
  omega

/-- Count actual `d` letters whose predecessor has the marked atom at port 1.
For an all-R inter-fusion interval these are exactly nonfusion backslides.
On unrestricted histories the definition also counts fusions from port 1. -/
def executionCarrierReturns {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (a : ZMod n) :
    List Letter → ℕ
  | [] => 0
  | .p :: rest => executionCarrierReturns F (step F s .p) a rest
  | .d :: rest => (if a ∈ (s.placed 1).getD ∅ then 1 else 0) +
      executionCarrierReturns F (step F s .d) a rest

theorem executionCarrierReturns_append {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (a : ZMod n)
    (u v : List Letter) :
    executionCarrierReturns F s a (u ++ v) = executionCarrierReturns F s a u +
      executionCarrierReturns F (run F s u) a v := by
  induction u generalizing s with
  | nil => simp [executionCarrierReturns, run]
  | cons l rest ih =>
      cases l <;> simp [executionCarrierReturns, run, ih, Nat.add_assoc]

private theorem atomAt_placementOfMap_iff {n : ℕ} [NeZero n]
    (f : ZMod n → ZMod n) (a q : ZMod n) :
    a ∈ (placementOfMap f q).getD ∅ ↔ f a = q := by
  by_cases h : (sourceFiber f q).Nonempty
  · simp [placementOfMap, h]
  · have hempty := Finset.not_nonempty_iff_eq_empty.mp h
    have ha : f a ≠ q := by
      intro heq
      exact h ⟨a, (mem_sourceFiber f a q).mpr heq⟩
    simp [placementOfMap, h, ha]

theorem executionCarrierReturns_eq_height {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (a : ZMod n) (z : ℕ)
    (hn : 2 ≤ n) (hplaced : s.placed = placementOfMap f)
    (hsite : f a = (z : ZMod n)) (word : List Letter) :
    executionCarrierReturns F s a word = carrierDownSteps n z word := by
  induction word generalizing s f z with
  | nil => rfl
  | cons l rest ih =>
      have hnext : forwardMapStep f l a = (carrierHeightStep n z l : ZMod n) := by
        have h := carrierHeightStep_cast n z hn l
        cases l <;> simpa [forwardMapStep, hsite] using h.symm
      have hrest := ih (step F s l) (forwardMapStep f l)
        (carrierHeightStep n z l) (step_placementOfMap F s f l hn hplaced) hnext
      cases l with
      | p => exact hrest
      | d =>
          simp only [executionCarrierReturns, carrierDownSteps]
          simp only [hrest, hplaced, atomAt_placementOfMap_iff, hsite]

/-- The interval bound is now expressed entirely with actual execution,
packet membership, and raw-letter counts; no numerical rotation certificate
is assumed. -/
theorem actual_interFusion_rotation_lower_bound {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (word : List Letter)
    (a : ZMod n) (C D : Finset (ZMod n)) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (hstart : s.placed 0 = some C) (haC : a ∈ C)
    (hstartHole : s.placed 1 = none)
    (hend : (run F s word).placed 0 = some D) (haD : a ∈ D)
    (hendOccupied : (run F s word).placed 1 ≠ none) :
    n + executionCarrierReturns F s a word ≤ word.count .p := by
  obtain ⟨lift, hplaced⟩ := ordered
  have hsource := (placementOfMap_some_iff lift.position 0 C).mp
    (hplaced ▸ hstart)
  have hsite : lift.position a = (0 : ℕ) :=
    by simpa using (mem_sourceFiber lift.position a 0).mp (hsource.1.symm ▸ haC)
  have hendSite := carrierHeightRun_site F s lift.position a 0 0 word D hn
    hplaced hsite hend haD
  rw [executionCarrierReturns_eq_height F s lift.position a 0 hn hplaced hsite word]
  exact interFusion_rotation_lower_bound F s word hn hstartHole hendSite hendOccupied

theorem actual_tail_rotation_lower_bound {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (word : List Letter)
    (a : ZMod n) (C D : Finset (ZMod n)) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (hstart : s.placed 0 = some C) (haC : a ∈ C)
    (hend : (run F s word).placed (n - 1 : ℕ) = some D) (haD : a ∈ D) :
    n - 1 + executionCarrierReturns F s a word ≤ word.count .p := by
  obtain ⟨lift, hplaced⟩ := ordered
  have hsource := (placementOfMap_some_iff lift.position 0 C).mp
    (hplaced ▸ hstart)
  have hsite : lift.position a = (0 : ℕ) :=
    by simpa using (mem_sourceFiber lift.position a 0).mp (hsource.1.symm ▸ haC)
  have hendSite := carrierHeightRun_site F s lift.position a (n - 1 : ℕ) 0 word D hn
    hplaced hsite hend haD
  rw [executionCarrierReturns_eq_height F s lift.position a 0 hn hplaced hsite word]
  exact tail_rotation_lower_bound word hn hendSite

private theorem marked_port_one_absent {n : ℕ} [NeZero n]
    (s : Execution n (ZMod n)) (a : ZMod n) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (hzero : a ∈ (s.placed 0).getD ∅) : a ∉ (s.placed 1).getD ∅ := by
  obtain ⟨lift, hplaced⟩ := ordered
  rw [hplaced, atomAt_placementOfMap_iff] at hzero
  rw [hplaced, atomAt_placementOfMap_iff]
  intro hone
  have heq : (1 : ZMod n) = 0 := hone.symm.trans hzero
  have := ZMod.one_eq_zero_iff.mp heq
  omega

/-- A literal decomposition into successive right-port fusions. The stored
facts concern actual predecessor ports, never a numerical cost budget.
The initial state is immediately after registration; `k` counts subsequent
fusions. No restriction on intervening physical coordinates is imposed. -/
inductive RightFusionIntervals {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (a : ZMod n) :
    ℕ → Execution n (ZMod n) → Execution n (ZMod n) → List Letter → Prop
  | nil (s) : RightFusionIntervals F a 0 s s []
  | cons {k s u restWord} (segment : List Letter)
      (startMarked : a ∈ (s.placed 0).getD ∅)
      (startHole : s.placed 1 = none)
      (endMarked : a ∈ ((run F s segment).placed 0).getD ∅)
      (endOccupied : (run F s segment).placed 1 ≠ none)
      (rest : RightFusionIntervals F a k
        (step F (run F s segment) .d) u restWord) :
      RightFusionIntervals F a (k + 1) s u (segment ++ [.d] ++ restWord)

theorem RightFusionIntervals.run_eq {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n} {k : ℕ}
    {s t : Execution n (ZMod n)} {word : List Letter}
    (intervals : RightFusionIntervals F a k s t word) :
    run F s word = t := by
  induction intervals with
  | nil s => rfl
  | cons segment _ _ _ _ rest ih =>
      simpa [run, List.foldl_append] using ih

theorem RightFusionIntervals.rotation_lower_bound {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n} {k : ℕ}
    {s t : Execution n (ZMod n)} {word : List Letter}
    (intervals : RightFusionIntervals F a k s t word)
    (hn : 2 ≤ n) (ordered : SourceOrdered s.placed) :
    k * n + executionCarrierReturns F s a word ≤ word.count .p := by
  induction intervals with
  | nil s => simp [executionCarrierReturns]
  | @cons k s u restWord segment hstart hhole hend hright rest ih =>
      have hmidOrder := run_ordered F s segment hn ordered
      have hnextOrder := step_ordered F (run F s segment) .d hn hmidOrder
      have hrest := ih hnextOrder
      have hstartPacket : ∃ C, s.placed 0 = some C ∧ a ∈ C := by
        cases h : s.placed 0 with
        | none => simp [h] at hstart
        | some C => exact ⟨C, rfl, by simpa [h] using hstart⟩
      have hendPacket : ∃ D, (run F s segment).placed 0 = some D ∧ a ∈ D := by
        cases h : (run F s segment).placed 0 with
        | none => simp [h] at hend
        | some D => exact ⟨D, rfl, by simpa [h] using hend⟩
      obtain ⟨C, hC, haC⟩ := hstartPacket
      obtain ⟨D, hD, haD⟩ := hendPacket
      have hsegment := actual_interFusion_rotation_lower_bound F s segment a C D hn
        ordered hC haC hhole hD haD hright
      have habsent := marked_port_one_absent (run F s segment) a hn hmidOrder hend
      simp only [run] at habsent
      simp only [executionCarrierReturns_append, run_append, List.count_append]
      simp [executionCarrierReturns, habsent, run, Nat.succ_mul,
        List.count_nil] at hrest hsegment ⊢
      omega

theorem RightFusionIntervals.rotation_lower_bound_with_tail {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n} {k : ℕ}
    {s t : Execution n (ZMod n)} {word : List Letter}
    (intervals : RightFusionIntervals F a k s t word)
    (hn : 2 ≤ n) (ordered : SourceOrdered s.placed)
    (tail : List Letter)
    (C D : Finset (ZMod n)) (hstart : t.placed 0 = some C) (haC : a ∈ C)
    (hend : (run F t tail).placed (n - 1 : ℕ) = some D) (haD : a ∈ D) :
    k * n + (n - 1) + executionCarrierReturns F s a (word ++ tail) ≤
      (word ++ tail).count .p := by
  have hinterval := intervals.rotation_lower_bound hn ordered
  have hrun := intervals.run_eq
  have htOrder : SourceOrdered t.placed := hrun ▸ run_ordered F s word hn ordered
  have htail := actual_tail_rotation_lower_bound F t tail a C D hn htOrder
    hstart haC hend haD
  rw [executionCarrierReturns_append, hrun, List.count_append]
  omega

/-- The manuscript's global rotation budget, for a literal decomposition
into the `n-2` post-registration right fusions and the actual terminal tail.
Extracting this decomposition from the specified full event log is separate. -/
theorem actual_allR_rotation_lower_bound {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    (intervals : RightFusionIntervals F a (n - 2) s t word)
    (hn : 3 ≤ n) (ordered : SourceOrdered s.placed)
    (tail : List Letter)
    (C D : Finset (ZMod n)) (hstart : t.placed 0 = some C) (haC : a ∈ C)
    (hend : (run F t tail).placed (n - 1 : ℕ) = some D) (haD : a ∈ D) :
    pMin n + executionCarrierReturns F s a (word ++ tail) ≤
      (word ++ tail).count .p := by
  have h := intervals.rotation_lower_bound_with_tail (by omega) ordered
    tail C D hstart haC hend haD
  have h₁ : n - 1 + 1 = n := Nat.sub_add_cancel (by omega)
  have h₂ : n - 2 + 2 = n := Nat.sub_add_cancel (by omega)
  have hpoly : pMin n = (n - 2) * n + (n - 1) := by
    have hp : n * (n - 1) = (n - 2) * n + n := by nlinarith
    unfold pMin
    omega
  rw [hpoly]
  exact h

end FusionLogAllR
