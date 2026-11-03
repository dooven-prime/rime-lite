import FutureEvent.ActualSingletonNormalForm
import FutureEvent.ZeroCarrierAssembly
import FutureEvent.InitialCutEquiv

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem singleton_packet_source (f : ZMod n → ZMod n) (a q : ZMod n)
    (h : placementOfMap f q = some {a}) : SingletonSource f a := by
  have hf := (placementOfMap_some_iff f q {a}).mp h
  have haq : f a = q := (mem_sourceFiber f a q).mp (by rw [hf.1]; simp)
  apply (singletonSource_iff_fiber f a).mpr
  rw [haq]
  exact hf.1

noncomputable def registerableNativeTarget (hn : 3 ≤ n) (p : RegisterableNativeParams n) :=
  (registerableNativeData hn (Nat.succ_pos _) p.2).target

theorem registerableNativeTarget_reachable (hn : 3 ≤ n) (p : RegisterableNativeParams n) :
    ∃ s : Execution n (ZMod n), PairGenerated s ∧ PairRegisterable s ∧
      s.placed = registerableNativeTarget hn p := by
  let data := registerableNativeData hn (Nat.succ_pos _) p.2
  have hb := registerableNativeData_bounds hn (Nat.succ_pos _) p.2
  obtain ⟨s, hg, ho, hp⟩ := zero_carrier_target_reachable data hb.1 hb.2
  obtain ⟨lift, hlift⟩ := pairGenerated_sourceOrdered s (by omega) hg
  have h0 : placementOfMap lift.position (data.siteFin ⟨0, by omega⟩) = some {0} := by
    rw [← hlift, hp, data.target_at, data.blockFin_zero, singleton_zero_carrier data hb.1 hb.2]
  have h1 : placementOfMap lift.position (data.siteFin ⟨1, by omega⟩) = some {1} := by
    rw [← hlift, hp, data.target_at, singleton_one_outside data hn hb.1
      (registerableNativeData_cut_one hn (Nat.succ_pos _) p.2)]
  exact ⟨s, hg, (generated_registerable_iff_singletons s lift.position hn hg hlift ho).mpr
    ⟨singleton_packet_source _ _ _ h0, singleton_packet_source _ _ _ h1⟩, hp⟩

theorem positive_rank_tuple_injective {k t : ℕ} (u : ℕ) (hu : 0 < u)
    (huk : u + k ≤ n) (hk : 0 < k) (ht : 0 < t)
    (p q : RankFiberParams n k t)
    (h : (ValidFiberPlacement.ofRankParams u hu huk hk ht p).target =
      (ValidFiberPlacement.ofRankParams u hu huk hk ht q).target) : p = q := by
  have hd := positive_fiber_target_injective
    (ValidFiberPlacement.ofRankParams u hu huk hk ht p)
    (ValidFiberPlacement.ofRankParams u hu huk hk ht q) h
  have hphase := congrArg ValidFiberPlacement.q hd
  have hcuts := congrArg ValidFiberPlacement.cut hd
  have hoffsets := congrArg ValidFiberPlacement.offset hd
  apply Prod.ext
  · apply Fin.ext
    have hv := congrArg ZMod.val hphase
    simpa [ValidFiberPlacement.ofRankParams, ZMod.val_natCast, Nat.mod_eq_of_lt p.1.isLt,
      Nat.mod_eq_of_lt q.1.isLt] using hv
  · apply Prod.ext
    · exact rankCuts_injective u p.2.1 q.2.1 hcuts
    · exact rankOffsets_injective p.2.2 q.2.2 hoffsets

theorem registerableNativeTarget_injective (hn : 3 ≤ n) :
    Function.Injective (registerableNativeTarget (n := n) hn) := by
  rintro ⟨i, phase, cuts, sites⟩ ⟨j, phase', cuts', sites'⟩ h
  have hr : (i.val + 1) + 1 = (j.val + 1) + 1 := ValidFiberPlacement.target_rank_eq
    (registerableNativeData hn (Nat.succ_pos _) (phase, cuts, sites))
    (registerableNativeData hn (Nat.succ_pos _) (phase', cuts', sites')) h
  have hij : i = j := Fin.ext (by omega)
  cases hij
  have htup := positive_rank_tuple_injective 1 (by omega) (by omega : 1 + (n - 1) ≤ n)
    (by omega : 0 < n - 1) (Nat.succ_pos (i.val + 1))
    (phase, cuts.val, sites) (phase', cuts'.val, sites') h
  have hphase : phase = phase' := congrArg Prod.fst htup
  have hcuts : cuts = cuts' := Subtype.ext (congrArg (fun p => p.2.1) htup)
  have hsites : sites = sites' := congrArg (fun p => p.2.2) htup
  cases hphase
  cases hcuts
  cases hsites
  rfl

theorem nativeCuts_admitted {t : ℕ} (hn : 3 ≤ n) (ht : 0 < t)
    (data : ValidFiberPlacement n (t + 1)) (hu : data.u = 1) (hv : data.v = n)
    (hc : data.cut ⟨1, by omega⟩ = 2) :
    ∃ i ∈ (data.toRankParams 1 (n - 1) hu (by omega)).2.1.val, i.val = 0 := by
  let params := data.toRankParams 1 (n - 1) hu (by omega)
  have hh := congrFun (data.rankCuts_toRankParams 1 (n - 1) hu (by omega)) ⟨1, by omega⟩
  change rankCuts (k := n - 1) (t := t + 1) 1 params.2.1 ⟨1, by omega⟩ = _ at hh
  rw [hc] at hh
  simp only [rankCuts, dif_neg (by omega : ¬1 = 0), dif_neg (by omega : ¬1 = t + 1)] at hh
  change 1 + 1 + selectedValue params.2.1 ⟨0, by omega⟩ = 2 at hh
  have hv0 : selectedValue params.2.1 ⟨0, by omega⟩ = 0 := by omega
  obtain ⟨j, hj, hval⟩ := Finset.mem_image.mp (show 0 ∈ params.2.1.val.image Fin.val from by
    rw [← selectedValue_image]
    exact Finset.mem_image.mpr ⟨⟨0, by omega⟩, Finset.mem_univ _, hv0⟩)
  exact ⟨j, hj, hval⟩

theorem registerableNativeTarget_covers_actual (hn : 3 ≤ n) (P : RegisterablePlacements n) :
    ∃ p : RegisterableNativeParams n, registerableNativeTarget hn p = P.val := by
  obtain ⟨s, hg, hr, hp⟩ := P.property
  obtain ⟨t, data, ht, hu, hv, hc, htarget⟩ := actual_singleton_normal_form hn s hg hr
  let params := data.toRankParams 1 (n - 1) hu (by omega)
  have hbound := fiberTuple_rank_le (by omega : 0 < n - 1) data.ht params
  let i : Fin (n - 2) := ⟨t - 1, by omega⟩
  have hit : i.val + 1 = t := by dsimp [i]; omega
  let cuts : InitialCutSelect ((n - 1) - 1) t :=
    ⟨params.2.1, nativeCuts_admitted hn ht data hu hv hc⟩
  let row : RegisterableNativeParam n t := (params.1, cuts, params.2.2)
  let row' : RegisterableNativeParam n (i.val + 1) := by simpa only [hit] using row
  have hrow : HEq row' row := by dsimp [row']; simp
  have transport : ∀ {a b : ℕ} (ha : 0 < a) (hb : 0 < b)
      (first : RegisterableNativeParam n a) (second : RegisterableNativeParam n b),
      a = b → HEq first second →
      (registerableNativeData hn ha first).target = (registerableNativeData hn hb second).target := by
    intro a b ha hb first second he hp
    cases he
    cases hp
    rfl
  have heq : registerableNativeTarget hn ⟨i, row'⟩ = (registerableNativeData hn ht row).target :=
    transport (Nat.succ_pos _) ht row' row hit hrow
  refine ⟨⟨i, row'⟩, heq.trans ?_⟩
  have he := data.of_toRankParams 1 (n - 1) hu (by omega)
  change (ValidFiberPlacement.ofRankParams 1 _ _ _ _ params).target = P.val
  rw [he]
  exact htarget.trans hp

noncomputable def registerableNativePlacement (hn : 3 ≤ n) (p : RegisterableNativeParams n) :
    RegisterablePlacements n := ⟨registerableNativeTarget hn p, registerableNativeTarget_reachable hn p⟩

noncomputable def registerableNativePlacementEquiv (hn : 3 ≤ n) :
    RegisterableNativeParams n ≃ RegisterablePlacements n :=
  Equiv.ofBijective (registerableNativePlacement hn) ⟨by
    intro p q h
    exact registerableNativeTarget_injective hn (congrArg Subtype.val h), by
    intro P
    obtain ⟨p, hp⟩ := registerableNativeTarget_covers_actual hn P
    exact ⟨p, Subtype.ext hp⟩⟩

noncomputable def registerablePlacementParamsEquiv (hn : 3 ≤ n) :
    RegisterableParams n ≃ RegisterablePlacements n :=
  (registerableNativeEquiv n hn).trans (registerableNativePlacementEquiv hn)

end FutureEvent
