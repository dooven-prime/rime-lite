import converse.ActualPartner

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The reverse invariant permits arbitrary outside packets. A sparse code
appears only after the first actual registration. -/
def ActualChainTrace {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (s : Execution n (ZMod n)) : Prop :=
  (s.origin=none ∧ s.chain=[]) ∨
    ∃ (v : Code (n-r)) (j : ℕ) (hj : j ≤ n-r),
      (∀ i : Fin (n-r), j ≤ i.val → v i=none) ∧
      s.origin.isSome=true ∧ s.chain=(decodePrefix hr v j hj).chain ∧
      recordedCarrierResult s=some (decodePrefix hr v j hj).frontier.carrier ∧
      (decodePrefix hr v j hj).frontier.absorbed=r-2+j ∧
      RecordedCarrier (arc 0 r) s

theorem actual_chain_trace_step {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (s : Execution n (ZMod n)) (a : Letter) (ordered : SourceOrdered s.placed)
    (trace : ActualChainTrace hr s) : ActualChainTrace hr (step (arc 0 r) s a) := by
  have hn : 2 ≤ n := by omega
  rcases trace with ⟨ho, hc⟩ | ⟨v, j, hj, hz, hreg, hc, hread, habs, hcarrier⟩
  · cases a with
    | p => left; simpa [step, ho, hc]
    | d =>
        cases h0 : s.placed 0 with
        | none => left; simp [step, stepDefect, h0, ho, hc]
        | some U =>
            cases h1 : s.placed 1 with
            | none => left; simp [step, stepDefect, h0, h1, ho, hc]
            | some V =>
                by_cases hUV : U∪V=arc 0 r
                · right
                  let v : Code (n-r) := fun _ => none
                  have ho' : (stepDefect (arc 0 r) s).origin=some ⟨U,V,U∪V⟩ := by
                    simp [stepDefect, h0, h1, ho, hUV]
                  have hc' : (stepDefect (arc 0 r) s).chain=[] := by
                    simp [stepDefect, h0, h1, ho, hc]
                  have hbase : (decodePrefix hr v 0 (by omega)).frontier.carrier=arc 0 r :=
                    Prefix.initial_carrier r hr
                  have hread' : recordedCarrierResult (stepDefect (arc 0 r) s)=some (arc 0 r) := by
                    simp [recordedCarrierResult, ho', hc', hUV]
                  have hp : (stepDefect (arc 0 r) s).placed 0=some (arc 0 r) := by
                    simp [stepDefect_placed, fusionPlacement, h0, h1, hUV]
                  refine ⟨v, 0, by omega, ?_, ?_, ?_, ?_, ?_, ?_⟩
                  · intro i _; rfl
                  · simpa [step, ho']
                  · simpa [step, decodePrefix, Prefix.initial, hc']
                  · simpa [step, hbase] using hread'
                  · simp [decodePrefix, Prefix.initial, CheckpointSourceFrontier.absorbed]
                  · exact ⟨0, arc 0 r, hp, Finset.Subset.rfl, hread'⟩
                · left
                  simp [step, stepDefect, h0, h1, ho, hc, hUV]
  · have next := actual_registered_carrier_step s (arc 0 r) a hn ordered
      (canonical_arc_nonempty r hr) hreg hcarrier
    cases a with
    | p =>
        right
        refine ⟨v, j, hj, hz, next.1, ?_, ?_, habs, next.2⟩
        · simpa [step] using hc
        · simpa [step, recordedCarrierResult] using hread
    | d =>
        cases h0 : s.placed 0 with
        | none =>
            right
            refine ⟨v, j, hj, hz, next.1, ?_, ?_, habs, next.2⟩
            · simpa [step, stepDefect, h0] using hc
            · simpa [step, stepDefect, h0, recordedCarrierResult] using hread
        | some U =>
            cases h1 : s.placed 1 with
            | none =>
                right
                refine ⟨v, j, hj, hz, next.1, ?_, ?_, habs, next.2⟩
                · simpa [step, stepDefect, h0, h1] using hc
                · simpa [step, stepDefect, h0, h1, recordedCarrierResult] using hread
            | some V =>
                by_cases hsel : arc 0 r ⊆ U ∨ arc 0 r ⊆ V
                · obtain ⟨v', b, hb, _, hafter, hr', hc', hread', habs', hcarrier'⟩ :=
                    actual_step_extends_code hr s v j hj ordered hreg hcarrier hz hc hread habs U V h0 h1 hsel
                  exact Or.inr ⟨v', b, hb, hafter, by simpa [step] using hr',
                    by simpa [step] using hc', by simpa [step] using hread', habs',
                    by simpa [step] using hcarrier'⟩
                · right
                  have ho' : (stepDefect (arc 0 r) s).origin=s.origin := by
                    cases ho : s.origin with
                    | none => simp [ho] at hreg
                    | some rho => simp [stepDefect, h0, h1, ho]
                  have hc' : (stepDefect (arc 0 r) s).chain=s.chain := by
                    simp [stepDefect, h0, h1, hreg, hsel]
                  refine ⟨v, j, hj, hz, next.1, ?_, ?_, habs, next.2⟩
                  · simpa [step, hc'] using hc
                  · change recordedCarrierResult (stepDefect (arc 0 r) s)=_
                    unfold recordedCarrierResult at hread ⊢
                    rw [ho', hc']
                    exact hread

theorem actual_chain_trace_run {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (start : Execution n (ZMod n)) (word : List Letter)
    (ordered : SourceOrdered start.placed) (trace : ActualChainTrace hr start) :
    ActualChainTrace hr (run (arc 0 r) start word) := by
  induction word generalizing start with
  | nil => simpa [run] using trace
  | cons a word ih =>
      exact ih (step (arc 0 r) start a)
        (step_ordered (arc 0 r) start a (by omega) ordered)
        (actual_chain_trace_step hr start a ordered trace)

theorem canonical_actual_chain_range {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (start : Execution n (ZMod n)) (word : List Letter)
    (ordered : SourceOrdered start.placed) (origin : start.origin=none) (chain : start.chain=[])
    (registered : (run (arc 0 r) start word).origin.isSome=true) :
    ∃ v : Code (n-r), (run (arc 0 r) start word).chain=decodeCanonicalChain hr v := by
  rcases actual_chain_trace_run hr start word ordered (Or.inl ⟨origin, chain⟩) with
    before | ⟨v, j, hj, hz, _, hc, _, _, _⟩
  · simp [before.1] at registered
  · have hs := decodePrefix_skip hr v j hj (n-r) le_rfl (by omega)
      (by intro i hji _; exact hz i hji)
    exact ⟨v, hc.trans hs.2.symm⟩

theorem shift_aligned_seed (c : ZMod n) :
    renameExecution (sourceShift c) (alignedExecution (-c))=singletonExecution n := by
  simp [renameExecution, alignedExecution, singletonExecution, add_assoc]

/-- Every registered actual chain belongs to the proper-arc decoder range.
The start and every prefix are genuine raw executions; no clean admission is
imposed on the history being classified. -/
theorem actual_chain_in_decode_range (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (word : List Letter)
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true) :
    ∃ v : Code (n-r), (run (arc c r) (singletonExecution n) word).chain=
      decodeChain c ⟨hr.1, hr.2.le⟩ v := by
  let start := alignedExecution (-c)
  have hstart : SourceOrdered start.placed := by
    dsimp [start]
    rw [← run_alignment (arc (0 : ZMod n) r) (-c)]
    exact run_ordered _ _ _ (by omega) singletonExecution_ordered
  have heq : renameExecution (sourceShift c) (run (arc 0 r) start word)=
      run (arc c r) (singletonExecution n) word := by
    rw [rename_run, shift_arc, show renameExecution (sourceShift c) start=singletonExecution n from
      shift_aligned_seed c]
  have hreg : (run (arc 0 r) start word).origin.isSome=true := by
    rw [← heq] at registered
    simpa only [renameExecution, Option.isSome_map] using registered
  obtain ⟨v, hv⟩ := canonical_actual_chain_range ⟨hr.1, hr.2.le⟩ start word hstart rfl rfl hreg
  refine ⟨v, ?_⟩
  have hc := congrArg (fun s : Execution n (ZMod n) => s.chain) heq
  change (run (arc 0 r) start word).chain.map (renameRecord (sourceShift c)) = _ at hc
  rw [← hc, hv]
  rfl

end ProperArc.Chains
