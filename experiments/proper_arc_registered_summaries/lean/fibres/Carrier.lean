import converse.ActualChainConverse
import RegisteredAbsorptionChains.FiberParamInverse

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def outsideCount {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) : ℕ :=
  (decodeCanonical hr v).frontier.hi-(decodeCanonical hr v).frontier.lo

theorem outsideCount_eq {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :
    outsideCount hr v=n-r-lastCheckpoint v (n-r) le_rfl := by
  have htotal := (decodeCanonical hr v).frontier.remaining_plus_absorbed
  rw [(decodeCanonical hr v).frontier.remaining_card] at htotal
  have habs := decodePrefix_absorbed hr v (n-r) le_rfl
  change (decodeCanonical hr v).frontier.absorbed=_ at habs
  dsimp [outsideCount]
  omega

def renamePlacement (e : ZMod n ≃ ZMod n) (P : Placement n (Finset (ZMod n))) :=
  fun q => (P q).map (Finset.image e)

theorem renamePlacement_injective (e : ZMod n ≃ ZMod n) :
    Function.Injective (renamePlacement e) := by
  intro P Q h
  funext q
  have hq := congrFun h q
  have hi := congrArg (Option.map (Finset.image e.symm)) hq
  simpa [renamePlacement, Option.map_map, Finset.image_image, Function.comp_def] using hi

/-- The retained carrier read in the reverse induction identifies the current
actual packet. This works from an arbitrary ordered unregistered start. -/
theorem canonical_code_carrier {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (start : Execution n (ZMod n)) (word : List Letter) (v : Code (n-r))
    (ordered : SourceOrdered start.placed) (origin : start.origin=none) (chain : start.chain=[])
    (registered : (run (arc 0 r) start word).origin.isSome=true)
    (decoded : (run (arc 0 r) start word).chain=decodeCanonicalChain hr v) :
    ∃ q, (run (arc 0 r) start word).placed q=some (decodeCanonical hr v).frontier.carrier := by
  rcases actual_chain_trace_run hr start word ordered (Or.inl ⟨origin,chain⟩) with
    before | ⟨v', j, hj, hz, _, hc, hread, _, hcarrier⟩
  · simp [before.1] at registered
  · have hs := decodePrefix_skip hr v' j hj (n-r) le_rfl (by omega)
      (by intro i hji _; exact hz i hji)
    have heq : v'=v := decodeCanonicalChain_injective hr (hs.2.trans hc.symm |>.trans decoded)
    obtain ⟨q, C, hC, _, hrecord⟩ := hcarrier
    have hCeq : C=(decodePrefix hr v' j hj).frontier.carrier :=
      Option.some.inj (hrecord.symm.trans hread)
    have hfull := congrArg CheckpointSourceFrontier.carrier hs.1
    refine ⟨q, ?_⟩
    simpa only [heq,decodeCanonical] using hC.trans (congrArg some (hCeq.trans hfull.symm))

theorem normalized_run (c : ZMod n) (r : ℕ) (word : List Letter) :
    renameExecution (sourceShift c) (run (arc 0 r) (alignedExecution (-c)) word)=
      run (arc c r) (singletonExecution n) word := by
  rw [rename_run, shift_arc, shift_aligned_seed]

theorem normalized_code_carrier (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (word : List Letter) (v : Code (n-r))
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true)
    (decoded : (run (arc c r) (singletonExecution n) word).chain=decodeChain c ⟨hr.1,hr.2.le⟩ v) :
    let s := run (arc 0 r) (alignedExecution (-c)) word
    SourceOrdered s.placed ∧ ∃ q, s.placed q=some (decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.carrier := by
  have hstart : SourceOrdered (alignedExecution (-c)).placed := by
    rw [← run_alignment (arc (0 : ZMod n) r) (-c)]
    exact run_ordered _ _ _ (by omega) singletonExecution_ordered
  have heq := normalized_run c r word
  have hreg : (run (arc 0 r) (alignedExecution (-c)) word).origin.isSome=true := by
    rw [← heq] at registered
    simpa only [renameExecution, Option.isSome_map] using registered
  have hc : (run (arc 0 r) (alignedExecution (-c)) word).chain=
      decodeCanonicalChain ⟨hr.1,hr.2.le⟩ v := by
    apply rename_chain_injective (sourceShift c)
    exact (congrArg (fun s : Execution n (ZMod n) => s.chain) heq).trans decoded
  exact ⟨run_ordered _ _ _ (by omega) hstart,
    canonical_code_carrier ⟨hr.1,hr.2.le⟩ _ word v hstart rfl rfl hreg hc⟩

theorem actual_code_carrier (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (word : List Letter) (v : Code (n-r))
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true)
    (decoded : (run (arc c r) (singletonExecution n) word).chain=decodeChain c ⟨hr.1,hr.2.le⟩ v) :
    ∃ q, (run (arc c r) (singletonExecution n) word).placed q=
      some (decodedCarrier c ⟨hr.1,hr.2.le⟩ v) := by
  obtain ⟨_, q, hq⟩ := normalized_code_carrier c hr word v registered decoded
  refine ⟨q, ?_⟩
  rw [← normalized_run c r word]
  simp only [renameExecution, hq, Option.map_some]
  rfl

theorem carrier_full_of_outside_zero {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r))
    (hk : outsideCount hr v=0) : (decodeCanonical hr v).frontier.carrier=Finset.univ := by
  rw [(decodeCanonical hr v).frontier.carrier_eq_compl_remaining]
  have hempty : (decodeCanonical hr v).frontier.remaining=∅ := by
    apply Finset.card_eq_zero.mp
    simpa only [CheckpointSourceFrontier.remaining_card,outsideCount] using hk
  simp [hempty]

end ProperArc.Chains
