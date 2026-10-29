import RegisteredAbsorptionChains.ActualFiberNormalForm
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n k t : ℕ} [NeZero n]

/-- Package a strictly increasing finite list of coordinates as a selected
subset, retaining its exact cardinality. -/
noncomputable def selectOfStrictMono {N r : ℕ}
    (f : Fin r → Fin N) (hf : StrictMono f) : Select N r := by
  refine ⟨Finset.univ.image f, ?_⟩
  rw [Finset.card_image_of_injective _ hf.injective]
  simp

theorem selectedValue_image (s : Select k t) :
    Finset.univ.image (selectedValue s) = s.1.image Fin.val := by
  ext v
  simp only [Finset.mem_image, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨i, rfl⟩
    refine ⟨(s.1.orderIsoOfFin s.2 i).val,
      (s.1.orderIsoOfFin s.2 i).property, rfl⟩
  · rintro ⟨x, hx, rfl⟩
    obtain ⟨i, hi⟩ := (s.1.orderIsoOfFin s.2).surjective
      (⟨x, hx⟩ : s.1)
    refine ⟨i, ?_⟩
    simpa [selectedValue] using congrArg
      (fun a : s.1 => a.val.val) hi

theorem selectedValue_selectOfStrictMono {N r : ℕ}
    (f : Fin r → Fin N) (hf : StrictMono f) (i : Fin r) :
    selectedValue (selectOfStrictMono f hf) i = (f i).val := by
  have hmono : StrictMono (fun j : Fin r => (f j).val) := by
    intro a b hab
    exact hf hab
  have himage : Finset.univ.image (selectedValue (selectOfStrictMono f hf)) =
      Finset.univ.image (fun j : Fin r => (f j).val) := by
    rw [selectedValue_image]
    ext v
    simp only [Finset.mem_image, Finset.mem_univ, true_and]
    constructor
    · rintro ⟨x, hx, rfl⟩
      obtain ⟨j, _, hj⟩ := Finset.mem_image.mp hx
      exact ⟨j, by simpa [hj]⟩
    · rintro ⟨j, rfl⟩
      exact ⟨f j, Finset.mem_image.mpr ⟨j, Finset.mem_univ _, rfl⟩, rfl⟩
  have heq := strictMono_fin_eq_of_image_eq
    (selectedValue (selectOfStrictMono f hf))
    (fun j : Fin r => (f j).val)
    (selectedValue_strict _) hmono himage
  exact congrFun heq i

theorem selectOfStrictMono_selectedValue {N r : ℕ}
    (s : Select N r) :
    selectOfStrictMono
      (fun i : Fin r => ⟨selectedValue s i, selectedValue_lt s i⟩)
      (by intro i j hij; exact selectedValue_strict s hij) = s := by
  apply Subtype.ext
  ext x
  simp only [selectOfStrictMono, Finset.mem_image, Finset.mem_univ,
    true_and]
  constructor
  · rintro ⟨i, hi⟩
    rw [← hi]
    change (s.1.orderIsoOfFin s.2 i).val ∈ s.1
    exact (s.1.orderIsoOfFin s.2 i).property
  · intro hx
    obtain ⟨i, hi⟩ := (s.1.orderIsoOfFin s.2).surjective
      (⟨x, hx⟩ : s.1)
    refine ⟨i, ?_⟩
    apply Fin.ext
    simpa [selectedValue] using congrArg
      (fun a : s.1 => a.val.val) hi

/-- Encode the strict interior cut positions relative to the carrier arc. -/
noncomputable def ValidFiberPlacement.innerCuts
    (data : ValidFiberPlacement n t) (u k : ℕ)
    (hu : data.u = u) (hv : data.v = u + k) :
    Fin (t - 1) → Fin (k - 1) := fun i => by
  let j : Fin (t + 1) := ⟨i.val + 1, by omega⟩
  have hzero : (⟨0, by omega⟩ : Fin (t + 1)) < j := by
    exact Fin.mk_lt_mk.mpr (by omega)
  have hlast : j < (⟨t, by omega⟩ : Fin (t + 1)) := by
    exact Fin.mk_lt_mk.mpr (by omega)
  have hlo := data.cut_strict hzero
  have hhi := data.cut_strict hlast
  rw [data.cut_zero, hu] at hlo
  rw [data.cut_last, hv] at hhi
  exact ⟨data.cut j - u - 1, by omega⟩

theorem ValidFiberPlacement.innerCuts_strict
    (data : ValidFiberPlacement n t) (u k : ℕ)
    (hu : data.u = u) (hv : data.v = u + k) :
    StrictMono (data.innerCuts u k hu hv) := by
  intro i j hij
  have hstep : data.cut (⟨i.val + 1, by omega⟩ : Fin (t + 1)) <
      data.cut (⟨j.val + 1, by omega⟩ : Fin (t + 1)) :=
    data.cut_strict (Fin.mk_lt_mk.mpr (by omega))
  have hlowi : u < data.cut ⟨i.val + 1, by omega⟩ := by
    have h := data.cut_strict
      (show (⟨0, by omega⟩ : Fin (t + 1)) < ⟨i.val + 1, by omega⟩ from
        Fin.mk_lt_mk.mpr (by omega))
    rw [data.cut_zero, hu] at h
    exact h
  change data.cut ⟨i.val + 1, by omega⟩ - u - 1 <
    data.cut ⟨j.val + 1, by omega⟩ - u - 1
  omega

/-- Encode the occupied sites other than the carrier site by their positive
clockwise offsets, shifted into `Fin (n-1)`. -/
noncomputable def ValidFiberPlacement.innerOffsets
    (data : ValidFiberPlacement n t) : Fin t → Fin (n - 1) := fun i => by
  let j : Fin (t + 1) := ⟨i.val + 1, by omega⟩
  have hpositive : 0 < data.offset j := by
    have h := data.offset_strict
      (show (⟨0, by omega⟩ : Fin (t + 1)) < j from
        Fin.mk_lt_mk.mpr (by omega))
    rw [data.offset_zero] at h
    exact h
  exact ⟨data.offset j - 1, by have := data.offset_lt j; omega⟩

theorem ValidFiberPlacement.innerOffsets_strict
    (data : ValidFiberPlacement n t) :
    StrictMono data.innerOffsets := by
  intro i j hij
  have hstep : data.offset (⟨i.val + 1, by omega⟩ : Fin (t + 1)) <
      data.offset (⟨j.val + 1, by omega⟩ : Fin (t + 1)) :=
    data.offset_strict (Fin.mk_lt_mk.mpr (by omega))
  have hpositive : 0 < data.offset ⟨i.val + 1, by omega⟩ := by
    have h := data.offset_strict
      (show (⟨0, by omega⟩ : Fin (t + 1)) < ⟨i.val + 1, by omega⟩ from
        Fin.mk_lt_mk.mpr (by omega))
    rw [data.offset_zero] at h
    exact h
  change data.offset ⟨i.val + 1, by omega⟩ - 1 <
    data.offset ⟨j.val + 1, by omega⟩ - 1
  omega

/-- The finite rank tuple recovered from a typed target, with no execution
search. Its phase is the integer representative of the carrier site. -/
noncomputable def ValidFiberPlacement.toRankParams
    (data : ValidFiberPlacement n t) (u k : ℕ)
    (hu : data.u = u) (hv : data.v = u + k) :
    RankFiberParams n k t :=
  (⟨data.q.val, data.q.val_lt⟩,
    selectOfStrictMono (data.innerCuts u k hu hv)
      (data.innerCuts_strict u k hu hv),
    selectOfStrictMono data.innerOffsets data.innerOffsets_strict)

theorem ValidFiberPlacement.rankCuts_toRankParams
    (data : ValidFiberPlacement n t) (u k : ℕ)
    (hu : data.u = u) (hv : data.v = u + k) :
    rankCuts u (data.toRankParams u k hu hv).2.1 = data.cut := by
  funext i
  by_cases hzero : i.val = 0
  · have hieq : i = ⟨0, by omega⟩ := Fin.ext hzero
    rw [hieq]
    simp only [rankCuts, if_pos rfl]
    exact hu.symm.trans data.cut_zero.symm
  by_cases hlast : i.val = t
  · have hieq : i = ⟨t, by omega⟩ := Fin.ext hlast
    rw [hieq]
    have ht := data.ht
    simp only [rankCuts, dif_neg (by omega : ¬ t = 0), if_pos rfl]
    exact hv.symm.trans data.cut_last.symm
  have hi : 0 < i.val ∧ i.val < t := by omega
  let j : Fin (t - 1) := ⟨i.val - 1, by omega⟩
  have hindex : (⟨j.val + 1, by omega⟩ : Fin (t + 1)) = i := by
    apply Fin.ext
    change i.val - 1 + 1 = i.val
    omega
  have hsel := selectedValue_selectOfStrictMono
    (data.innerCuts u k hu hv) (data.innerCuts_strict u k hu hv) j
  have hsel' : selectedValue
      (data.toRankParams u k hu hv).2.1 j = data.cut i - u - 1 := by
    simpa [ValidFiberPlacement.toRankParams,
      ValidFiberPlacement.innerCuts, j, hindex] using hsel
  have hlow : u < data.cut i := by
    have h := data.cut_strict
      (show (⟨0, by omega⟩ : Fin (t + 1)) < i from
        Fin.mk_lt_mk.mpr (by omega))
    rw [data.cut_zero, hu] at h
    exact h
  simp only [rankCuts, dif_neg hzero, dif_neg hlast]
  have hidx : (⟨i.val - 1, by omega⟩ : Fin (t - 1)) = j := rfl
  rw [hidx, hsel']
  omega

theorem ValidFiberPlacement.rankOffsets_toRankParams
    (data : ValidFiberPlacement n t) (u k : ℕ)
    (hu : data.u = u) (hv : data.v = u + k) :
    rankOffsets (data.toRankParams u k hu hv).2.2 = data.offset := by
  funext i
  by_cases hzero : i.val = 0
  · have hieq : i = ⟨0, by omega⟩ := Fin.ext hzero
    rw [hieq]
    simp only [rankOffsets, if_pos rfl]
    exact data.offset_zero.symm
  have hi : 0 < i.val := by omega
  let j : Fin t := ⟨i.val - 1, by omega⟩
  have hindex : (⟨j.val + 1, by omega⟩ : Fin (t + 1)) = i := by
    apply Fin.ext
    change i.val - 1 + 1 = i.val
    omega
  have hsel := selectedValue_selectOfStrictMono
    data.innerOffsets data.innerOffsets_strict j
  have hsel' : selectedValue
      (data.toRankParams u k hu hv).2.2 j = data.offset i - 1 := by
    simpa [ValidFiberPlacement.toRankParams,
      ValidFiberPlacement.innerOffsets, j, hindex] using hsel
  have hpositive : 0 < data.offset i := by
    have h := data.offset_strict
      (show (⟨0, by omega⟩ : Fin (t + 1)) < i from
        Fin.mk_lt_mk.mpr (by omega))
    rw [data.offset_zero] at h
    exact h
  simp only [rankOffsets, dif_neg hzero]
  have hidx : (⟨i.val - 1, by omega⟩ : Fin t) = j := rfl
  rw [hidx, hsel']
  omega

@[ext] theorem ValidFiberPlacement.ext_fields
    (a b : ValidFiberPlacement n t)
    (hu : a.u = b.u) (hv : a.v = b.v)
    (hcut : a.cut = b.cut) (hq : a.q = b.q)
    (hoff : a.offset = b.offset) : a = b := by
  cases a with
  | mk hta ua va hua huva hvna ca cza cla csa qa oa oza osa ola =>
    cases b with
    | mk htb ub vb hub huvb hvnb cb czb clb csb qb ob ozb osb olb =>
      cases hu
      cases hv
      cases hcut
      cases hq
      cases hoff
      rfl

/-- Full normalization of a typed fixed-rank fiber target: its finite
rank tuple decodes back to the identical target record. -/
theorem ValidFiberPlacement.of_toRankParams
    (data : ValidFiberPlacement n t) (u k : ℕ)
    (hu : data.u = u) (hv : data.v = u + k) :
    ValidFiberPlacement.ofRankParams u (by rw [← hu]; exact data.hu)
      (by rw [← hv]; exact data.hvn)
      (by have := data.huv; omega) data.ht
      (data.toRankParams u k hu hv) = data := by
  have hcuts := data.rankCuts_toRankParams u k hu hv
  have hoffsets := data.rankOffsets_toRankParams u k hu hv
  apply ValidFiberPlacement.ext_fields
  · exact hu.symm
  · exact hv.symm
  · exact hcuts
  · simp [ValidFiberPlacement.ofRankParams,
      ValidFiberPlacement.toRankParams, ZMod.natCast_zmod_val]
  · exact hoffsets

/-- The finite rank tuple has no redundant encoding: extracting its cuts,
phase and occupied offsets after decoding returns the original tuple. -/
theorem ValidFiberPlacement.to_ofRankParams
    (u : ℕ) (hu : 0 < u) (huk : u + k ≤ n)
    (hk : 0 < k) (ht : 0 < t)
    (params : RankFiberParams n k t) :
    (ValidFiberPlacement.ofRankParams u hu huk hk ht params).toRankParams
      u k rfl rfl = params := by
  apply Prod.ext
  · apply Fin.ext
    simp [ValidFiberPlacement.toRankParams,
      ValidFiberPlacement.ofRankParams, ZMod.val_natCast,
      Nat.mod_eq_of_lt params.1.isLt]
  · apply Prod.ext
    · have hcuts :
        (ValidFiberPlacement.ofRankParams u hu huk hk ht params).innerCuts
          u k rfl rfl =
          (fun i : Fin (t - 1) =>
            ⟨selectedValue params.2.1 i, selectedValue_lt params.2.1 i⟩) := by
          funext i
          apply Fin.ext
          have hi : 0 < i.val + 1 ∧ i.val + 1 < t := by omega
          have hidx : (⟨i.val + 1 - 1, by omega⟩ : Fin (t - 1)) = i := by
            apply Fin.ext
            change i.val + 1 - 1 = i.val
            omega
          simp only [ValidFiberPlacement.innerCuts,
            ValidFiberPlacement.ofRankParams, rankCuts,
            dif_neg (by omega : ¬ i.val + 1 = 0),
            dif_neg (by omega : ¬ i.val + 1 = t)]
          rw [hidx]
          omega
      simp only [ValidFiberPlacement.toRankParams, hcuts]
      exact selectOfStrictMono_selectedValue params.2.1
    · have hoffsets :
        (ValidFiberPlacement.ofRankParams u hu huk hk ht params).innerOffsets =
          (fun i : Fin t =>
            ⟨selectedValue params.2.2 i, selectedValue_lt params.2.2 i⟩) := by
          funext i
          apply Fin.ext
          have hidx : (⟨i.val + 1 - 1, by omega⟩ : Fin t) = i := by
            apply Fin.ext
            change i.val + 1 - 1 = i.val
            omega
          simp only [ValidFiberPlacement.innerOffsets,
            ValidFiberPlacement.ofRankParams, rankOffsets,
            dif_neg (by omega : ¬ i.val + 1 = 0)]
          rw [hidx]
          omega
      simp only [ValidFiberPlacement.toRankParams, hoffsets]
      exact selectOfStrictMono_selectedValue params.2.2

/-- Every typed target carries its own exact source-cut naming. This is the
bridge from arbitrary valid target data to uniqueness at a concrete site. -/
noncomputable def ValidFiberPlacement.asCutNamed
    (data : ValidFiberPlacement n t) (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi) :
    CutNamed f data.toLegal := by
  refine {
    count := by have := data.ht; omega
    carrier := ?_
    cut := fun i => if hi : i < t + 1 then data.cut ⟨i, hi⟩ else data.v
    cut_zero := ?_
    cut_last := ?_
    cut_step := ?_
    outside := ?_
  }
  · rw [data.toLegal_block]
    have hidx : (ZMod.finEquiv (t + 1)).symm (0 : ZMod (t + 1)) =
        ⟨0, Nat.zero_lt_succ t⟩ := by
      simpa only [Nat.cast_zero] using
        (finEquiv_symm_natCast (r := t + 1) 0 (Nat.zero_lt_succ t))
    rw [hidx, data.blockFin_zero]
    exact fiber_carrier_eq_frontier f data hu hv
  · change data.cut (⟨0, Nat.zero_lt_succ t⟩ : Fin (t + 1)) = f.lo
    exact data.cut_zero.trans hu
  · simp [data.cut_last, hv]
  · intro i hi
    simp only [dif_pos (show i < t + 1 by omega), dif_pos hi]
    exact data.cut_strict (Fin.mk_lt_mk.mpr (by omega))
  · intro i hi1 hir
    rw [data.toLegal_block]
    have hidx : (ZMod.finEquiv (t + 1)).symm (i : ZMod (t + 1)) =
        ⟨i, hir⟩ := finEquiv_symm_natCast i hir
    rw [hidx]
    have hzero : i ≠ 0 := by omega
    simp only [ValidFiberPlacement.blockFin, dif_neg hzero]
    let j : Fin t := ⟨i - 1, by omega⟩
    rw [data.outside_eq_sourceInterval j]
    have hnext : (⟨j.val + 1, by omega⟩ : Fin (t + 1)) =
        ⟨i, hir⟩ := by
      apply Fin.ext
      change i - 1 + 1 = i
      omega
    rw [hnext]
    simp only [dif_pos (show i - 1 < t + 1 by omega),
      dif_pos hir]
    rfl

theorem ValidFiberPlacement.of_asCutNamed
    (data : ValidFiberPlacement n t) (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi) :
    (data.asCutNamed f hu hv).toValidFiberPlacement
      data.toLegal_positive (by rw [← hu, ← hv]; exact data.huv) = data := by
  apply ValidFiberPlacement.ext_fields
  · exact hu.symm
  · exact hv.symm
  · funext i
    change (if hi : i.val < t + 1 then data.cut ⟨i.val, hi⟩ else data.v) =
      data.cut i
    simp [i.isLt]
  · change data.toLegal.position 0 = data.q
    rw [data.toLegal_position]
    have hidx : (ZMod.finEquiv (t + 1)).symm (0 : ZMod (t + 1)) =
        ⟨0, Nat.zero_lt_succ t⟩ := by
      simpa only [Nat.cast_zero] using
        (finEquiv_symm_natCast (r := t + 1) 0 (Nat.zero_lt_succ t))
    rw [hidx, data.siteFin_zero]
  · funext i
    change data.toLegal.offset i.val = data.offset i
    simp only [LegalNamedPlacement.offset, if_pos i.isLt]
    rw [data.toLegal_position, data.toLegal_position]
    have hidx : (ZMod.finEquiv (t + 1)).symm
        (i.val : ZMod (t + 1)) = i := by
      simpa using finEquiv_symm_natCast i.val i.isLt
    have hzero : (ZMod.finEquiv (t + 1)).symm (0 : ZMod (t + 1)) =
        ⟨0, Nat.zero_lt_succ t⟩ := by
      simpa only [Nat.cast_zero] using
        (finEquiv_symm_natCast (r := t + 1) 0 (Nat.zero_lt_succ t))
    rw [hidx, hzero]
    exact data.siteFin_offset i

/-- The concrete target determines the full cut/site record once the decoded
carrier arc is fixed. The proof uses source-key ordering, not a cardinality
argument or an existential choice of names. -/
theorem ValidFiberPlacement.target_injective_fixed
    (u k : ℕ) (hu2 : 2 ≤ u) (huk : u + k ≤ n)
    (first second : ValidFiberPlacement n t)
    (hu1 : first.u = u) (hv1 : first.v = u + k)
    (hu2' : second.u = u) (hv2 : second.v = u + k)
    (h : first.target = second.target) : first = second := by
  let f : CheckpointSourceFrontier n := {
    lo := u
    hi := u + k
    lo_valid := hu2
    noncrossing := by omega
    hi_valid := huk
  }
  have hfirst : first.u = f.lo := hu1
  have hfirstV : first.v = f.hi := hv1
  have hsecond : second.u = f.lo := hu2'
  have hsecondV : second.v = f.hi := hv2
  have hremain : f.lo < f.hi := by
    have := first.huv
    dsimp [f]
    omega
  have hnamed : first.toLegal.placed = second.toLegal.placed := h
  have heq := (first.asCutNamed f hfirst hfirstV).same_placement_fiber_data
    (second.asCutNamed f hsecond hsecondV)
    first.toLegal_positive second.toLegal_positive hremain hnamed
  exact (first.of_asCutNamed f hfirst hfirstV).symm.trans
    (heq.trans (second.of_asCutNamed f hsecond hsecondV))

theorem selectedValue_injective {N r : ℕ} (first second : Select N r)
    (h : selectedValue first = selectedValue second) : first = second := by
  calc
    first = selectOfStrictMono
        (fun i : Fin r => ⟨selectedValue first i, selectedValue_lt first i⟩)
        (by intro i j hij; exact selectedValue_strict first hij) :=
      (selectOfStrictMono_selectedValue first).symm
    _ = selectOfStrictMono
        (fun i : Fin r => ⟨selectedValue second i, selectedValue_lt second i⟩)
        (by intro i j hij; exact selectedValue_strict second hij) := by
      congr 1
      funext i
      apply Fin.ext
      exact congrFun h i
    _ = second := selectOfStrictMono_selectedValue second

theorem rankCuts_injective (u : ℕ) (first second : Select (k - 1) (t - 1))
    (h : rankCuts u first = rankCuts u second) : first = second := by
  apply selectedValue_injective
  funext i
  have hpoint := congrFun h (⟨i.val + 1, by omega⟩ : Fin (t + 1))
  have hzero : i.val + 1 ≠ 0 := by omega
  have hlast : i.val + 1 ≠ t := by omega
  simp only [rankCuts, dif_neg hzero, dif_neg hlast] at hpoint
  have hidx : (⟨i.val + 1 - 1, by omega⟩ : Fin (t - 1)) = i := by
    apply Fin.ext
    change i.val + 1 - 1 = i.val
    omega
  rw [hidx] at hpoint
  omega

theorem rankOffsets_injective (first second : Select (n - 1) t)
    (h : rankOffsets first = rankOffsets second) : first = second := by
  apply selectedValue_injective
  funext i
  have hpoint := congrFun h (⟨i.val + 1, by omega⟩ : Fin (t + 1))
  have hzero : i.val + 1 ≠ 0 := by omega
  simp only [rankOffsets, dif_neg hzero] at hpoint
  have hidx : (⟨i.val + 1 - 1, by omega⟩ : Fin t) = i := by
    apply Fin.ext
    change i.val + 1 - 1 = i.val
    omega
  rw [hidx] at hpoint
  omega

theorem rank_params_target_injective
    (u k : ℕ) (hu2 : 2 ≤ u) (huk : u + k ≤ n)
    (hk : 0 < k) (ht : 0 < t)
    (first second : RankFiberParams n k t)
    (h : (ValidFiberPlacement.ofRankParams u (by omega) huk hk ht first).target =
      (ValidFiberPlacement.ofRankParams u (by omega) huk hk ht second).target) :
    first = second := by
  let d1 := ValidFiberPlacement.ofRankParams u (by omega : 0 < u)
    huk hk ht first
  let d2 := ValidFiberPlacement.ofRankParams u (by omega : 0 < u)
    huk hk ht second
  have hd : d1 = d2 :=
    ValidFiberPlacement.target_injective_fixed u k hu2 huk d1 d2
      rfl rfl rfl rfl h
  have hphase := congrArg ValidFiberPlacement.q hd
  have hcuts := congrArg ValidFiberPlacement.cut hd
  have hoffsets := congrArg ValidFiberPlacement.offset hd
  apply Prod.ext
  · apply Fin.ext
    have hv := congrArg ZMod.val hphase
    simpa [d1, d2, ValidFiberPlacement.ofRankParams,
      ZMod.val_natCast, Nat.mod_eq_of_lt first.1.isLt,
      Nat.mod_eq_of_lt second.1.isLt] using hv
  · apply Prod.ext
    · apply rankCuts_injective u
      simpa [d1, d2, ValidFiberPlacement.ofRankParams] using hcuts
    · apply rankOffsets_injective
      simpa [d1, d2, ValidFiberPlacement.ofRankParams] using hoffsets

theorem ValidFiberPlacement.target_rank_eq
    {t₁ t₂ : ℕ} (first : ValidFiberPlacement n t₁)
    (second : ValidFiberPlacement n t₂)
    (h : first.target = second.target) : t₁ = t₂ := by
  have hfirst : (placedBlocks first.target).card = t₁ + 1 :=
    first.toLegal.blocks_card
  have hsecond : (placedBlocks second.target).card = t₂ + 1 :=
    second.toLegal.blocks_card
  rw [h] at hfirst
  omega

/-- Both the rank and every finite parameter are determined by the literal
target placement, not only by its block-counting formula. -/
theorem rank_params_target_unique
    (u k : ℕ) (hu2 : 2 ≤ u) (huk : u + k ≤ n)
    (hk : 0 < k)
    {t₁ t₂ : ℕ} (ht₁ : 0 < t₁) (ht₂ : 0 < t₂)
    (first : RankFiberParams n k t₁)
    (second : RankFiberParams n k t₂)
    (h : (ValidFiberPlacement.ofRankParams u (by omega) huk hk ht₁ first).target =
      (ValidFiberPlacement.ofRankParams u (by omega) huk hk ht₂ second).target) :
    (⟨t₁, first⟩ : Σ t, RankFiberParams n k t) = ⟨t₂, second⟩ := by
  have hrank := ValidFiberPlacement.target_rank_eq
    (ValidFiberPlacement.ofRankParams u (by omega) huk hk ht₁ first)
    (ValidFiberPlacement.ofRankParams u (by omega) huk hk ht₂ second) h
  cases hrank
  have hparams := rank_params_target_injective u k hu2 huk hk ht₁
    first second h
  cases hparams
  rfl

/-- Reverse existence with the native finite tuple. The same actual endpoint
first gives a typed target, and that target is then encoded without any
additional reachability choice. -/
theorem actual_fiber_rank_normal_form
    (word : List Letter) (hn : 2 ≤ n)
    (c : Code (n - 2))
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (hchain :
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn)
    (hremaining :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi) :
    ∃ (t : ℕ) (ht : 0 < t)
      (params : RankFiberParams n
        ((decodeCode c hn).frontier.hi - (decodeCode c hn).frontier.lo) t),
      (run (selectedPair n) (singletonExecution n) word).placed =
        (ValidFiberPlacement.ofRankParams
          (decodeCode c hn).frontier.lo
          (by have := (decodeCode c hn).frontier.lo_valid; omega)
          (by have := (decodeCode c hn).frontier.hi_valid
              have := (decodeCode c hn).frontier.noncrossing; omega)
          (by omega) ht params).target := by
  obtain ⟨t, data, hu, hv, hplace⟩ :=
    actual_fiber_normal_form word hn c hregistered hchain hremaining
  let f := (decodeCode c hn).frontier
  let u := f.lo
  let k := f.hi - f.lo
  have heq : u + k = f.hi := by
    dsimp [u, k]
    have := f.noncrossing
    omega
  let params := data.toRankParams u k hu (by rw [heq]; exact hv)
  refine ⟨t, data.ht, params, ?_⟩
  have hdecode := data.of_toRankParams u k hu (by rw [heq]; exact hv)
  exact hplace.trans (congrArg ValidFiberPlacement.target hdecode).symm

/-- Positive-rank finite parameters, retaining the proof that the outside
partition has at least one block. -/
abbrev PositiveRankFiberParams (n k : ℕ) :=
  {p : Σ t : ℕ, RankFiberParams n k t // 0 < p.1}

/-- Literal placements attained by generated histories with the fixed
source-addressed selected chain. The origin is only required to be registered;
the separate origin-classification question is not hidden in this type. -/
abbrev ActualFixedChainPlacements (c : Code (n - 2)) (hn : 2 ≤ n) :=
  {P : Placement n (Finset (ZMod n)) //
    ∃ word : List Letter,
      let s := run (selectedPair n) (singletonExecution n) word
      s.origin.isSome = true ∧ s.chain = decodeChain c hn ∧ s.placed = P}

noncomputable def rankTupleTarget
    (u k : ℕ) (hu : 0 < u) (huk : u + k ≤ n) (hk : 0 < k)
    (p : PositiveRankFiberParams n k) :
    Placement n (Finset (ZMod n)) :=
  (ValidFiberPlacement.ofRankParams u hu huk hk p.2 p.1.2).target

theorem rankTupleTarget_injective
    (u k : ℕ) (hu2 : 2 ≤ u) (huk : u + k ≤ n) (hk : 0 < k) :
    Function.Injective (rankTupleTarget u k (by omega) huk hk) := by
  intro first second h
  apply Subtype.ext
  exact rank_params_target_unique u k hu2 huk hk first.2 second.2
    first.1.2 second.1.2 h

/-- The non-full-carrier part of Theorem 4.2 at the level of literal
placements: every rank tuple has one generated witness, and every generated
endpoint has exactly one rank tuple. Full summaries additionally require the
separate origin check. -/
noncomputable def actualFixedChainPlacementEquiv
    (c : Code (n - 2)) (hn : 2 ≤ n)
    (hremaining :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi) :
    PositiveRankFiberParams n
      ((decodeCode c hn).frontier.hi - (decodeCode c hn).frontier.lo) ≃
      ActualFixedChainPlacements c hn := by
  let f := (decodeCode c hn).frontier
  let u := f.lo
  let k := f.hi - f.lo
  have hu : 0 < u := by have := f.lo_valid; omega
  have hu2 : 2 ≤ u := f.lo_valid
  have huk : u + k ≤ n := by
    have hnoncross := f.noncrossing
    have hhiValid := f.hi_valid
    change f.lo + (f.hi - f.lo) ≤ n
    omega
  have hk : 0 < k := by
    change 0 < f.hi - f.lo
    exact Nat.sub_pos_of_lt hremaining
  have hlo : u = f.lo := rfl
  have hhi : u + k = f.hi := by
    have := f.noncrossing
    dsimp [u, k]
    omega
  refine Equiv.ofBijective
    (fun p => (⟨rankTupleTarget u k hu huk hk p, ?_⟩ :
      ActualFixedChainPlacements c hn)) ?_
  · obtain ⟨word, hw⟩ := code_rank_params_reachable c hn
      u hu huk hk p.2 p.1.2 hlo hhi
    refine ⟨word, ?_⟩
    dsimp at hw ⊢
    refine ⟨?_, hw.2.1, hw.2.2⟩
    rw [hw.1]
    rw [registration_origin hn]
    rfl
  · constructor
    · intro first second h
      apply rankTupleTarget_injective u k hu2 huk hk
      exact congrArg Subtype.val h
    · intro P
      obtain ⟨word, hword⟩ := P.2
      dsimp at hword
      obtain ⟨t, ht, params, hplace⟩ :=
        actual_fiber_rank_normal_form word hn c hword.1 hword.2.1 hremaining
      refine ⟨⟨⟨t, params⟩, ht⟩, ?_⟩
      apply Subtype.ext
      exact hplace.symm.trans hword.2.2

end RegisteredAbsorptionChains
