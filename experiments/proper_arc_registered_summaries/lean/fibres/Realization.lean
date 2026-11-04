import fibres.NormalForm

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The fibre consists of literal placements of actual histories at this
fixed complete origin and selected chain. -/
def ActualCodePlacements (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (t : Fin (r-1)) (v : Code (n-r)) :=
  {P : Placement n (Finset (ZMod n)) // ∃ word : List Letter,
    let s := run (arc c r) (singletonExecution n) word
    s.origin=some (originRecord c r (t.val+1)) ∧
    s.chain=decodeChain c ⟨hr.1,hr.2.le⟩ v ∧ s.placed=P}

theorem canonical_fiber_target_reachable {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (v : Code (n-r)) (t : Fin (r-1)) {b : ℕ} (data : ValidFiberPlacement n b)
    (hu : data.u=(decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.lo)
    (hv : data.v=(decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.hi) :
    ∃ word : List Letter,
      let s := run (arc 0 r) (singletonExecution n) word
      s.origin=some (originRecord 0 r (t.val+1)) ∧
      s.chain=decodeCanonicalChain ⟨hr.1,hr.2.le⟩ v ∧ s.placed=data.target := by
  obtain ⟨s,pre,h⟩ := realize_clean_prefix hr v (t.val+1) ⟨by omega,by have := t.isLt; omega⟩ (n-r) le_rfl
  have hreg : s.origin.isSome=true := by rw [h.origin]; rfl
  obtain ⟨suffix,hs⟩ := allCut_realize_target (arc 0 r) data
    (decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier hu hv s ⟨pre,h.actual⟩ hreg
    (canonical_arc_nonempty r ⟨hr.1,hr.2.le⟩)
    (Prefix.inside r (n-r) hr.2.le _) h.clean
  refine ⟨pre++suffix,?_⟩
  dsimp only
  rw [run_append,h.actual,hs]
  exact ⟨h.origin,h.chain,rfl⟩

theorem fiber_target_reachable (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (v : Code (n-r)) (t : Fin (r-1)) {b : ℕ} (data : ValidFiberPlacement n b)
    (hu : data.u=(decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.lo)
    (hv : data.v=(decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.hi) :
    ∃ word : List Letter,
      let s := run (arc c r) (singletonExecution n) word
      s.origin=some (originRecord c r (t.val+1)) ∧
      s.chain=decodeChain c ⟨hr.1,hr.2.le⟩ v ∧
      s.placed=renamePlacement (sourceShift c) data.target := by
  obtain ⟨word,ho,hc,hp⟩ := canonical_fiber_target_reachable hr v t data hu hv
  refine ⟨pWord (-c).val++word,?_⟩
  have heq : run (arc c r) (singletonExecution n) (pWord (-c).val++word)=
      renameExecution (sourceShift c) (run (arc 0 r) (singletonExecution n) word) := by
    rw [run_append,run_alignment,← shift_seed,← shift_arc,← rename_run]
  dsimp only
  rw [heq]
  exact ⟨by simp [renameExecution,ho,shift_origin],
    by simp only [renameExecution,hc]; rfl,by simp only [renameExecution,hp]; rfl⟩

noncomputable def positiveFiberData {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r))
    (hk : 0 < outsideCount hr v) (p : FiberParams n (outsideCount hr v)) :
    ValidFiberPlacement n (p.1.val+1) :=
  ValidFiberPlacement.ofRankParams (decodeCanonical hr v).frontier.lo
    (by have := (decodeCanonical hr v).frontier.lo_valid; omega)
    (by have := (decodeCanonical hr v).frontier.noncrossing
        have := (decodeCanonical hr v).frontier.hi_valid; dsimp [outsideCount]; omega)
    hk (by omega) p.2

noncomputable def positiveFiberTarget (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (v : Code (n-r)) (hk : 0 < outsideCount hr v) (p : FiberParams n (outsideCount hr v)) :=
  renamePlacement (sourceShift c) (positiveFiberData hr v hk p).target

theorem positiveFiberTarget_reachable (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (t : Fin (r-1)) (v : Code (n-r)) (hk : 0 < outsideCount ⟨hr.1,hr.2.le⟩ v)
    (p : FiberParams n (outsideCount ⟨hr.1,hr.2.le⟩ v)) :
    ∃ word : List Letter,
      let s := run (arc c r) (singletonExecution n) word
      s.origin=some (originRecord c r (t.val+1)) ∧
      s.chain=decodeChain c ⟨hr.1,hr.2.le⟩ v ∧
      s.placed=positiveFiberTarget c ⟨hr.1,hr.2.le⟩ v hk p := by
  apply fiber_target_reachable c hr v t (positiveFiberData ⟨hr.1,hr.2.le⟩ v hk p) rfl
  change (decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.lo+outsideCount ⟨hr.1,hr.2.le⟩ v = _
  have := (decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.noncrossing
  dsimp [outsideCount]
  omega

theorem decodedCarrier_full (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (v : Code (n-r)) (hk : outsideCount hr v=0) : decodedCarrier c hr v=Finset.univ := by
  unfold decodedCarrier
  rw [carrier_full_of_outside_zero hr v hk,Finset.image_univ_of_surjective (sourceShift c).surjective]

theorem full_carrier_target_reachable (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (t : Fin (r-1)) (v : Code (n-r)) (hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0) (q : ZMod n) :
    ∃ word : List Letter,
      let s := run (arc c r) (singletonExecution n) word
      s.origin=some (originRecord c r (t.val+1)) ∧
      s.chain=decodeChain c ⟨hr.1,hr.2.le⟩ v ∧
      s.placed=fullCarrierPlacement (Finset.univ : Finset (ZMod n)) q := by
  obtain ⟨pre,ho,hc,hclean,_⟩ := realize_clean_code c hr v (t.val+1) ⟨by omega,by have := t.isLt; omega⟩
  obtain ⟨q0,hq0⟩ := hclean.1
  rw [decodedCarrier_full c ⟨hr.1,hr.2.le⟩ v hk] at hq0
  have hP := sourceOrdered_fullCarrier _ (run_ordered _ _ _ (by omega) singletonExecution_ordered) q0 hq0
  obtain ⟨suffix,hs,_⟩ := realize_full_carrier_rotation (arc c r) Finset.univ _ q0 q hP
  refine ⟨pre++suffix,?_⟩
  dsimp only
  rw [run_append,hs]
  exact ⟨ho,hc,rfl⟩

end ProperArc.Chains
