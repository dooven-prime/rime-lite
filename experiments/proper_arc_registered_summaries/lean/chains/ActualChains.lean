import chains.CleanRealization
import chains.DecoderInjective
import classification.OriginExhaustive

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem renameRecord_symm (e : ZMod n ≃ ZMod n) (rho : FusionRecord (ZMod n)) :
    renameRecord e.symm (renameRecord e rho) = rho := by
  cases rho
  simp [renameRecord, Finset.image_image, Function.comp_def]

theorem rename_chain_injective (e : ZMod n ≃ ZMod n) :
    Function.Injective (List.map (renameRecord e)) := by
  intro A B h
  have hi := congrArg (List.map (renameRecord e.symm)) h
  simpa [List.map_map, Function.comp_def, renameRecord_symm] using hi

theorem decodeChain_injective (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) :
    Function.Injective (decodeChain c hr) := by
  intro v w h
  apply decodeCanonicalChain_injective hr
  exact rename_chain_injective (sourceShift c) h

/-- The code-independent source anchor is read at its actual atom `c`, not at
the canonical physical port zero. -/
def recordKeyAt (c : ZMod n) (r : ℕ) (rho : FusionRecord (ZMod n)) : ℕ × Bool :=
  (rho.result.card-r, c ∈ rho.left)

theorem shifted_recordKey (c : ZMod n) (r : ℕ) (rho : FusionRecord (ZMod n)) :
    recordKeyAt c r (renameRecord (sourceShift c) rho) = recordKey r rho := by
  have hc : c ∈ rho.left.image (sourceShift c) ↔ (0 : ZMod n) ∈ rho.left := by
    simp [Finset.mem_image]
  simp only [recordKeyAt, recordKey, renameRecord,
    Finset.card_image_of_injective _ (sourceShift c).injective, hc]

/-- Complete checkpoint positions and L/R port bindings are recoverable from
the literal source-addressed records of the translated decoder. -/
theorem decodeChain_keys (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (v : Code (n-r)) :
    (decodeChain c hr v).map (recordKeyAt c r) = keys v (n-r) le_rfl := by
  simp only [decodeChain, List.map_map, Function.comp_def, shifted_recordKey]
  exact decodePrefix_keys hr v (n-r) le_rfl

/-- Membership is witnessed by a real singleton-seed word at the specified
complete origin. No decoder-range or cleanliness premise is used here. -/
def ActualSelectedChains (c : ZMod n) (r t : ℕ) :=
  {A : List (FusionRecord (ZMod n)) // ∃ w : List Letter,
    (run (arc c r) (singletonExecution n) w).origin = some (originRecord c r t) ∧
    (run (arc c r) (singletonExecution n) w).chain = A}

noncomputable def codeEmbeddingActualSelectedChains (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) :
    Code (n-r) ↪ ActualSelectedChains c r (t.val+1) where
  toFun v := ⟨decodeChain c ⟨hr.1, hr.2.le⟩ v, by
    obtain ⟨w, ho, hchain, _, _⟩ := realize_clean_code c hr v (t.val+1)
      ⟨by omega, by have := t.isLt; omega⟩
    exact ⟨w, ho, hchain⟩⟩
  inj' := by
    intro v w h
    exact decodeChain_injective c ⟨hr.1, hr.2.le⟩ (congrArg Subtype.val h)

theorem codeEmbeddingActualSelectedChains_val (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r)) :
    (codeEmbeddingActualSelectedChains c hr t v).val =
      decodeChain c ⟨hr.1, hr.2.le⟩ v := rfl

theorem codeEmbeddingActualSelectedChains_clean (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r)) :
    ∃ w : List Letter,
      let s := run (arc c r) (singletonExecution n) w
      s.origin = some (originRecord c r (t.val+1)) ∧
      s.chain = (codeEmbeddingActualSelectedChains c hr t v).val ∧
      CleanOutside (decodedCarrier c ⟨hr.1, hr.2.le⟩ v) s ∧
      arc c r ⊆ decodedCarrier c ⟨hr.1, hr.2.le⟩ v :=
  realize_clean_code c hr v (t.val+1) ⟨by omega, by have := t.isLt; omega⟩

end ProperArc.Chains
