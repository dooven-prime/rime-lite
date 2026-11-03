import FutureEvent.PlacementParameters
import RegisteredAbsorptionChains.FiberParamInverse

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem fiber_carrier_zero {t : ℕ} (data : ValidFiberPlacement n t) :
    (0 : ZMod n) ∈ data.carrier := by
  have hu := data.hu
  simp [ValidFiberPlacement.carrier, hu]

theorem fiber_target_carrier_recovery {t s : ℕ}
    (first : ValidFiberPlacement n t) (second : ValidFiberPlacement n s)
    (h : first.target = second.target) :
    first.carrier = second.carrier ∧ first.q = second.q := by
  have hsite : second.target first.q = some first.carrier := by
    rw [← h]
    simpa only [first.siteFin_zero, first.blockFin_zero] using
      first.target_at ⟨0, Nat.zero_lt_succ t⟩
  obtain ⟨i, hi⟩ := second.target_only_sites first.q (by rw [hsite]; simp)
  have hblock : second.blockFin i = first.carrier :=
    Option.some.inj ((second.target_at i).symm.trans (hi ▸ hsite))
  have hi0 : i = ⟨0, Nat.zero_lt_succ s⟩ := by
    by_contra hne
    have hdis := second.blockFin_disjoint i ⟨0, Nat.zero_lt_succ s⟩ hne
    have hz : (0 : ZMod n) ∈ second.blockFin i := by
      rw [hblock]
      exact fiber_carrier_zero first
    exact Finset.disjoint_left.mp hdis hz (by
      change (0 : ZMod n) ∈ second.carrier
      exact fiber_carrier_zero second)
  refine ⟨?_, ?_⟩
  · simpa only [hi0, second.blockFin_zero] using hblock.symm
  · simpa only [hi0, second.siteFin_zero] using hi.symm

theorem fiber_carrier_bounds_recovery {t s : ℕ}
    (first : ValidFiberPlacement n t) (second : ValidFiberPlacement n s)
    (h : first.carrier = second.carrier) : first.u = second.u ∧ first.v = second.v := by
  have hfuv := first.huv
  have hfvn := first.hvn
  have hsuv := second.huv
  have hsv := second.hvn
  have outside (a : ℕ) (ha : a < n) :
      (first.u ≤ a ∧ a < first.v) ↔ (second.u ≤ a ∧ a < second.v) := by
    have he := congrArg (fun C : Finset (ZMod n) => (a : ZMod n) ∈ C) h
    simp only [ValidFiberPlacement.carrier, Finset.mem_filter, Finset.mem_univ,
      true_and, ZMod.val_natCast_of_lt ha] at he
    have heiff := Iff.of_eq he
    omega
  have hu1 := (outside first.u (by omega)).mp (by omega)
  have hu2 := (outside second.u (by omega)).mpr (by omega)
  have hv1 := (outside (first.v - 1) (by omega)).mp (by omega)
  have hv2 := (outside (second.v - 1) (by omega)).mpr (by omega)
  omega

theorem fiber_target_nonterminal {t : ℕ} (data : ValidFiberPlacement n t)
    (state : Execution n (ZMod n)) (hp : state.placed = data.target) :
    ¬ RankOnePlacement state := by
  rintro ⟨q, hq⟩
  have hpos (i : Fin (t + 1)) : data.siteFin i = q := by
    have hi : placementOfMap (fun _ : ZMod n => q) (data.siteFin i) = some (data.blockFin i) := by
      rw [← hq, hp]
      exact data.target_at i
    have hf := (placementOfMap_some_iff (fun _ : ZMod n => q) _ _).mp hi
    obtain ⟨atom, ha⟩ := hf.2
    have hmem := hf.1.symm ▸ ha
    exact ((mem_sourceFiber (fun _ : ZMod n => q) atom _).mp hmem).symm
  let i0 : Fin (t + 1) := ⟨0, by omega⟩
  let i1 : Fin (t + 1) := ⟨1, by have := data.ht; omega⟩
  have he := data.siteFin_injective ((hpos i0).trans (hpos i1).symm)
  have hv := congrArg Fin.val he
  change 0 = 1 at hv
  omega

omit [NeZero n] in
theorem fiberTuple_rank_le {k t : ℕ} (hk : 0 < k) (ht : 0 < t)
    (params : RankFiberParams n k t) : t ≤ k := by
  have hbound := Finset.card_le_univ params.2.1.val
  rw [params.2.1.property] at hbound
  simp only [Fintype.card_fin] at hbound
  omega

theorem fiberTarget_transport {u v k l t s : ℕ}
    (hu : 0 < u) (huk : u + k ≤ n) (hk : 0 < k) (ht : 0 < t)
    (hv : 0 < v) (hvl : v + l ≤ n) (hl : 0 < l) (hs : 0 < s)
    (first : RankFiberParams n k t) (second : RankFiberParams n l s)
    (heu : u = v) (hek : k = l) (het : t = s) (hep : HEq first second) :
    (ValidFiberPlacement.ofRankParams u hu huk hk ht first).target =
      (ValidFiberPlacement.ofRankParams v hv hvl hl hs second).target := by
  cases heu
  cases hek
  cases het
  cases hep
  rfl

end FutureEvent
