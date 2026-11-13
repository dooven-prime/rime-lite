import Paper44.TerminalDecoder

/-! # Terminal codes and the actual terminal-label image

The target is an image of real singleton-seed executions, not an abstract
well-formed-label type. Terminal phase is intentionally absent.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

def ActualTerminalLabel (n depth : ℕ) [NeZero n] :=
  {label : PrefixLabel (FusionRecord (ZMod n)) (FusionRecord (ZMod n)) //
    ∃ s : CircularState n, s.val.origin.isSome = true ∧
      RankOnePlacement s.val ∧ circularLabel depth s.val = label}

def canonicalOrigin (n : ℕ) : FusionRecord (ZMod n) :=
  ⟨{0}, {1}, selectedPair n⟩

theorem rankOne_packet_univ (s : Execution n (ZMod n))
    (ht : RankOnePlacement s) (q : ZMod n) (C : Finset (ZMod n))
    (hq : s.placed q = some C) : C = Finset.univ := by
  obtain ⟨r, hr⟩ := ht
  rw [hr] at hq
  obtain ⟨hC, hnonempty⟩ := (placementOfMap_some_iff (fun _ : ZMod n => r) q C).mp hq
  by_cases h : r = q
  · simpa [sourceFiber, h] using hC.symm
  · have hempty : sourceFiber (fun _ : ZMod n => r) q = ∅ := by simp [sourceFiber, h]
    rw [hempty] at hC
    exact False.elim (hnonempty.ne_empty hC.symm)

/-- Reverse range theorem: an actual registered terminal has an exact full code. -/
theorem actual_terminal_code (hn : 3 ≤ n) (s : CircularState n)
    (hr : s.val.origin.isSome = true) (ht : RankOnePlacement s.val) :
    ∃ c : Code (n - 2), c (lastCheckpoint hn) ≠ none ∧
      s.val.origin = some (canonicalOrigin n) ∧ s.val.chain = decodeChain c (by omega) := by
  obtain ⟨w, hw⟩ := s.property
  have hr' : (run (selectedPair n) (singletonExecution n) w).origin.isSome = true := by
    simpa only [selectedPair, hw] using hr
  obtain ⟨c, hc⟩ := actual_chain_in_decode_range w (by omega) hr'
  obtain ⟨q, hq⟩ := actual_code_carrier_at_site w (by omega) c hr' hc
  have hsite : s.val.placed q = some (decodedCarrier c (by omega)) := by
    simpa only [selectedPair, hw] using hq
  have hfull := rankOne_packet_univ s.val ht q _ hsite
  refine ⟨c, (decodedCarrier_full_iff_last c hn).mp hfull, ?_, ?_⟩
  · have ho := actual_registered_origin_unique w hn hr'
    rw [registration_origin (by omega)] at ho
    simpa only [selectedPair, hw, canonicalOrigin] using ho
  · simpa only [selectedPair, hw] using hc

/-- Every full code has an actual rank-one witness, with the exact old records. -/
theorem full_code_reachable (hn : 3 ≤ n) (c : Code (n - 2))
    (hc : c (lastCheckpoint hn) ≠ none) :
    ∃ s : CircularState n, s.val.origin = some (canonicalOrigin n) ∧
      s.val.chain = decodeChain c (by omega) ∧ RankOnePlacement s.val := by
  obtain ⟨w, q, hq, ho, hchain, _⟩ := realize_clean_code_actual_carrier c (by omega)
  let s : CircularState n := ⟨run {0, 1} (singletonExecution n) w, ⟨w, rfl⟩⟩
  have hfull := (decodedCarrier_full_iff_last c hn).mpr hc
  have hsource := sourceOrdered_fullCarrier _
    (run_ordered (selectedPair n) (singletonExecution n) w (by omega) singletonExecution_ordered)
    q (by simpa only [hfull] using hq)
  have hconst := placementOfMap_fullCarrier (fun _ : ZMod n => q) q (by ext; simp)
  refine ⟨s, ?_, hchain, q, hsource.trans hconst.symm⟩
  rw [registration_origin (by omega)] at ho
  exact ho

abbrev CircularTerminalSparseCode (n j : ℕ) (hn : 3 ≤ n) :=
  {c : Code (n - 2) // (support c).card = j} ⊕
    {c : Code (n - 2) // (support c).card < j ∧ c (lastCheckpoint hn) ≠ none}

noncomputable def circularTerminalSparseEquiv (hn : 3 ≤ n) (j : ℕ) :
    TerminalPrefixCode (n - 2) j ≃ CircularTerminalSparseCode n j hn := by
  have heq : n - 2 - 1 = n - 3 := by omega
  simpa only [PositiveTerminalSparseCode, CircularTerminalSparseCode, lastCheckpoint, heq] using
    positiveTerminalSparseEquiv (n - 2) j (by omega)

def terminalSparseLabel (hn : 3 ≤ n) (j : ℕ) :
    CircularTerminalSparseCode n j hn →
      PrefixLabel (FusionRecord (ZMod n)) (FusionRecord (ZMod n))
  | .inl c => .registered (canonicalOrigin n) (decodeChain c.val (by omega)) .saturated
  | .inr c => .registered (canonicalOrigin n) (decodeChain c.val (by omega)) .short

theorem terminalSparseLabel_injective (hn : 3 ≤ n) (j : ℕ) :
    Function.Injective (terminalSparseLabel hn j) := by
  intro c d h
  cases c <;> cases d
  · congr 1
    apply Subtype.ext
    exact decodeChain_injective (by omega) (PrefixLabel.registered.inj h).2.1
  · cases (PrefixLabel.registered.inj h).2.2
  · cases (PrefixLabel.registered.inj h).2.2
  · congr 1
    apply Subtype.ext
    exact decodeChain_injective (by omega) (PrefixLabel.registered.inj h).2.1

/-- Saturated prefixes ending early are completed by one actual final absorption. -/
theorem terminalSparseLabel_reachable (hn : 3 ≤ n) (j : ℕ) (_hj : 0 < j)
    (c : CircularTerminalSparseCode n j hn) :
    ∃ s : CircularState n, s.val.origin.isSome = true ∧ RankOnePlacement s.val ∧
      circularLabel j s.val = terminalSparseLabel hn j c := by
  cases c with
  | inl c =>
      have hlen : (decodeChain c.val (by omega)).length = j :=
        (decodeChain_length c.val (by omega)).trans c.property
      by_cases hlast : c.val (lastCheckpoint hn) = none
      · obtain ⟨d, rho, hd, hchain⟩ := complete_sparse_prefix c.val hn hlast
        obtain ⟨s, ho, hs, ht⟩ := full_code_reachable hn d hd
        refine ⟨s, by simp [ho], ht, ?_⟩
        simp only [circularLabel, ho, retainedLabel, hs, hchain, List.length_append,
          List.length_singleton, hlen, show ¬j + 1 < j by omega, if_false, terminalSparseLabel]
        rw [List.take_append_of_le_length (by omega), List.take_of_length_le (by omega)]
      · obtain ⟨s, ho, hs, ht⟩ := full_code_reachable hn c.val hlast
        refine ⟨s, by simp [ho], ht, ?_⟩
        simp [circularLabel, ho, retainedLabel, hs, hlen, terminalSparseLabel,
          List.take_of_length_le (show (decodeChain c.val (by omega)).length ≤ j by omega)]
  | inr c =>
      have hlen : (decodeChain c.val (by omega)).length < j := by
        rw [decodeChain_length]; exact c.property.1
      obtain ⟨s, ho, hs, ht⟩ := full_code_reachable hn c.val c.property.2
      refine ⟨s, by simp [ho], ht, ?_⟩
      simp [circularLabel, ho, retainedLabel, hs, hlen, terminalSparseLabel,
        List.take_of_length_le (show (decodeChain c.val (by omega)).length ≤ j by omega)]

theorem terminalSparseLabel_covers (hn : 3 ≤ n) (j : ℕ) (_hj : 0 < j)
    (label : ActualTerminalLabel n j) :
    ∃ c : CircularTerminalSparseCode n j hn, terminalSparseLabel hn j c = label.val := by
  obtain ⟨s, hr, ht, hlabel⟩ := label.property
  obtain ⟨c, hlast, ho, hc⟩ := actual_terminal_code hn s hr ht
  by_cases hshort : (decodeChain c (by omega)).length < j
  · refine ⟨.inr ⟨c, by rw [← decodeChain_length c (by omega)]; exact hshort, hlast⟩, ?_⟩
    rw [← hlabel]
    simp [terminalSparseLabel, circularLabel, ho, retainedLabel, hc, hshort,
      List.take_of_length_le (show (decodeChain c (by omega)).length ≤ j by omega)]
  · obtain ⟨d, hd⟩ := take_decodeChain_in_range c (by omega) j
    have hcard : (support d).card = j := by
      rw [← decodeChain_length d (by omega), hd, List.length_take, Nat.min_eq_left (by omega)]
    refine ⟨.inl ⟨d, hcard⟩, ?_⟩
    rw [← hlabel]
    simp [terminalSparseLabel, circularLabel, ho, retainedLabel, hc, hshort, hd]

noncomputable def terminalSparseActualEquiv (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    CircularTerminalSparseCode n j hn ≃ ActualTerminalLabel n j :=
  Equiv.ofBijective (fun c => ⟨terminalSparseLabel hn j c, terminalSparseLabel_reachable hn j hj c⟩)
    ⟨fun _ _ h => terminalSparseLabel_injective hn j (congrArg Subtype.val h), by
      intro label
      obtain ⟨c, hc⟩ := terminalSparseLabel_covers hn j hj label
      exact ⟨c, Subtype.ext hc⟩⟩

/-- Complete range equivalence: finite terminal parameters ↔ actual attained labels. -/
noncomputable def terminalPrefixActualEquiv (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    TerminalPrefixCode (n - 2) j ≃ ActualTerminalLabel n j :=
  (circularTerminalSparseEquiv hn j).trans (terminalSparseActualEquiv hn j hj)

theorem terminalPrefixActualEquiv_value (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (c : TerminalPrefixCode (n - 2) j) :
    (terminalPrefixActualEquiv hn j hj c).val =
      terminalSparseLabel hn j (circularTerminalSparseEquiv hn j c) := rfl

/-- The forward map includes actual raw-history provenance, not just legality. -/
theorem terminalPrefix_actual_history (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (c : TerminalPrefixCode (n - 2) j) :
    ∃ word : List Letter,
      let s := run {0, 1} (singletonExecution n) word
      s.origin.isSome = true ∧ RankOnePlacement s ∧
        circularLabel j s = (terminalPrefixActualEquiv hn j hj c).val := by
  obtain ⟨s, hr, ht, hl⟩ := (terminalPrefixActualEquiv hn j hj c).property
  obtain ⟨word, hw⟩ := s.property
  exact ⟨word, by simpa only [hw] using And.intro hr (And.intro ht hl)⟩

theorem terminalPrefix_encode_decode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (c : TerminalPrefixCode (n - 2) j) :
    (terminalPrefixActualEquiv hn j hj).symm (terminalPrefixActualEquiv hn j hj c) = c :=
  (terminalPrefixActualEquiv hn j hj).symm_apply_apply c

theorem terminalPrefix_decode_encode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (label : ActualTerminalLabel n j) :
    terminalPrefixActualEquiv hn j hj ((terminalPrefixActualEquiv hn j hj).symm label) = label :=
  (terminalPrefixActualEquiv hn j hj).apply_symm_apply label

theorem finite_actualTerminalLabel (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Finite (ActualTerminalLabel n j) :=
  Finite.of_equiv _ (terminalPrefixActualEquiv hn j hj)

/-- Lemma 3.2 counts actually attained terminal labels, not only parameters. -/
theorem card_actualTerminalLabel (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (ActualTerminalLabel n j) = terminalPrefixCount (n - 2) j := by
  rw [← Nat.card_congr (terminalPrefixActualEquiv hn j hj), Nat.card_eq_fintype_card]
  exact card_terminalPrefixCode (n - 2) j

theorem card_actualTerminalLabel_paper (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (ActualTerminalLabel n j) =
      2 ^ j * (n - 2).choose j +
        ∑ ell ∈ Finset.Icc 1 (j - 1),
          2 ^ ell * (n - 3).choose (ell - 1) := by
  rw [card_actualTerminalLabel hn j hj, terminalPrefixCount_eq_paper]
  have heq : n - 2 - 1 = n - 3 := by omega
  rw [heq]

end Paper44
