import RegisteredAbsorptionChains.FiberTargetAdmission
import RegisteredAbsorptionChains.FiberParameters
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n k t : ℕ} [NeZero n]

/-- Zero-based, strictly increasing values of a selected finite subset. -/
noncomputable def selectedValue (s : Select k t) (i : Fin t) : ℕ :=
  ((s.1.orderIsoOfFin s.2 i).val : Fin k).val

theorem selectedValue_strict (s : Select k t) :
    StrictMono (selectedValue s) := by
  intro i j hij
  have h := (s.1.orderIsoOfFin s.2).strictMono hij
  exact h

theorem selectedValue_lt (s : Select k t) (i : Fin t) :
    selectedValue s i < k :=
  ((s.1.orderIsoOfFin s.2 i).val : Fin k).isLt

/-- Normalize the selected occupied offsets. Zero is the carrier position;
the remaining entries are one plus the sorted elements of `Select (n-1) t`. -/
noncomputable def rankOffsets (s : Select (n - 1) t) :
    Fin (t + 1) → ℕ := fun i =>
  if h : i.val = 0 then 0 else
    1 + selectedValue s ⟨i.val - 1, by omega⟩

omit [NeZero n] in
theorem rankOffsets_zero (s : Select (n - 1) t) :
    rankOffsets s ⟨0, Nat.zero_lt_succ t⟩ = 0 := by
  simp [rankOffsets]

omit [NeZero n] in
theorem rankOffsets_lt (s : Select (n - 1) t)
    (hn : 1 ≤ n) (i : Fin (t + 1)) :
    rankOffsets s i < n := by
  by_cases hi : i.val = 0
  · simp [rankOffsets, hi]
    omega
  · simp only [rankOffsets, dif_neg hi]
    have hval := selectedValue_lt s ⟨i.val - 1, by omega⟩
    omega

omit [NeZero n] in
theorem rankOffsets_strict (s : Select (n - 1) t) :
    StrictMono (rankOffsets s) := by
  intro i j hij
  have hval : i.val < j.val := hij
  by_cases hi : i.val = 0
  · have hj : j.val ≠ 0 := by omega
    simp [rankOffsets, hi, hj]
  · have hj : j.val ≠ 0 := by omega
    simp only [rankOffsets, dif_neg hi, dif_neg hj]
    have hidx : (⟨i.val - 1, by omega⟩ : Fin t) <
        (⟨j.val - 1, by omega⟩ : Fin t) :=
      Fin.mk_lt_mk.mpr (by omega)
    have hstrict := selectedValue_strict s hidx
    omega

/-- The `t-1` cut choices occupy the strict interior of the complement
interval `[u,u+k)`. Endpoints are inserted separately. -/
noncomputable def rankCuts (u : ℕ) (s : Select (k - 1) (t - 1)) :
    Fin (t + 1) → ℕ := fun i =>
  if hzero : i.val = 0 then u else
    if hlast : i.val = t then u + k else
      u + 1 + selectedValue s ⟨i.val - 1, by omega⟩

theorem rankCuts_zero (u : ℕ) (s : Select (k - 1) (t - 1)) :
    rankCuts u s ⟨0, Nat.zero_lt_succ t⟩ = u := by
  simp [rankCuts]

theorem rankCuts_last (u : ℕ) (s : Select (k - 1) (t - 1))
    (ht : 0 < t) :
    rankCuts u s ⟨t, Nat.lt_succ_self t⟩ = u + k := by
  simp [rankCuts, Nat.ne_of_gt ht]

theorem rankCuts_strict (u : ℕ) (s : Select (k - 1) (t - 1))
    (hk : 0 < k) (ht : 0 < t) :
    StrictMono (rankCuts u s) := by
  intro i j hij
  have hval : i.val < j.val := hij
  have hit : i.val ≤ t := by omega
  have hjt : j.val ≤ t := by omega
  by_cases hi0 : i.val = 0
  · have hj0 : j.val ≠ 0 := by omega
    by_cases hjlast : j.val = t
    · simp only [rankCuts, dif_pos hi0, dif_neg hj0, dif_pos hjlast]
      omega
    · simp only [rankCuts, dif_pos hi0, dif_neg hj0, dif_neg hjlast]
      omega
  · have hj0 : j.val ≠ 0 := by omega
    have hilast : i.val ≠ t := by omega
    by_cases hjlast : j.val = t
    · simp only [rankCuts, dif_neg hi0, dif_neg hj0,
        dif_neg hilast, dif_pos hjlast]
      have hsmall := selectedValue_lt s ⟨i.val - 1, by omega⟩
      omega
    · simp only [rankCuts, dif_neg hi0, dif_neg hj0,
        dif_neg hilast, dif_neg hjlast]
      have hidx : (⟨i.val - 1, by omega⟩ : Fin (t - 1)) <
          (⟨j.val - 1, by omega⟩ : Fin (t - 1)) :=
        Fin.mk_lt_mk.mpr (by omega)
      have hstrict := selectedValue_strict s hidx
      omega

/-- Decode the finite fixed-rank parameter tuple against a specified source
carrier arc `[0,u) ∪ [u+k,n)`. This is a combinatorial construction, not a
reachability assertion. -/
noncomputable def ValidFiberPlacement.ofRankParams
    (u : ℕ) (hu : 0 < u) (huk : u + k ≤ n)
    (hk : 0 < k) (ht : 0 < t)
    (params : RankFiberParams n k t) : ValidFiberPlacement n t where
  ht := ht
  u := u
  v := u + k
  hu := hu
  huv := by omega
  hvn := huk
  cut := rankCuts u params.2.1
  cut_zero := rankCuts_zero u params.2.1
  cut_last := rankCuts_last u params.2.1 ht
  cut_strict := rankCuts_strict u params.2.1 hk ht
  q := (params.1.val : ZMod n)
  offset := rankOffsets params.2.2
  offset_zero := rankOffsets_zero params.2.2
  offset_strict := rankOffsets_strict params.2.2
  offset_lt := by
    intro i
    exact rankOffsets_lt params.2.2 (by omega) i

/-- Native cut/phase/occupied-site parameters provide the target-side
positive-cycle witness without assuming an execution of the target. -/
theorem rankFiberParams_target_admit
    (u : ℕ) (hu : 0 < u) (huk : u + k ≤ n)
    (hk : 0 < k) (ht : 0 < t)
    (params : RankFiberParams n k t)
    (source : LegalNamedPlacement n (t + 1) (ZMod n))
    (source_order : source.PositivelyOrdered)
    (same_blocks : source.block =
      (ValidFiberPlacement.ofRankParams u hu huk hk ht params).toLegal.block) :
    SameOrientedBlockCycle (r := t + 1) source.placed
      (ValidFiberPlacement.ofRankParams u hu huk hk ht params).target := by
  exact (ValidFiberPlacement.ofRankParams u hu huk hk ht params)
    |>.same_cycle_with_source source source_order same_blocks

/-- Conditional placement adjustment after an independent actual history has
assembled precisely the named source blocks. -/
theorem rankFiberParams_realize_from_named_source
    (u : ℕ) (hu : 0 < u) (huk : u + k ≤ n)
    (hk : 0 < k) (ht : 0 < t)
    (params : RankFiberParams n k t)
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (source : LegalNamedPlacement n (t + 1) (ZMod n))
    (source_eq : s.placed = source.placed)
    (source_order : source.PositivelyOrdered)
    (same_blocks : source.block =
      (ValidFiberPlacement.ofRankParams u hu huk hk ht params).toLegal.block) :
    ∃ word : List Letter,
      run F s word = { s with placed :=
        (ValidFiberPlacement.ofRankParams u hu huk hk ht params).target } ∧
      FusionFree F s word := by
  exact (ValidFiberPlacement.ofRankParams u hu huk hk ht params)
    |>.realize_from_named_source F s source source_eq source_order same_blocks

end RegisteredAbsorptionChains
