import FutureEvent.PlacementGeometry
import FutureEvent.CarrierCode

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

noncomputable def registeredParamData (_hn : 3 ≤ n) (p : RegisteredPlacementParams n) :
    ValidFiberPlacement n (p.2.2.1.val + 1) :=
  ValidFiberPlacement.ofRankParams (p.2.1.val + 2) (by omega)
    (by have := p.1.isLt; have := p.2.1.isLt; omega)
    (Nat.succ_pos _) (Nat.succ_pos _) p.2.2.2

noncomputable def registeredParamTarget (hn : 3 ≤ n) (p : RegisteredPlacementParams n) :
    Placement n (Finset (ZMod n)) := (registeredParamData hn p).target

theorem registeredParamTarget_reachable (hn : 3 ≤ n) (p : RegisteredPlacementParams n) :
    ∃ s : Execution n (ZMod n), PairGenerated s ∧ RegisteredNonterminal s ∧
      s.placed = registeredParamTarget hn p := by
  let u := p.2.1.val + 2
  let k := p.1.val + 1
  have hu : 2 ≤ u := by dsimp [u]; omega
  have huk : u + k ≤ n := by
    have := p.1.isLt
    have := p.2.1.isLt
    dsimp [u, k]
    omega
  let c := canonicalCarrierCode (n := n) u k
  have hc := canonicalCarrierCode_frontier (n := n) u k hu huk
  obtain ⟨word, ho, _, hp⟩ := code_rank_params_reachable c (by omega)
    u (by omega) huk (show 0 < k by dsimp [k]; omega)
    (Nat.succ_pos p.2.2.1.val) p.2.2.2 hc.1.symm hc.2.symm
  let s := run {0, 1} (singletonExecution n) word
  have hplace : s.placed = registeredParamTarget hn p := hp
  refine ⟨s, ⟨word, rfl⟩, ⟨?_, ?_⟩, hplace⟩
  · rw [show s.origin = (registrationExecution n).origin from ho, registration_origin (by omega)]
    rfl
  · exact fiber_target_nonterminal (registeredParamData hn p) s hplace

theorem registeredParamTarget_injective (hn : 3 ≤ n) :
    Function.Injective (registeredParamTarget (n := n) hn) := by
  rintro ⟨i, u, t, first⟩ ⟨j, v, s, second⟩ h
  have hc := (fiber_target_carrier_recovery
    (registeredParamData hn ⟨i, u, t, first⟩)
    (registeredParamData hn ⟨j, v, s, second⟩) h).1
  have hb := fiber_carrier_bounds_recovery
    (registeredParamData hn ⟨i, u, t, first⟩)
    (registeredParamData hn ⟨j, v, s, second⟩) hc
  have hu : u.val + 2 = v.val + 2 := hb.1
  have hv : u.val + 2 + (i.val + 1) = v.val + 2 + (j.val + 1) := hb.2
  have hij : i = j := Fin.ext (by omega)
  cases hij
  have huv : u = v := Fin.ext (by omega)
  cases huv
  have ht : t.val + 1 = s.val + 1 := ValidFiberPlacement.target_rank_eq
    (registeredParamData hn ⟨i, u, t, first⟩)
    (registeredParamData hn ⟨i, u, s, second⟩) h
  have hts : t = s := Fin.ext (by omega)
  cases hts
  have hp := rank_params_target_injective (u.val + 2) (i.val + 1) (by omega)
    (by have := u.isLt; have := i.isLt; omega)
    (Nat.succ_pos _) (Nat.succ_pos _) first second h
  cases hp
  rfl

theorem actual_registered_frontier_positive (word : List Letter) (hn : 3 ≤ n)
    (c : Code (n - 2))
    (hr : (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (hc : (run (selectedPair n) (singletonExecution n) word).chain = decodeChain c (by omega))
    (ht : ¬ RankOnePlacement (run (selectedPair n) (singletonExecution n) word)) :
    (decodeCode c (by omega)).frontier.lo < (decodeCode c (by omega)).frontier.hi := by
  let f := (decodeCode c (by omega)).frontier
  by_contra h
  have he : f.lo = f.hi := by have := f.noncrossing; change ¬ f.lo < f.hi at h; omega
  obtain ⟨q, hq⟩ := actual_code_carrier_at_site word (by omega) c hr hc
  have hfull : decodedCarrier c (by omega) = (Finset.univ : Finset (ZMod n)) := by
    ext a
    simp only [decodedCarrier]
    change a ∈ f.carrier ↔ a ∈ Finset.univ
    rw [f.mem_carrier_iff]
    simp only [Finset.mem_univ, iff_true]
    rw [← he]
    omega
  rw [hfull] at hq
  have hsource := sourceOrdered_fullCarrier _
    (run_ordered (selectedPair n) (singletonExecution n) word (by omega) singletonExecution_ordered) q hq
  have hconstant := placementOfMap_fullCarrier (fun _ : ZMod n => q) q
    (by ext a; simp)
  exact ht ⟨q, hsource.trans hconstant.symm⟩

theorem registeredParamTarget_covers_actual (hn : 3 ≤ n)
    (P : RegisteredNonterminalPlacements n) :
    ∃ p : RegisteredPlacementParams n, registeredParamTarget hn p = P.val := by
  obtain ⟨state, ⟨word, rfl⟩, hr, hp⟩ := P.property
  have hr' : (run (selectedPair n) (singletonExecution n) word).origin.isSome = true := hr.1
  obtain ⟨c, hc⟩ := actual_chain_in_decode_range word (by omega) hr'
  have hpositive := actual_registered_frontier_positive word hn c hr' hc hr.2
  obtain ⟨t, ht, params, hplace⟩ := actual_fiber_rank_normal_form word (by omega) c hr' hc hpositive
  let f := (decodeCode c (by omega)).frontier
  let k := f.hi - f.lo
  have hk : 0 < k := by dsimp [k]; exact Nat.sub_pos_of_lt hpositive
  have hkn : k ≤ n - 2 := by have := f.lo_valid; have := f.hi_valid; dsimp [k]; omega
  have htk : t ≤ k := fiberTuple_rank_le hk ht params
  have hu : f.lo - 2 < n - 1 - k := by
    have := f.lo_valid
    have := f.hi_valid
    have := f.noncrossing
    dsimp [k]
    omega
  let i : Fin (n - 2) := ⟨k - 1, by omega⟩
  let u : Fin (n - 1 - (i.val + 1)) := ⟨f.lo - 2, by dsimp [i]; omega⟩
  let j : Fin (i.val + 1) := ⟨t - 1, by dsimp [i]; omega⟩
  have hki : i.val + 1 = k := by dsimp [i]; omega
  have huj : u.val + 2 = f.lo := by have := f.lo_valid; dsimp [u]; omega
  have htj : j.val + 1 = t := by dsimp [j]; omega
  let params' : RankFiberParams n (i.val + 1) (j.val + 1) := by
    simpa only [hki, htj] using params
  refine ⟨⟨i, u, j, params'⟩, ?_⟩
  have htarget : registeredParamTarget hn ⟨i, u, j, params'⟩ =
      (ValidFiberPlacement.ofRankParams f.lo (by have := f.lo_valid; omega)
        (by have := f.noncrossing; have := f.hi_valid; dsimp [k]; omega)
        hk ht params).target := by
    have hparams : HEq params' params := by dsimp [params']; simp
    exact fiberTarget_transport _ _ _ _ _ _ _ _ params' params huj hki htj hparams
  rw [htarget]
  exact hplace.symm.trans hp

noncomputable def registeredParamsPlacement (hn : 3 ≤ n) (p : RegisteredPlacementParams n) :
    RegisteredNonterminalPlacements n :=
  ⟨registeredParamTarget hn p, registeredParamTarget_reachable hn p⟩

noncomputable def registeredPlacementParamsEquiv (hn : 3 ≤ n) :
    RegisteredPlacementParams n ≃ RegisteredNonterminalPlacements n :=
  Equiv.ofBijective (registeredParamsPlacement hn) ⟨by
    intro p q h
    exact registeredParamTarget_injective hn (congrArg Subtype.val h), by
    intro P
    obtain ⟨p, hp⟩ := registeredParamTarget_covers_actual hn P
    exact ⟨p, Subtype.ext hp⟩⟩

end FutureEvent
