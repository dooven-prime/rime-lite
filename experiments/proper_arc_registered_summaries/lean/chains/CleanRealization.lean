import chains.Decoder
import chains.SourceTranslation

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- All fields refer to the same actual prefix, including the complete origin,
the batched selected records, and the currently present decoded carrier. -/
structure CleanPrefix {r : ℕ} (hr : 2 ≤ r ∧ r < n) (v : Code (n-r))
    (t j : ℕ) (hj : j ≤ n-r) (s : Execution n (ZMod n)) (w : List Letter) : Prop where
  actual : run (arc 0 r) (singletonExecution n) w = s
  origin : s.origin = some (originRecord 0 r t)
  chain : s.chain = (decodePrefix ⟨hr.1, hr.2.le⟩ v j hj).chain
  clean : CleanOutside (decodePrefix ⟨hr.1, hr.2.le⟩ v j hj).frontier.carrier s

theorem realize_clean_prefix {r : ℕ} (hr : 2 ≤ r ∧ r < n) (v : Code (n-r))
    (t : ℕ) (ht : 1 ≤ t ∧ t < r) :
    ∀ j (hj : j ≤ n-r), ∃ s w, CleanPrefix hr v t j hj s w := by
  intro j
  induction j with
  | zero =>
      intro hj
      refine ⟨⟨boundaryPlacement 0 r, some (originRecord 0 r t), []⟩,
        originWord 0 r t, run_originWord 0 r t hr.2 ht.1 ht.2, rfl, rfl, ?_⟩
      rw [show (decodePrefix ⟨hr.1, hr.2.le⟩ v 0 hj).frontier.carrier = arc 0 r from
        Prefix.initial_carrier r ⟨hr.1, hr.2.le⟩]
      exact boundary_clean 0 r
  | succ j ih =>
      intro hj
      obtain ⟨s, w, prev⟩ := ih (by omega)
      let f := (decodePrefix ⟨hr.1, hr.2.le⟩ v j (by omega)).frontier
      let i : Fin (n-r) := ⟨j, by omega⟩
      have hreach : ReachableExecution (arc 0 r) s := ⟨w, prev.actual⟩
      have hreg : s.origin.isSome = true := by rw [prev.origin]; rfl
      have hsel : (arc (0 : ZMod n) r).Nonempty := by
        refine ⟨0, ?_⟩
        rw [arc, mem_interval_iff 0 0 0 r hr.2.le]
        simp; omega
      have hin : arc (0 : ZMod n) r ⊆ f.carrier :=
        Prefix.inside r j hr.2.le _
      have hnext : f.absorbed < r-2+j+1 := by
        have := (decodePrefix ⟨hr.1, hr.2.le⟩ v j (by omega)).bound
        dsimp [f]; omega
      have hmax : r-2+j+1 ≤ n-2 := by omega
      cases hs : v i with
      | none =>
          refine ⟨s, w, prev.actual, prev.origin, ?_, ?_⟩
          · simpa [decodePrefix, Prefix.advance, i, hs] using prev.chain
          · simpa [decodePrefix, Prefix.advance, i, hs] using prev.clean
      | some side =>
          cases side with
          | false =>
              obtain ⟨suffix, _, ho, hc, hclean⟩ :=
                f.realizeL_checkpoint (arc 0 r) s hreach hreg hsel hin prev.clean
                  (r-2+j+1) hnext hmax
              refine ⟨run (arc 0 r) s suffix, w++suffix, ?_, ho.trans prev.origin, ?_, ?_⟩
              · rw [run_append, prev.actual]
              · simpa [decodePrefix, Prefix.advance, i, hs, f, prev.chain] using hc
              · simpa [decodePrefix, Prefix.advance, i, hs, f] using hclean
          | true =>
              obtain ⟨suffix, _, ho, hc, hclean⟩ :=
                f.realizeR_checkpoint (arc 0 r) s hreach hreg hsel hin prev.clean
                  (r-2+j+1) hnext hmax
              refine ⟨run (arc 0 r) s suffix, w++suffix, ?_, ho.trans prev.origin, ?_, ?_⟩
              · rw [run_append, prev.actual]
              · simpa [decodePrefix, Prefix.advance, i, hs, f, prev.chain] using hc
              · simpa [decodePrefix, Prefix.advance, i, hs, f] using hclean

def decodeChain (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :
    List (FusionRecord (ZMod n)) :=
  (decodeCanonicalChain hr v).map (renameRecord (sourceShift c))

def decodedCarrier (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :
    Finset (ZMod n) :=
  (decodeCanonical hr v).frontier.carrier.image (sourceShift c)

/-- Every proper-arc code has an actual singleton-seed witness at every origin
cut. Multi-atom partners are assembled outside the carrier before one selected
event; the inherited checkpoint theorem supplies that continuous word. -/
theorem realize_clean_code (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (v : Code (n-r)) (t : ℕ) (ht : 1 ≤ t ∧ t < r) :
    ∃ w : List Letter,
      let s := run (arc c r) (singletonExecution n) w
      s.origin = some (originRecord c r t) ∧
      s.chain = decodeChain c ⟨hr.1, hr.2.le⟩ v ∧
      CleanOutside (decodedCarrier c ⟨hr.1, hr.2.le⟩ v) s ∧
      arc c r ⊆ decodedCarrier c ⟨hr.1, hr.2.le⟩ v := by
  obtain ⟨s, w, h⟩ := realize_clean_prefix hr v t ht (n-r) le_rfl
  refine ⟨pWord (-c).val ++ w, ?_⟩
  have heq : run (arc c r) (singletonExecution n) (pWord (-c).val ++ w) =
      renameExecution (sourceShift c) s := by
    rw [run_append, run_alignment, ← shift_seed, ← shift_arc, ← rename_run, h.actual]
  dsimp only
  rw [heq]
  refine ⟨?_, ?_, ?_, ?_⟩
  · simp [renameExecution, h.origin, shift_origin]
  · change s.chain.map _ = _
    rw [h.chain]
    rfl
  · exact rename_clean _ _ _ h.clean
  · rw [← shift_arc]
    exact Finset.image_subset_image (Prefix.inside r (n-r) hr.2.le _)

end ProperArc.Chains
