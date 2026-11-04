import fibres.Realization

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem positiveFiberTarget_injective (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (v : Code (n-r)) (hk : 0 < outsideCount hr v) :
    Function.Injective (positiveFiberTarget c hr v hk) := by
  intro first second h
  have hcan := renamePlacement_injective (sourceShift c) h
  let f := (decodeCanonical hr v).frontier
  have huk : f.lo+outsideCount hr v ≤ n := by
    have := f.noncrossing
    have := f.hi_valid
    change f.lo+(f.hi-f.lo) ≤ n
    omega
  have hsigma := rank_params_target_unique f.lo (outsideCount hr v) f.lo_valid huk hk
    (by omega) (by omega) first.2 second.2 hcan
  rcases first with ⟨i,p⟩
  rcases second with ⟨j,q⟩
  have hij : i=j := Fin.ext (by have h := congrArg Sigma.fst hsigma; dsimp at h; omega)
  subst j
  have hpq : p=q := eq_of_heq (Sigma.mk.inj_iff.mp hsigma).2
  subst q
  rfl

theorem actual_fiber_params (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (word : List Letter) (v : Code (n-r))
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true)
    (decoded : (run (arc c r) (singletonExecution n) word).chain=decodeChain c ⟨hr.1,hr.2.le⟩ v)
    (hk : 0 < outsideCount ⟨hr.1,hr.2.le⟩ v) :
    ∃ p : FiberParams n (outsideCount ⟨hr.1,hr.2.le⟩ v),
      (run (arc c r) (singletonExecution n) word).placed=
        positiveFiberTarget c ⟨hr.1,hr.2.le⟩ v hk p := by
  obtain ⟨j,data,hu,hv,hP⟩ := actual_fiber_normal_form c hr word v registered decoded hk
  have ht := data.ht
  obtain ⟨i,hi⟩ : ∃ i, j=i+1 := ⟨j-1,by omega⟩
  subst j
  let f := (decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier
  let k := outsideCount ⟨hr.1,hr.2.le⟩ v
  have hsum : f.lo+k=f.hi := by
    have := f.noncrossing
    change f.lo+(f.hi-f.lo)=f.hi
    omega
  have hv' : data.v=f.lo+k := hv.trans hsum.symm
  let params := data.toRankParams f.lo k hu hv'
  have hibound : i+1 ≤ k := rank_params_outside_bound hk ht params
  let p : FiberParams n k := ⟨⟨i,by omega⟩,params⟩
  have hd : positiveFiberData ⟨hr.1,hr.2.le⟩ v hk p=data :=
    data.of_toRankParams f.lo k hu hv'
  refine ⟨p,?_⟩
  simpa only [positiveFiberTarget,hd] using hP

noncomputable def positivePlacementFibreEquiv (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : 0 < outsideCount ⟨hr.1,hr.2.le⟩ v) :
    FiberParams n (outsideCount ⟨hr.1,hr.2.le⟩ v) ≃ ActualCodePlacements c hr t v := by
  apply Equiv.ofBijective (fun p =>
    (⟨positiveFiberTarget c ⟨hr.1,hr.2.le⟩ v hk p,
      positiveFiberTarget_reachable c hr t v hk p⟩ : ActualCodePlacements c hr t v))
  constructor
  · intro first second h
    exact positiveFiberTarget_injective c ⟨hr.1,hr.2.le⟩ v hk (congrArg Subtype.val h)
  · intro P
    obtain ⟨word,ho,hc,hplaced⟩ := P.property
    have hreg : (run (arc c r) (singletonExecution n) word).origin.isSome=true := by rw [ho]; rfl
    obtain ⟨p,hp⟩ := actual_fiber_params c hr word v hreg hc hk
    exact ⟨p,Subtype.ext (hp.symm.trans hplaced)⟩

theorem positivePlacementFibreEquiv_val (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : 0 < outsideCount ⟨hr.1,hr.2.le⟩ v)
    (p : FiberParams n (outsideCount ⟨hr.1,hr.2.le⟩ v)) :
    (positivePlacementFibreEquiv c hr t v hk p).val=
      positiveFiberTarget c ⟨hr.1,hr.2.le⟩ v hk p := rfl

noncomputable def fullPlacementFibreEquiv (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0) :
    ZMod n ≃ ActualCodePlacements c hr t v := by
  apply Equiv.ofBijective (fun q =>
    (⟨fullCarrierPlacement Finset.univ q,full_carrier_target_reachable c hr t v hk q⟩ :
      ActualCodePlacements c hr t v))
  constructor
  · intro q q' h
    exact fullCarrierPlacement_injective Finset.univ (congrArg Subtype.val h)
  · intro P
    obtain ⟨word,ho,hc,hplaced⟩ := P.property
    have hreg : (run (arc c r) (singletonExecution n) word).origin.isSome=true := by rw [ho]; rfl
    obtain ⟨q,hq⟩ := actual_code_carrier c hr word v hreg hc
    rw [decodedCarrier_full c ⟨hr.1,hr.2.le⟩ v hk] at hq
    have hP := sourceOrdered_fullCarrier _ (run_ordered _ _ _ (by omega) singletonExecution_ordered) q hq
    exact ⟨q,Subtype.ext (hP.symm.trans hplaced)⟩

theorem fullPlacementFibreEquiv_val (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0) (q : ZMod n) :
    (fullPlacementFibreEquiv c hr t v hk q).val=fullCarrierPlacement Finset.univ q := rfl

/-- Finite native cut/phase/occupied-offset parameters, with an independent
single-packet phase branch when no outside source atoms remain. -/
def CodeFiberParams {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) : Type :=
  if outsideCount hr v=0 then ZMod n else FiberParams n (outsideCount hr v)

noncomputable def codePlacementFibreEquiv (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r)) :
    CodeFiberParams ⟨hr.1,hr.2.le⟩ v ≃ ActualCodePlacements c hr t v := by
  by_cases hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0
  · simpa only [CodeFiberParams,if_pos hk] using fullPlacementFibreEquiv c hr t v hk
  · simpa only [CodeFiberParams,if_neg hk] using
      positivePlacementFibreEquiv c hr t v (Nat.pos_of_ne_zero hk)

theorem card_actualCodePlacements (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r)) :
    Nat.card (ActualCodePlacements c hr t v)=
      n*(n+outsideCount ⟨hr.1,hr.2.le⟩ v-2).choose (outsideCount ⟨hr.1,hr.2.le⟩ v) := by
  rw [Nat.card_congr (codePlacementFibreEquiv c hr t v).symm]
  by_cases hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0
  · simp [CodeFiberParams,hk,Nat.card_eq_fintype_card]
  · simp only [CodeFiberParams,if_neg hk,Nat.card_eq_fintype_card]
    exact card_fiberParams n _ (by omega) (Nat.pos_of_ne_zero hk)

end ProperArc.Chains
