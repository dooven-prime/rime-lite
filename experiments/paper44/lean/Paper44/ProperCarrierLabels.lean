import Paper44.ProperCarrierCompletion

/-! # Actual proper-carrier compatible labels

The carrier is a dependent index. Equal saturated labels at different current
carriers are never identified by this type. Its values are an image of actual
generated states, rather than an assumed set of legal syntactic prefixes.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

abbrev ProperCarrier (n : ℕ) [NeZero n] :=
  {f : CheckpointSourceFrontier n // f.lo < f.hi}

def ActualProperPrefixLabel (j : ℕ) (f : ProperCarrier n) :=
  {label : PrefixLabel (FusionRecord (ZMod n)) (FusionRecord (ZMod n)) //
    ∃ s : CircularState n, s.val.origin.isSome = true ∧
      (∃ q, s.val.placed q = some f.val.carrier) ∧ circularLabel j s.val = label}

def codePrefixLabel (hn : 3 ≤ n) (j : ℕ) (c : Code (n - 2)) :=
  retainedLabel j (canonicalOrigin n) (decodeChain c (by omega))

theorem actual_proper_code (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n)
    (label : ActualProperPrefixLabel j f) :
    ∃ c : Code (n - 2), (decodeCode c (by omega)).frontier = f.val ∧
      codePrefixLabel hn j c = label.val := by
  obtain ⟨s, hr, ⟨q, hq⟩, hl⟩ := label.property
  obtain ⟨w, hw⟩ := s.property
  have hr' : (run (selectedPair n) (singletonExecution n) w).origin.isSome = true := by
    simpa only [selectedPair, hw] using hr
  obtain ⟨c, hc⟩ := actual_chain_in_decode_range w (by omega) hr'
  obtain ⟨q', hq'⟩ := actual_code_carrier_at_site w (by omega) c hr' hc
  have hs := run_ordered (selectedPair n) (singletonExecution n) w
    (by omega) singletonExecution_ordered
  have hin : selectedPair n ⊆ f.val.carrier := by
    intro a ha; exact Finset.mem_union_left _ (Finset.mem_union_left _ ha)
  have hin' : selectedPair n ⊆ decodedCarrier c (by omega) := by
    intro a ha; exact Finset.mem_union_left _ (Finset.mem_union_left _ ha)
  have hq0 : (run (selectedPair n) (singletonExecution n) w).placed q = some f.val.carrier := by
    simpa only [selectedPair, hw] using hq
  have hC := (sourceOrdered_selected_packet_unique _ (selectedPair n) _ _ q q' hs
    ⟨0, by simp [selectedPair]⟩ hq0 hin hq' hin').2
  have hfront := (frontier_eq_of_carrier_eq_of_remaining f.val _ hC f.property).symm
  refine ⟨c, hfront, ?_⟩
  have ho := actual_registered_origin_unique w hn hr'
  rw [registration_origin (by omega)] at ho
  rw [← hl]
  have ho' : s.val.origin = some (canonicalOrigin n) := by
    simpa only [selectedPair, hw, canonicalOrigin] using ho
  have hc' : s.val.chain = decodeChain c (by omega) := by
    simpa only [selectedPair, hw] using hc
  simp only [codePrefixLabel, circularLabel, ho', hc']

/-- The complete chain is realized in the same execution as the requested
carrier and retained label. No statement here identifies different carriers. -/
theorem proper_code_label_reachable (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n)
    (c : Code (n - 2)) (hc : (decodeCode c (by omega)).frontier = f.val) :
    ∃ s : CircularState n, s.val.origin.isSome = true ∧
      (∃ q, s.val.placed q = some f.val.carrier) ∧
      circularLabel j s.val = codePrefixLabel hn j c := by
  obtain ⟨w, q, hq, ho, hchain, _⟩ := realize_clean_code_actual_carrier c (by omega)
  rw [registration_origin (by omega)] at ho
  refine ⟨⟨run {0, 1} (singletonExecution n) w, w, rfl⟩,
    ?_, ⟨q, ?_⟩, ?_⟩
  · change (run (selectedPair n) (singletonExecution n) w).origin.isSome = true
    rw [ho]; rfl
  · change (run (selectedPair n) (singletonExecution n) w).placed q = _
    simpa only [decodedCarrier, hc] using hq
  · change circularLabel j (run (selectedPair n) (singletonExecution n) w) = _
    rw [circularLabel, ho, hchain]
    rfl

/-- Every actual compatible label admits an actual full-chain representative
ending at exactly the prescribed current carrier. -/
theorem proper_label_representative (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n)
    (label : ActualProperPrefixLabel j f) :
    ∃ c : Code (n - 2), (decodeCode c (by omega)).frontier = f.val ∧
      codePrefixLabel hn j c = label.val ∧
      ∃ s : CircularState n, s.val.origin.isSome = true ∧
        s.val.chain = decodeChain c (by omega) ∧
        (∃ q, s.val.placed q = some f.val.carrier) ∧ circularLabel j s.val = label.val := by
  obtain ⟨c, hf, hl⟩ := actual_proper_code hn j f label
  obtain ⟨w, q, hq, ho, hchain, _⟩ := realize_clean_code_actual_carrier c (by omega)
  rw [registration_origin (by omega)] at ho
  refine ⟨c, hf, hl, ⟨run {0, 1} (singletonExecution n) w, w, rfl⟩,
    ?_, hchain, ⟨q, ?_⟩, ?_⟩
  · change (run (selectedPair n) (singletonExecution n) w).origin.isSome = true
    rw [ho]; rfl
  · change (run (selectedPair n) (singletonExecution n) w).placed q = _
    simpa only [decodedCarrier, hf] using hq
  · rw [← hl]
    change circularLabel j (run (selectedPair n) (singletonExecution n) w) = _
    rw [circularLabel, ho, hchain]
    rfl

end Paper44
