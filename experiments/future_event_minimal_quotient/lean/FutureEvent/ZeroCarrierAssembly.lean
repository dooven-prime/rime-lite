import FutureEvent.IntervalAssembly
import FutureEvent.RegisterableData

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n t : ℕ} [NeZero n]

noncomputable def zeroPackedData (data : ValidFiberPlacement n t) : ValidFiberPlacement n t :=
  { data with
    q := 0
    offset := fun i => if hi : i.val = 0 then 0 else data.cut ⟨i.val - 1, by omega⟩
    offset_zero := by simp
    offset_strict := by
      intro i j hij
      have hj : j.val ≠ 0 := by have h : i.val < j.val := hij; omega
      simp only [dif_neg hj]
      by_cases hi : i.val = 0
      · rw [dif_pos hi]
        have h := (data.cut_bounds ⟨j.val - 1, by omega⟩).1
        have := data.hu
        omega
      · rw [dif_neg hi]
        exact data.cut_strict (Fin.mk_lt_mk.mpr (by have h : i.val < j.val := hij; omega))
    offset_lt := by
      intro i
      split_ifs with hi
      · exact Nat.pos_of_ne_zero (NeZero.ne n)
      · have h := data.cut_strict (show (⟨i.val - 1, by omega⟩ : Fin (t + 1)) < i
          from Fin.mk_lt_mk.mpr (by omega))
        have hh := (data.cut_bounds i).2.trans data.hvn
        omega }

def outsideMacro (data : ValidFiberPlacement n t) (i : Fin t) : List Letter :=
  sourceBlockWord (n := n) (data.cut ⟨i.val, by omega⟩) (data.cut ⟨i.val + 1, by omega⟩)

def outsideAssemblyWord (data : ValidFiberPlacement n t) : List Letter :=
  (List.finRange t).flatMap (outsideMacro data)

theorem outsideMacro_site (data : ValidFiberPlacement n t) (i : Fin t) (q : ZMod n) :
    siteWord (outsideMacro data i) q =
      if q ∈ data.outside i then (data.cut ⟨i.val, by omega⟩ : ZMod n) else q := by
  rw [outsideMacro, sourceBlockWord_site _ _
    (data.cut_strict (Fin.mk_lt_mk.mpr (by omega)))
    ((data.cut_bounds ⟨i.val + 1, by omega⟩).2.trans data.hvn)]
  rw [data.outside_eq_sourceInterval]

theorem outside_root_mem (data : ValidFiberPlacement n t) (i : Fin t) :
    (data.cut ⟨i.val, by omega⟩ : ZMod n) ∈ data.outside i := by
  have hl := data.cut_strict (show (⟨i.val, by omega⟩ : Fin (t + 1)) <
    ⟨i.val + 1, by omega⟩ from Fin.mk_lt_mk.mpr (by omega))
  have hh := (data.cut_bounds ⟨i.val + 1, by omega⟩).2.trans data.hvn
  have hn : data.cut ⟨i.val, by omega⟩ < n := by omega
  rw [data.outside_eq_sourceInterval, mem_sourceInterval_iff _ _ hh,
    ZMod.val_natCast_of_lt hn]
  omega

theorem outsideAssembly_site (data : ValidFiberPlacement n t) (i : Fin t) (q : ZMod n)
    (hq : q ∈ data.outside i) :
    siteWord (outsideAssemblyWord data) q = (data.cut ⟨i.val, by omega⟩ : ZMod n) := by
  have aux : ∀ indices : List (Fin t), ∀ q : ZMod n, q ∈ data.outside i →
      siteWord (indices.flatMap (outsideMacro data)) q =
        if i ∈ indices then (data.cut ⟨i.val, by omega⟩ : ZMod n) else q := by
    intro indices
    induction indices with
    | nil => intro q _; rfl
    | cons j rest ih =>
        intro q hq
        rw [List.flatMap_cons, siteWord_append, outsideMacro_site]
        by_cases he : i = j
        · subst j
          rw [if_pos hq, ih _ (outside_root_mem data i)]
          split_ifs <;> simp_all
        · have hnot : q ∉ data.outside j := fun hj =>
            Finset.disjoint_left.mp (data.outside_disjoint i j he) hq hj
          rw [if_neg hnot, ih q hq]
          simp [he]
  simpa [outsideAssemblyWord] using aux (List.finRange t) q hq

theorem outsideAssembly_zero (data : ValidFiberPlacement n t) :
    siteWord (outsideAssemblyWord data) (0 : ZMod n) = 0 := by
  apply flatMap_site_fixed
  intro i _
  rw [outsideMacro_site]
  have hnot : (0 : ZMod n) ∉ data.outside i := by
    have hl := (data.cut_bounds ⟨i.val, by omega⟩).1
    have hu := data.hu
    simp only [ValidFiberPlacement.outside, Finset.mem_filter, Finset.mem_univ, true_and,
      ZMod.val_zero]
    omega
  rw [if_neg hnot]

theorem singleton_seed_map :
    (singletonExecution n).placed = placementOfMap (fun a : ZMod n => a) := by
  funext q
  have hf : sourceFiber (fun a : ZMod n => a) q = {q} := by ext a; simp
  simp [singletonExecution, placementOfMap, hf]

theorem outsideAssembly_packed_target (data : ValidFiberPlacement n t) (hu : data.u = 1)
    (hv : data.v = n) :
    (run {0, 1} (singletonExecution n) (outsideAssemblyWord data)).placed =
      (zeroPackedData data).target := by
  have hn : 2 ≤ n := by have := data.huv; have := data.hvn; omega
  rw [atomSite_run {0, 1} (singletonExecution n) (fun a : ZMod n => a) _ hn singleton_seed_map]
  apply map_matches_legal (zeroPackedData data).toLegal
  intro i atom ha
  let j := (ZMod.finEquiv (t + 1)).symm i
  change atom ∈ (zeroPackedData data).blockFin j at ha
  change siteWord (outsideAssemblyWord data) atom = (zeroPackedData data).siteFin j
  by_cases hj : j.val = 0
  · have hcar : (zeroPackedData data).carrier = {0} :=
      singleton_zero_carrier (zeroPackedData data) hu hv
    simp only [ValidFiberPlacement.blockFin, dif_pos hj, hcar, Finset.mem_singleton] at ha
    subst atom
    rw [outsideAssembly_zero]
    have he : j = ⟨0, Nat.zero_lt_succ t⟩ := Fin.ext hj
    rw [he, ValidFiberPlacement.siteFin_zero]
    rfl
  · have hmem : atom ∈ data.outside ⟨j.val - 1, by omega⟩ := by
      simp only [ValidFiberPlacement.blockFin, dif_neg hj] at ha
      have he : (zeroPackedData data).outside ⟨j.val - 1, by omega⟩ =
          data.outside ⟨j.val - 1, by omega⟩ := by
        ext a
        simp [ValidFiberPlacement.outside, zeroPackedData]
      exact he ▸ ha
    have hs := outsideAssembly_site data ⟨j.val - 1, by omega⟩ atom hmem
    simpa only [ValidFiberPlacement.siteFin, zeroPackedData, dif_neg hj, zero_add] using hs

theorem zero_carrier_target_reachable (data : ValidFiberPlacement n t) (hu : data.u = 1)
    (hv : data.v = n) :
    ∃ s : Execution n (ZMod n), PairGenerated s ∧ s.origin = none ∧ s.placed = data.target := by
  have hn : 2 ≤ n := by have := data.huv; have := data.hvn; omega
  let word := outsideAssemblyWord data
  let start := run {0, 1} (singletonExecution n) word
  have hplaced : start.placed = (zeroPackedData data).toLegal.placed :=
    outsideAssembly_packed_target data hu hv
  obtain ⟨suffix, hsuffix, hfree⟩ := data.realize_from_named_source {0, 1} start
    (zeroPackedData data).toLegal hplaced (zeroPackedData data).toLegal_positive rfl
  have h0 : siteWord word (0 : ZMod n) = 0 := outsideAssembly_zero data
  have h1 : siteWord word (1 : ZMod n) = 1 := by
    let i : Fin t := ⟨0, data.ht⟩
    have hmem : (1 : ZMod n) ∈ data.outside i := by
      have hlt := data.cut_strict (show (⟨0, Nat.zero_lt_succ t⟩ : Fin (t + 1)) <
        ⟨1, by have := data.ht; omega⟩ from Fin.mk_lt_mk.mpr (by omega))
      rw [data.cut_zero, hu] at hlt
      have hval : (1 : ZMod n).val = 1 := by
        simpa only [Nat.cast_one] using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
      rw [data.outside_eq_sourceInterval, mem_sourceInterval_iff _ _
        ((data.cut_bounds ⟨i.val + 1, by omega⟩).2.trans data.hvn), hval]
      change data.cut ⟨0, Nat.zero_lt_succ t⟩ ≤ 1 ∧ 1 < data.cut ⟨1, by have := data.ht; omega⟩
      rw [data.cut_zero, hu]
      exact ⟨le_rfl, hlt⟩
    simpa only [i, data.cut_zero, hu, Nat.cast_one] using outsideAssembly_site data i 1 hmem
  have ho : start.origin = none := by
    cases horigin : start.origin with
    | none => rfl
    | some record =>
        have hc := run_registered_colocated (singletonExecution n) (fun a : ZMod n => a) word hn
          singleton_seed_map (by simp [singletonExecution]) (by change start.origin.isSome = true; rw [horigin]; rfl)
        rw [forwardMapRun_eq_siteWord, forwardMapRun_eq_siteWord, h0, h1] at hc
        have hbad := ZMod.one_eq_zero_iff.mp hc.symm
        omega
  have hrecords := fusionFree_records_and_trace {0, 1} start suffix hfree
  refine ⟨run {0, 1} (singletonExecution n) (word ++ suffix), ⟨word ++ suffix, rfl⟩, ?_, ?_⟩
  · rw [run_append]
    exact hrecords.1.trans ho
  · rw [run_append, hsuffix]

end FutureEvent
