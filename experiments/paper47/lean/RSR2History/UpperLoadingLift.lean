import Mathlib.Tactic

namespace RSR2History

/-- The integer-coordinate action of a silent upper defect. -/
def upperDefectLift (n : Nat) (x : Int) : Int :=
  if x % (n : Int) = 1 then x - 1 else x

theorem upperDefectLift_mono (n : Nat) {x y : Int} (hxy : x ≤ y) :
    upperDefectLift n x ≤ upperDefectLift n y := by
  by_cases hx : x % (n : Int) = 1
  · by_cases hy : y % (n : Int) = 1
    · simp [upperDefectLift, hx, hy]
      omega
    · simp [upperDefectLift, hx, hy]
      omega
  · by_cases hy : y % (n : Int) = 1
    · simp [upperDefectLift, hx, hy]
      have hlt : x < y := by
        by_contra hnot
        have heq : x = y := by omega
        exact hx (by simpa [heq] using hy)
      omega
    · simpa [upperDefectLift, hx, hy] using hxy

theorem upperDefectLift_periodic (n : Nat) (x : Int) :
    upperDefectLift n (x + n) = upperDefectLift n x + n := by
  unfold upperDefectLift
  have hmod : (x + (n : Int)) % (n : Int) = x % (n : Int) := by
    simp
  by_cases hx : x % (n : Int) = 1
  · simp [hmod, hx]
    omega
  · simp [hmod, hx]

/-- On a set of packet lifts where a silent slide causes no collision,
the defect map preserves strict order. -/
theorem upperDefectLift_strict_of_no_collision (n : Nat) {x y : Int}
    (hxy : x < y)
    (hnc : upperDefectLift n x ≠ upperDefectLift n y) :
    upperDefectLift n x < upperDefectLift n y :=
  lt_of_le_of_ne (upperDefectLift_mono n hxy.le) hnc

/-- A defect slide cannot move a lift below a periodic birth coordinate. -/
theorem upperDefectLift_ge_birth {n : Nat} {birth x : Int}
    (hperiod : birth % (n : Int) = 0) (hbx : birth ≤ x) :
    birth ≤ upperDefectLift n x := by
  unfold upperDefectLift
  by_cases hslide : x % (n : Int) = 1
  · simp only [if_pos hslide]
    by_cases heq : x = birth
    · subst x
      rw [hperiod] at hslide
      norm_num at hslide
    · have hlt : birth < x := by omega
      omega
  · simpa only [if_neg hslide] using hbx

inductive UpperLiftOp where
  | rotate
  | silentSlide
  deriving DecidableEq, Repr

/-- Replay the two silent upper-coordinate updates on one packet. -/
def upperLiftRun (n : Nat) : List UpperLiftOp → Int → Int
  | [], x => x
  | .rotate :: ops, x => upperLiftRun n ops (x + 1)
  | .silentSlide :: ops, x => upperLiftRun n ops (upperDefectLift n x)

theorem upperLiftRun_ge_birth {n : Nat} {birth : Int}
    (hperiod : birth % (n : Int) = 0) :
    ∀ (ops : List UpperLiftOp) (x : Int), birth ≤ x →
      birth ≤ upperLiftRun n ops x := by
  intro ops
  induction ops with
  | nil =>
      intro x hx
      simpa [upperLiftRun] using hx
  | cons op ops ih =>
      intro x hx
      cases op with
      | rotate =>
          simp only [upperLiftRun]
          exact ih (x + 1) (by omega)
      | silentSlide =>
          simp only [upperLiftRun]
          exact ih (upperDefectLift n x)
            (upperDefectLift_ge_birth hperiod hx)

def upperLiftRotations : List UpperLiftOp → Nat
  | [] => 0
  | .rotate :: ops => upperLiftRotations ops + 1
  | .silentSlide :: ops => upperLiftRotations ops

def upperLiftSlideHits (n : Nat) : List UpperLiftOp → Int → Nat
  | [], _ => 0
  | .rotate :: ops, x => upperLiftSlideHits n ops (x + 1)
  | .silentSlide :: ops, x =>
      (if x % (n : Int) = 1 then 1 else 0) +
        upperLiftSlideHits n ops (upperDefectLift n x)

theorem upperLiftRun_eq_start_add_rotations_sub_slideHits (n : Nat)
    (ops : List UpperLiftOp) (x : Int) :
    upperLiftRun n ops x = x + (upperLiftRotations ops : Int) -
      (upperLiftSlideHits n ops x : Int) := by
  induction ops generalizing x with
  | nil => simp [upperLiftRun, upperLiftRotations, upperLiftSlideHits]
  | cons op ops ih =>
      cases op with
      | rotate =>
          simp only [upperLiftRun, upperLiftRotations, upperLiftSlideHits]
          rw [ih]
          simp only [Nat.cast_add, Nat.cast_one]
          omega
      | silentSlide =>
          simp only [upperLiftRun, upperLiftRotations, upperLiftSlideHits]
          rw [ih]
          by_cases hhit : x % (n : Int) = 1
          · simp [upperDefectLift, hhit]
            omega
          · simp [upperDefectLift, hhit]

/-- In a cyclic lift, the next packet inserted at the port lies at a new
multiple of `n`, beyond the previous packet's birth threshold. -/
theorem insertedLift_birth_lower_bound {n i : Nat} {previous birth : Int}
    (hprevious : (n : Int) * (i : Int) ≤ previous)
    (hbetween : previous < birth)
    (hmultiple : ∃ q : Int, birth = (n : Int) * q) :
    (n : Int) * ((i + 1 : Nat) : Int) ≤ birth := by
  obtain ⟨q, hq⟩ := hmultiple
  have hn_nonneg : 0 ≤ (n : Int) := by exact_mod_cast Nat.zero_le n
  have hstrict : (n : Int) * (i : Int) < (n : Int) * q := by
    calc
      (n : Int) * (i : Int) ≤ previous := hprevious
      _ < birth := hbetween
      _ = (n : Int) * q := hq
  have hiq : (i : Int) < q := by
    by_contra hnot
    have hqi : q ≤ (i : Int) := by omega
    have hmul := mul_le_mul_of_nonneg_left hqi hn_nonneg
    omega
  have hnext : ((i + 1 : Nat) : Int) ≤ q := by omega
  have hmul := mul_le_mul_of_nonneg_left hnext hn_nonneg
  simpa [hq] using hmul

/-- A certificate for an ordered sequence of upper arrivals. Between births,
the preceding packet follows its actual integer lift under silent upper
rotations and slides. Each new arrival is inserted at a later multiple of
the circumference. -/
inductive UpperBirthChain (n : Nat) : Nat → Int → Type where
  | first : UpperBirthChain n 1 0
  | next {i : Nat} {previous birth : Int}
      (prior : UpperBirthChain n i previous)
      (ops : List UpperLiftOp)
      (birth_periodic : birth % (n : Int) = 0)
      (birth_after : upperLiftRun n ops previous < birth) :
      UpperBirthChain n (i + 1) birth

theorem UpperBirthChain.birth_periodic {n i : Nat} {birth : Int}
    (chain : UpperBirthChain n i birth) : birth % (n : Int) = 0 := by
  induction chain with
  | first => simp
  | @next i previous birth prior ops hperiod hafter ih => exact hperiod

theorem UpperBirthChain.index_pos {n i : Nat} {birth : Int}
    (chain : UpperBirthChain n i birth) : 1 ≤ i := by
  induction chain with
  | first => omega
  | @next i previous birth prior ops hperiod hafter ih => omega

theorem UpperBirthChain.birth_lower_bound {n i : Nat} {birth : Int}
    (chain : UpperBirthChain n i birth) :
    (n : Int) * ((i - 1 : Nat) : Int) ≤ birth := by
  induction chain with
  | first => simp
  | @next i previous birth prior ops hperiod hafter ih =>
      have hcurrent : previous ≤ upperLiftRun n ops previous :=
        upperLiftRun_ge_birth prior.birth_periodic ops previous le_rfl
      have hprev : (n : Int) * ((i - 1 : Nat) : Int) ≤ previous := ih
      have hnew := insertedLift_birth_lower_bound hprev
        (lt_of_le_of_lt hcurrent hafter)
        ⟨birth / (n : Int), (Int.mul_ediv_cancel_of_emod_eq_zero hperiod).symm⟩
      simpa [Nat.sub_add_cancel prior.index_pos] using hnew

/-- Rounding a packed full-cycle endpoint up to the next integral period. -/
theorem upperLift_anchor_rounding {n : Nat} (hn : 2 ≤ n) {q : Int}
    (hlower : (n : Int) * ((n : Int) - 1) ≤
      (n : Int) * q + ((n : Int) - 1)) :
    (n : Int) * ((n : Int) - 1) ≤ (n : Int) * q := by
  have hnpos : 0 < (n : Int) := by exact_mod_cast (show 0 < n by omega)
  by_cases hq : (n : Int) - 1 ≤ q
  · exact mul_le_mul_of_nonneg_left hq (le_of_lt hnpos)
  · have hqle : q ≤ (n : Int) - 2 := by omega
    have hmul := mul_le_mul_of_nonneg_left hqle (le_of_lt hnpos)
    have hgap :
        (n : Int) * ((n : Int) - 2) + ((n : Int) - 1) <
          (n : Int) * ((n : Int) - 1) := by nlinarith
    have hbad :
        (n : Int) * q + ((n : Int) - 1) <
          (n : Int) * ((n : Int) - 1) := by linarith
    omega

/-- Geometric endpoint data at the first upper fusion. `last_birth_lower`
comes from the insertion induction; `packed_cycle` records full occupancy. -/
theorem upperLoading_anchor_lower_bound {n : Nat} (hn : 2 ≤ n)
    {anchor birth final : Int} (anchor_periodic : ∃ q : Int, anchor = (n : Int) * q)
    (arrivals : UpperBirthChain n n birth)
    (last_never_below_birth : birth ≤ final)
    (packed_cycle : final = anchor + ((n : Int) - 1)) :
    (n : Int) * ((n : Int) - 1) ≤ anchor := by
  have hlast_birth := arrivals.birth_lower_bound
  have hlast : (n : Int) * ((n : Int) - 1) ≤
      anchor + ((n : Int) - 1) := by
    have hcast : ((n - 1 : Nat) : Int) = (n : Int) - 1 := by omega
    rw [hcast] at hlast_birth
    calc
      (n : Int) * ((n : Int) - 1) ≤ birth := hlast_birth
      _ ≤ final := last_never_below_birth
      _ = anchor + ((n : Int) - 1) := packed_cycle
  obtain ⟨q, hq⟩ := anchor_periodic
  calc
    (n : Int) * ((n : Int) - 1) ≤ (n : Int) * q := by
      rw [hq] at hlast
      exact upperLift_anchor_rounding hn hlast
    _ = anchor := hq.symm

theorem upperLoading_rotations_lower_bound {n : Nat} (hn : 2 ≤ n)
    (anchorOps : List UpperLiftOp) {anchor birth final : Int}
    (arrivals : UpperBirthChain n n birth)
    (anchor_periodic : ∃ q : Int,
      upperLiftRun n anchorOps 0 = (n : Int) * q)
    (anchor_final : anchor = upperLiftRun n anchorOps 0)
    (final_ge_birth : birth ≤ final)
    (packed_cycle : final = anchor + ((n : Int) - 1)) :
    n * (n - 1) + upperLiftSlideHits n anchorOps 0 ≤
      upperLiftRotations anchorOps := by
  have hanchor := upperLoading_anchor_lower_bound hn anchor_periodic arrivals
    final_ge_birth (by simpa [anchor_final] using packed_cycle)
  have htrack := upperLiftRun_eq_start_add_rotations_sub_slideHits n anchorOps 0
  simp only [Int.zero_add] at htrack
  have hcast : ((n * (n - 1) : Nat) : Int) =
      (n : Int) * ((n : Int) - 1) := by
    have hn1 : 1 ≤ n := by omega
    simp [Nat.cast_sub hn1]
  have hbound : ((n * (n - 1) : Nat) : Int) ≤ upperLiftRun n anchorOps 0 := by
    simpa [hcast, anchor_final] using hanchor
  have hcost :
      n * (n - 1) + upperLiftSlideHits n anchorOps 0 ≤
        upperLiftRotations anchorOps := by
    rw [htrack] at hbound
    omega
  exact hcost

/-- Convert the lifted-coordinate identity `anchor = rotations - slides`
to a raw rotation budget, keeping the bound as a separate parameter. -/
theorem upperRotationCount_of_lifted_anchor {bound rotations slides : Nat}
    {anchor : Int} (hbound : (bound : Int) ≤ anchor)
    (htrack : anchor = (rotations : Int) - (slides : Int)) :
    bound + slides ≤ rotations := by
  rw [htrack] at hbound
  omega

end RSR2History
